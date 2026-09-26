# -*- coding: utf-8 -*-
"""Agrega botones de descarga PNG y SVG a una pagina de figuras ya generada.

Trabaja sobre el HTML terminado, sin tocar el notebook que lo produjo: inyecta
un <script> antes de </body> que recorre las graficas de ECharts que haya en la
pagina y le pone a cada una sus dos botones.

Que se recorra el DOM y no se toque el codigo de la pagina es lo que hace que
esto sirva igual para `figuras_v3.html`, para una version futura o para una
pagina con otra cantidad de figuras: el parche no sabe cuantas hay ni como se
construyeron.

El original se respalda con sufijo `.orig.html` la primera vez.

    python agregar_descargas.py ruta/figuras_v3.html
    python agregar_descargas.py fig.html --salida fig_descargable.html
"""
import argparse
import io
import os
import shutil

MARCA = "<!-- descargas-png-svg -->"

PARCHE = MARCA + r"""
<style>
  .descargas{display:inline-flex;gap:6px;margin:0 0 0 10px;vertical-align:middle}
  .descargas button{border:1px solid #e1e0d9;background:#fcfcfb;color:#52514e;
    border-radius:999px;padding:2px 10px;font:inherit;font-size:11px;
    letter-spacing:.04em;cursor:pointer;line-height:1.5}
  .descargas button:hover{border-color:#52514e;color:#0b0b0b}
</style>
<script>
(function(){
  if (typeof echarts === 'undefined') return;

  /* 3x sobre el tamano en pantalla: una figura de ~1000 px de ancho sale de
     ~3000 y aguanta impresion. El PNG se usa donde no entra un vectorial
     (Word viejo, PowerPoint, una vista previa); el SVG es el que conviene para
     la tesis impresa, porque no se pixelea a ninguna escala. */
  var PIXELES = 3;
  var FONDO = '#fcfcfb';

  function slug(t) {
    return String(t || '').toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 60) || 'figura';
  }

  function bajar(href, nombre) {
    var a = document.createElement('a');
    a.href = href; a.download = nombre;
    document.body.appendChild(a); a.click(); a.remove();
  }

  /* El SVG de ECharts sale SIN fondo. Pegado en un documento con fondo blanco
     no se nota, pero sobre cualquier otro color las etiquetas grises quedan
     ilegibles, asi que se le antepone un rectangulo del color de la pagina.

     Y se apaga el `toolbox` mientras se exporta: varias figuras de esta pagina
     llevan el boton de guardado propio de ECharts arriba a la derecha, y sin
     apagarlo el icono queda horneado dentro de la imagen descargada. Se vuelve
     a encender en el `finally`, para que un fallo no deje la pagina sin el. */
  function svgDe(inst) {
    var op = inst.getOption();
    var hayCaja = !!(op.toolbox && op.toolbox.length && op.toolbox[0].show !== false);
    if (hayCaja) inst.setOption({toolbox: {show: false}});
    try {
      var s = inst.renderToSVGString ? inst.renderToSVGString()
            : decodeURIComponent(inst.getDataURL({type: 'svg'}).split(',')[1]);
      return s.replace(/(<svg[^>]*>)/,
        '$1<rect x="0" y="0" width="100%" height="100%" fill="' + FONDO + '"/>');
    } finally {
      if (hayCaja) inst.setOption({toolbox: {show: true}});
    }
  }

  function comoSVG(inst, nombre) {
    bajar('data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgDe(inst)),
          nombre + '.svg');
  }

  /* Esta pagina dibuja con el renderizador SVG, asi que `getDataURL` devolveria
     un SVG aunque se le pida PNG. El PNG se arma aparte: se carga el SVG como
     imagen y se pinta en un lienzo a 3x.
     El SVG va como `data:` y no como `blob:` a proposito -- con la pagina
     abierta desde file://, un blob puede manchar el lienzo y `toDataURL` falla
     con un error de seguridad. */
  function comoPNG(inst, nombre) {
    var im = new Image();
    im.onload = function () {
      var cv = document.createElement('canvas');
      cv.width = (im.width || inst.getWidth()) * PIXELES;
      cv.height = (im.height || inst.getHeight()) * PIXELES;
      var cx = cv.getContext('2d');
      cx.fillStyle = FONDO;
      cx.fillRect(0, 0, cv.width, cv.height);
      cx.drawImage(im, 0, 0, cv.width, cv.height);
      try { bajar(cv.toDataURL('image/png'), nombre + '.png'); }
      catch (e) { alert('El navegador no dejó convertir esta figura a PNG. ' +
                        'El SVG sí funciona y no pierde calidad.'); }
    };
    im.onerror = function () {
      alert('No se pudo convertir esta figura a PNG. El SVG sí funciona.');
    };
    im.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgDe(inst));
  }

  function titulo(nodo) {
    var sec = nodo.closest('.fig, section, figure') || nodo.parentNode;
    var h = sec.querySelector('h3, h2, h1');
    return h ? h.textContent : '';
  }

  /* Se buscan las graficas por el atributo que ECharts le pone a su contenedor,
     no por una clase de esta pagina: asi el parche no depende de como se
     llamen los divs. */
  function recorrer() {
    document.querySelectorAll('[_echarts_instance_]').forEach(function (nodo) {
      if (nodo.dataset.conDescargas) return;
      var inst = echarts.getInstanceByDom(nodo);
      if (!inst) return;
      nodo.dataset.conDescargas = '1';

      var nombre = slug(titulo(nodo));
      var caja = document.createElement('span');
      caja.className = 'descargas';
      caja.innerHTML = '<button type="button" data-f="png">PNG</button>'
                     + '<button type="button" data-f="svg">SVG</button>';
      caja.addEventListener('click', function (ev) {
        var b = ev.target.closest('button');
        if (!b) return;
        if (b.dataset.f === 'svg') comoSVG(inst, nombre); else comoPNG(inst, nombre);
      });

      var sec = nodo.closest('.fig, section, figure') || nodo.parentNode;
      var h = sec.querySelector('h3, h2, h1');
      if (h) h.appendChild(caja); else nodo.parentNode.insertBefore(caja, nodo);
    });
  }

  /* Dos pasadas y una mas despues de cada clic: varias figuras de esta pagina
     no existen al cargar -- las crean los controles de su panel -- y una sola
     pasada las dejaria sin botones. */
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', recorrer);
  else recorrer();
  addEventListener('load', recorrer);
  document.addEventListener('click', function () { setTimeout(recorrer, 400); });
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("--salida", default=None,
                    help="por omision se reescribe la misma ruta, con respaldo")
    args = ap.parse_args()

    if not os.path.exists(args.entrada):
        raise SystemExit("no encuentro {}".format(args.entrada))

    with io.open(args.entrada, encoding="utf-8") as fh:
        pagina = fh.read()

    if MARCA in pagina:
        raise SystemExit("esa pagina ya tiene los botones de descarga")
    if "</body>" not in pagina:
        raise SystemExit("la pagina no tiene </body>: no se donde inyectar")

    salida = args.salida or args.entrada
    if salida == args.entrada:
        respaldo = os.path.splitext(args.entrada)[0] + ".orig.html"
        if not os.path.exists(respaldo):
            shutil.copy2(args.entrada, respaldo)
            print("respaldo   : {}".format(respaldo))

    # Antes del ULTIMO </body>, no del primero: si alguna figura trae HTML
    # incrustado con esa etiqueta, el parche quedaria a media pagina.
    corte = pagina.rfind("</body>")
    nueva = pagina[:corte] + PARCHE + "\n" + pagina[corte:]

    with io.open(salida, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(nueva)
    print("DESCARGAS  : {}  ({:.0f} KB)".format(salida, len(nueva.encode("utf-8")) / 1024))


if __name__ == "__main__":
    main()
