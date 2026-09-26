# -*- coding: utf-8 -*-
"""Nubes de palabras del corpus, en Apache ECharts, desde los CSV.

Lee lo que dejo `frecuencias_corpus.py` y dibuja una nube por grupo. NO vuelve
a pasar spaCy: la separacion es deliberada y es la misma que declara el
notebook -- todo se calcula una vez en Python y la pagina recibe numeros ya
agregados, asi que el HTML sigue funcionando sin kernel y las figuras se
regeneran en segundos.

El PESO de cada nube depende del corte:

    corte sin universo (corpus, criterio)   peso = frecuencia de ocurrencias
    corte con universo (grupo, polaridad,   peso = z de log-odds contra el
    criterio_valencia)                              resto de su universo

Un corte que se solapa -- los criterios, donde un tuit puede tocar varios --
no admite uno-contra-resto, y por eso esas nubes van por frecuencia y el panel
lo dice.

    python nubes_corpus.py
    python nubes_corpus.py --forma cardioid
    python nubes_corpus.py --mascara mapa.png --salida salida/nubes.html
"""
import argparse
import base64
import io
import json
import mimetypes
import os

CDN_ECHARTS = "https://cdnjs.cloudflare.com/ajax/libs/echarts/5.6.0/echarts.min.js"
CDN_WORDCLOUD = ("https://cdnjs.cloudflare.com/ajax/libs/"
                 "echarts-wordcloud/2.1.0/echarts-wordcloud.min.js")

# Las que acepta echarts-wordcloud. COMPROBADAS renderizando las ocho con los
# mismos 70 terminos: en un lienzo normal, "pentagon" y "cardioid" apenas se
# distinguen de "circle", y "triangle-forward" de "triangle". Las que de verdad
# se leen como forma son "square", "diamond", "triangle" y "star".
#
# "square" es ademas la que MAS palabras acomoda, porque aprovecha todo el
# rectangulo. Las formas con puntas desperdician area y, con
# drawOutOfBound:false, descartan mas terminos sin decir cuantos.
FORMAS = ("circle", "cardioid", "diamond", "square", "triangle",
          "triangle-forward", "pentagon", "star")

NOMBRE_CATEGORIA = {"ADJ": "adjetivo · evalúa", "NOUN": "sustantivo · tema",
                    "PROPN": "nombre propio · sitúa"}

# Palabras funcion INGLESAS que sobreviven a la traduccion. spaCy analiza en
# espanol, y su lista de palabras vacias no las cubre: el analizador las toma
# por sustantivos o nombres propios y se cuelan entre los mas frecuentes.
# No son contenido, son residuo de una traduccion imperfecta.
#
# Se excluyen SOLO del dibujo. Los CSV las conservan: son el dato, y quitarlas
# de ahi seria perder la evidencia de que la traduccion falla.
VACIAS = {
    "the", "and", "you", "this", "that", "with", "for", "out", "one", "not",
    "are", "was", "were", "have", "has", "but", "from", "they", "his", "her",
    "its", "your", "our", "their", "what", "when", "who", "all", "any", "can",
    "just", "like", "get", "got", "she", "him", "them", "there", "here",
    # interjecciones y onomatopeyas: tampoco dicen nada
    "jaja", "jajaja", "jajajaja", "nah", "ugh", "lol", "omg", "wtf",
}


# Temas. `bandera` usa el verde, el blanco y el rojo sobre negro.
#
# Los tonos NO son los oficiales de la bandera (#006847 y #CE1126): sobre negro
# ese verde y ese rojo quedan por debajo del contraste legible para texto
# pequeno. Se usan las versiones aclaradas, que conservan el color y se leen.
#
# El color sigue codificando la categoria gramatical, no es decoracion:
#   PROPN (situa)   verde     ADJ (evalua)  rojo     NOUN (tema)  blanco
TEMAS = {
    "claro": {
        "css": (":root{ color-scheme: light;\n"
                "    --sup:#fcfcfb; --plano:#f9f9f7; --tinta:#0b0b0b; --tinta2:#52514e;\n"
                "    --mudo:#898781; --grid:#e1e0d9; --borde:rgba(11,11,11,.10);\n"
                "    --aviso-fondo:#fff6e6; --aviso-borde:#f0d9a8; --aviso-tinta:#6a4c00; }"),
        "mezcla_base": 245,
        "categoria": {
            "MX_PAIS": "#c62f2e", "MX_CIUDAD_SEDE": "#eb6834", "MX_DESTINO": "#eda100",
            "MX_ESTADIO": "#b45309", "MX_INSTITUCION": "#4a3aa7",
            "MX_PERSONA_PUBLICA": "#9333ea", "MX_CRIMEN_ORGANIZADO": "#be123c",
            "MX_TORNEO": "#0369a1", "LOC": "#1baf7a", "PER": "#6b7280",
            "ORG": "#52514e", "MISC": "#a8a29e",
            "ADJ": "#c2410c", "NOUN": "#2a78d6", "PROPN": "#0f766e",
        },
        "grupo": {"negativo": "#e34948", "ambivalente": "#eda100", "positivo": "#2a78d6",
                  "calificado": "#eb6834", "no_calificado": "#898781", "_neutro": "#52514e"},
    },
    "bandera": {
        "css": (":root{ color-scheme: dark;\n"
                "    --sup:#141414; --plano:#0a0a0a; --tinta:#f2f2ef; --tinta2:#bdbdb6;\n"
                "    --mudo:#8a8a83; --grid:#2c2c2c; --borde:rgba(242,242,239,.14);\n"
                "    --aviso-fondo:#241d05; --aviso-borde:#5c4a12; --aviso-tinta:#e8cf85; }"),
        "mezcla_base": 10,
        "categoria": {
            "MX_PAIS": "#35c46f", "MX_CIUDAD_SEDE": "#35c46f", "MX_DESTINO": "#7fe0a4",
            "MX_ESTADIO": "#7fe0a4", "MX_INSTITUCION": "#f4f4f2",
            "MX_PERSONA_PUBLICA": "#f4f4f2", "MX_CRIMEN_ORGANIZADO": "#ef4b52",
            "MX_TORNEO": "#f4f4f2", "LOC": "#bdbdb6", "PER": "#8a8a83",
            "ORG": "#8a8a83", "MISC": "#6b6b64",
            "ADJ": "#ef4b52", "NOUN": "#f4f4f2", "PROPN": "#35c46f",
        },
        "grupo": {"negativo": "#ef4b52", "ambivalente": "#f4f4f2", "positivo": "#35c46f",
                  "calificado": "#35c46f", "no_calificado": "#8a8a83", "_neutro": "#f4f4f2"},
    },
}


def color_de(grupo, paleta):
    for clave, valor in paleta.items():
        if clave != "_neutro" and (grupo == clave or grupo.endswith("__" + clave)):
            return valor
    return paleta["_neutro"]


def data_uri(ruta):
    tipo = mimetypes.guess_type(ruta)[0] or "image/png"
    with open(ruta, "rb") as fh:
        return "data:{};base64,{}".format(tipo, base64.b64encode(fh.read()).decode("ascii"))


def proporcion(ruta):
    """ancho/alto de la mascara.

    `maskImage` se ESTIRA al area de dibujo. Con un lienzo ancho y una mascara
    cuadrada, un balon sale como elipse. La pagina usa esto para reducir el
    ancho del area y conservar la figura.
    """
    try:
        from PIL import Image
        with Image.open(ruta) as im:
            return round(im.width / im.height, 4)
    except Exception:
        return 1.0


def preparar(df, grupos, top, soporte, excluidas, paleta):
    """Una entrada por nube con TODOS los terminos que pasan el soporte.

    No se elige aqui la medida ni el recorte: la pagina lleva un selector y
    necesita las tres columnas. Lo que si se fija aqui es el SOPORTE, que no es
    una preferencia de lectura sino el minimo de evidencia para dibujar algo.
    """
    nubes = []
    for _, meta in grupos.iterrows():
        sub = df[(df.corte == meta["corte"]) & (df.grupo == meta["grupo"])]
        hay_z = meta["contraste"] == "z" and not sub.empty and sub["z"].notna().any()
        if sub.empty:
            nubes.append(dict(meta_basica(meta, paleta), terminos=[], hay_z=False))
            continue
        s = sub[(sub.ocurrencias >= soporte) & (~sub.termino.isin(excluidas))]
        # Tope generoso: la pagina recorta al top por la medida elegida, y
        # cada medida ordena distinto.
        s = s.sort_values(["ocurrencias", "termino"], ascending=[False, True]).head(top * 3)
        tiene_cat = "categoria" in s.columns
        terminos = [[r.termino, int(r.ocurrencias), int(r.tuits),
                     (round(float(r.z), 3) if hay_z and r.z == r.z else None),
                     (str(r.categoria) if tiene_cat and isinstance(r.categoria, str) else "")]
                    for r in s.itertuples()]
        nubes.append(dict(meta_basica(meta, paleta), terminos=terminos, hay_z=bool(hay_z)))
    return nubes


def meta_basica(meta, paleta):
    return {"corte": meta["corte"], "grupo": meta["grupo"],
            "n_tuits": int(meta["n_tuits"]), "contraste": meta["contraste"],
            "descripcion": meta["descripcion"], "color": color_de(meta["grupo"], paleta)}


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nubes de palabras del corpus</title>
<script src="__CDN__"></script>
<script src="__CDN_NUBE__"></script>
<style>
__TEMA_CSS__
  *{box-sizing:border-box}
  body{margin:0;background:var(--plano);color:var(--tinta);
       font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
  .wrap{max-width:1180px;margin:0 auto;padding:24px 16px 64px}
  h1{font-size:21px;margin:0 0 4px} h2{font-size:15px;margin:0 0 2px}
  h3{font-size:14px;margin:26px 0 2px}
  .sub{color:var(--tinta2);font-size:13px;margin:0 0 18px}
  .nota{color:var(--mudo);font-size:12px;margin:4px 0 0}
  .panel{background:var(--sup);border:1px solid var(--borde);border-radius:10px;
         padding:14px 16px;margin:0 0 14px}
  .chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 4px}
  .n{border:1px solid var(--grid);border-radius:999px;padding:2px 9px;
     font-size:11px;color:var(--tinta2);font-variant-numeric:tabular-nums}
  .aviso{background:var(--aviso-fondo);border:1px solid var(--aviso-borde);color:var(--aviso-tinta);
         border-radius:8px;padding:9px 12px;margin:8px 0 0;font-size:12.5px}
  .lienzo{width:100%}
  /* UNA sola columna a proposito. Con dos, cada nube se dibuja en un lienzo
     de la mitad de ancho y el mismo valor de z sale con tipografia distinta:
     nubes de geometria distinta no se pueden comparar entre si, que es
     justo para lo que existe esta pagina. */
  .rejilla{display:block}
  .control{position:sticky;top:0;z-index:5;background:var(--sup);
           border:1px solid var(--borde);border-radius:10px;padding:10px 14px;
           margin:0 0 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  .control > span{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--mudo)}
  .chip{border:1px solid var(--grid);background:var(--sup);color:var(--tinta2);
        border-radius:999px;padding:3px 11px;font-size:12px;cursor:pointer}
  /* El texto del chip activo toma el color del FONDO, no un blanco fijo: en
     tema oscuro la tinta es clara y blanco sobre blanco no se lee. */
  .chip[aria-pressed="true"]{background:var(--tinta);border-color:var(--tinta);color:var(--plano)}
  table{border-collapse:collapse;font-size:12px;width:100%;
        font-variant-numeric:tabular-nums;margin-top:8px}
  th,td{text-align:right;padding:3px 7px;border-bottom:1px solid var(--grid)}
  th:first-child,td:first-child{text-align:left}
  details{margin-top:8px} summary{cursor:pointer;font-size:12px;color:var(--tinta2)}
  .fallo{padding:40px;text-align:center;color:var(--tinta2)}
</style>
</head>
<body>
<div class="wrap" id="raiz"></div>
<script>
const D = __DATOS__;
const RAIZ = document.getElementById('raiz');
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const el = h => { const d=document.createElement('div'); d.innerHTML=h.trim(); return d.firstChild; };

/* Dos modos de falla, no uno: si falta solo la extension, el resto de la
   pagina sirve y hay que decir que faltan las nubes, no dejarlas en blanco. */
const HAY_ECHARTS = typeof echarts !== 'undefined';
let HAY_NUBE = false;
if (HAY_ECHARTS) {
  try {
    const d=document.createElement('div');
    d.style.cssText='width:64px;height:64px;position:absolute;left:-9999px;top:0';
    document.body.appendChild(d);
    const ch=echarts.init(d);
    ch.setOption({series:[{type:'wordCloud',data:[{name:'x',value:1}]}]});
    HAY_NUBE = ch.getModel().getSeriesByType('wordCloud').length > 0;
    ch.dispose(); d.remove();
  } catch(e) { HAY_NUBE = false; }
}

RAIZ.appendChild(el('<h1>Nubes de palabras del corpus</h1>'));
RAIZ.appendChild(el('<p class="sub">'+D.ficha.n_tuits+' tuits · lemas y entidades de spaCy sobre la '
  +'<b>traducción automática</b> al español, el único espacio donde un corpus multilingüe es comparable. '
  +'Generado desde <code>'+esc(D.ficha.origen)+'</code>.</p>'));

if (!HAY_ECHARTS) {
  RAIZ.innerHTML = '<div class="fallo"><h1>No se pudo cargar la biblioteca de gráficas</h1>'
    + '<p>Esta página dibuja con Apache ECharts desde <code>__CDN__</code> y la petición no llegó.'
    + ' Los datos están dentro del archivo: recupera la conexión y recarga.</p></div>';
} else if (!HAY_NUBE) {
  RAIZ.appendChild(el('<p class="aviso">No se pudo cargar <code>echarts-wordcloud</code> '
    + 'desde <code>__CDN_NUBE__</code>. Las tablas de cada panel sí traen los datos.</p>'));
}
/* dibujar() se llama AL FINAL del script, no aquí: MODO se declara con let más
   abajo y llamarla antes cae en su zona muerta temporal. */

function tablaDe(n, modo){
  const L = elegir(n, modo);
  const cab = ['término','ocurrencias','tuits'].concat(n.hay_z ? ['z'] : []);
  return '<details><summary>ver los '+L.length+' términos de esta nube</summary>'
    + '<table><tr>'+cab.map(c=>'<th>'+c+'</th>').join('')+'</tr>'
    + L.map(t=>'<tr><td>'+esc(t[0])+'</td><td>'+t[1]+'</td><td>'+t[2]+'</td>'
        +(n.hay_z?'<td>'+(t[3]===null?'—':t[3])+'</td>':'')+'</tr>').join('')
    + '</table></details>';
}

/* MEDIDAS. El tamaño es una elección de lectura, no una propiedad del dato,
   y por eso se elige en la página en vez de congelarse al generarla:
     ocurrencias  cuánto se dice           -> los términos comunes dominan
     tuits        en cuántos tuits se dice  -> una palabra repetida no infla
     z            cuán característico es     -> el ancla se encoge sola          */
const MEDIDAS = {
  ocurrencias: {i:1, rotulo:'ocurrencias'},
  tuits:       {i:2, rotulo:'tuits'},
  z:           {i:3, rotulo:'z de log-odds'},
};
/* Por omision TUITS, no ocurrencias: cuenta en cuantos tuits se dice algo, no
   cuantas veces se tecleo. Un solo tuit que repite una palabra no puede
   inflarla -- "tacos" sale 5 veces pero en 2 tuits --, asi que el ranking es
   mas defendible. */
let MODO = 'tuits';

function elegir(n, modo){
  const m = MEDIDAS[modo] || MEDIDAS.ocurrencias;
  let L = n.terminos.filter(t => t[m.i] !== null && t[m.i] !== undefined);
  /* El soporte se aplica a la MEDIDA ACTIVA, no siempre a las ocurrencias: un
     término con 3 ocurrencias en un solo tuit pasaría un filtro de ocurrencias
     y se dibujaría como si tuviera respaldo, cuando lo dijo una sola persona.
     En modo z el soporte sigue siendo de ocurrencias, porque z no es un
     recuento y su propio umbral es que sea positiva. */
  if (modo === 'z') L = L.filter(t => t[3] > 0 && t[1] >= D.ficha.min_soporte);
  else L = L.filter(t => t[m.i] >= D.ficha.min_soporte);
  return L.sort((a,b) => (b[m.i] - a[m.i]) || (a[0] < b[0] ? -1 : 1)).slice(0, D.ficha.top);
}

function panel(cont, n, modo){
  const L = elegir(n, modo), m = MEDIDAS[modo];
  const s = document.createElement('section');
  s.className = 'panel';
  const chips = ['<span class="n">'+n.n_tuits+' tuits</span>',
                 '<span class="n">'+L.length+' términos</span>',
                 '<span class="n">tamaño: '+esc(m.rotulo)+'</span>'];
  /* Si la figura se encogió hay que decirlo ANTES de construir el HTML: dos
     nubes del mismo ancho aparente pueden tener escalas distintas, y callarlo
     las haría parecer comparables. */
  if (D.ficha.ajustar && L.length) {
    const fa = Math.round(factorArea(n, modo) * 100);
    if (fa < 95) chips.push('<span class="n">figura al '+fa+'% · '+L.length
      + ' de '+NMAX+' términos</span>');
  }
  let h = '<h2>'+esc(n.grupo.replace(/__/g,' · ').replace(/_/g,' '))+'</h2>'
        + '<p class="nota">'+esc(n.descripcion)+'</p>'
        + '<div class="chips">'+chips.join('')+'</div>';
  const avisos = [];
  if (!L.length)
    avisos.push('<b>Omitida.</b> Ningún término alcanza el soporte mínimo ('
      + D.ficha.min_soporte + ' apariciones en el grupo) en estos ' + n.n_tuits + ' tuits.');
  else if (L.length < D.ficha.min_terminos)
    avisos.push('<b>Vocabulario escaso.</b> '+n.n_tuits+' tuits y '+L.length
      + ' términos, por debajo de los '+D.ficha.min_terminos+' declarados: <b>no es comparable</b> con las nubes grandes.');
  if (modo === 'z' && L.length)
    avisos.push('<b>El tamaño no es la valencia.</b> Es cuán <b>característico</b> es el término '
      + 'de este grupo frente al resto de su universo: un término repartido por igual entre los '
      + 'grupos sale pequeño aunque sea el más frecuente aquí.');
  if (modo !== 'z' && L.length && n.hay_z)
    avisos.push('El tamaño es <b>frecuencia</b>: los términos comunes al corpus —«méxico» el primero— '
      + 'pesan por ser comunes, no por ser propios de este grupo. Cambia a <b>z</b> arriba para verlo al revés.');
  if (D.ficha.mascara && L.length)
    avisos.push('<b>Con m\u00e1scara se pierden t\u00e9rminos.</b> Las palabras solo caben en el \u00e1rea '
      + 'opaca de <code>'+esc(D.ficha.mascara_nombre)+'</code>, y las que no entran se descartan '
      + '<b>sin avisar cu\u00e1ntas</b>. Se piden '+L.length+'; cu\u00e1ntas se dibujan no lo dice la biblioteca.');
  if (n.contraste === 'se_solapa')
    avisos.push('Este corte <b>se solapa</b>: un tuit puede estar en varios de sus grupos, '
      + 'así que no admite uno-contra-resto y no tiene z.');
  avisos.forEach(a => h += '<p class="aviso">'+a+'</p>');
  if (L.length) {
    h += '<div class="lienzo" style="height:'+D.ficha.alto+'px"></div>';
    if (D.ficha.color === 'categoria') {
      const cats = [...new Set(L.map(t=>t[4]).filter(Boolean))].sort();
      if (cats.length) h += '<div class="chips">' + cats.map(c =>
        '<span class="n" style="border-color:'+(D.ficha.paleta_categoria[c]||n.color)
        + ';color:'+(D.ficha.paleta_categoria[c]||n.color)+'">'
        + esc(D.ficha.nombre_categoria[c] || c)+'</span>').join('') + '</div>';
    }
  }
  h += tablaDe(n, modo);
  s.innerHTML = h;
  cont.appendChild(s);
  return s.querySelector('.lienzo');
}

/* El area que necesita una nube crece con el numero de terminos, y el lado con
   su RAIZ. Sin esto, una nube de 93 terminos se dibuja en la misma figura que
   una de 1000 y queda perdida en el centro: la letra se ve chica no porque el
   termino sea raro, sino porque sobra lienzo.
   El tamano de letra en px NO cambia -- cambia la figura --, asi que encoger
   el circulo hace que las palabras ocupen mas de el y la diferencia de
   frecuencia se lea mejor. */
let NMAX = 1;
function factorArea(n, modo){
  if (!D.ficha.ajustar) return 1;
  const k = elegir(n, modo).length;
  if (!k || NMAX <= 1) return 1;
  return Math.max(D.ficha.area_minima, Math.sqrt(k / NMAX));
}

function pintar(lienzo, n, modo, mascara){
  if (!lienzo) return;
  if (!HAY_NUBE) { lienzo.innerHTML =
    '<p class="aviso">Sin la extensión de nubes; los términos están en la tabla.</p>'; return; }
  const m = MEDIDAS[modo], L = elegir(n, modo);
  const vals = L.map(t=>t[m.i]);
  const max = Math.max.apply(null, vals), min = Math.min.apply(null, vals);
  const mezcla = (hex, f) => {
    const c = parseInt(hex.slice(1), 16);
    const r = c>>16, g = (c>>8)&255, b = c&255;
    /* Se mezcla hacia el FONDO, no siempre hacia el blanco: sobre negro,
       aclarar los terminos de peso bajo los haria saltar en vez de apagarlos.
       El piso NO baja de 0.55 o dejan de leerse. */
    const B = D.ficha.mezcla_base;
    const q = v => Math.round(B + (v - B) * (0.55 + 0.45 * f));
    return 'rgb('+q(r)+','+q(g)+','+q(b)+')';
  };
  /* La biblioteca mapea `value` a tamaño LINEALMENTE dentro de sizeRange, así
     que la curva se aplica aquí: se normaliza el peso a 0..1 y se eleva al
     exponente. El peso real no se pierde — el tooltip y la tabla siguen
     leyendo las columnas originales.
       curva > 1  amplifica: los grandes crecen y los chicos se achican
       curva = 1  lineal (el tamaño es la altura)
       curva = 0.5 hace el AREA proporcional al peso, no la altura */
  const curvado = v => {
    /* EXPONENCIAL: el tamaño se multiplica por `base` en cada unidad de peso.
       Satura muy pronto -- con base 2 y rango 9..60 px, todo lo que pase de
       ~3 unidades por encima del mínimo sale al máximo --, así que amplifica
       la COLA y aplasta la cabeza. Se ofrece porque es una lectura legítima
       cuando la mayoría de los términos vive en 1..3, pero deja de distinguir
       entre los más frecuentes. */
    if (D.ficha.base > 1) {
      const s = Math.min(D.ficha.tam[1], D.ficha.tam[0] * Math.pow(D.ficha.base, v - min));
      return (s - D.ficha.tam[0]) / (D.ficha.tam[1] - D.ficha.tam[0]);
    }
    const f = max > min ? (v - min) / (max - min) : 1;
    return Math.pow(f, D.ficha.curva);
  };
  const colorDe = t => {
    if (D.ficha.color === 'plano') return n.color;
    if (D.ficha.color === 'categoria') return D.ficha.paleta_categoria[t[4]] || n.color;
    /* El color sigue la MISMA curva que el tamaño: si no, color y tamaño
       contarían historias distintas del mismo número. */
    return mezcla(n.color, curvado(t[m.i]));
  };
  const serie = {
    type:'wordCloud', shape: D.ficha.forma, drawOutOfBound:false,
    gridSize: D.ficha.rejilla, sizeRange: D.ficha.tam,
    /* Determinista: sin rotación y con rejilla fija, la misma entrada da
       siempre la misma figura y la página puede citarse. */
    rotationRange:[0,0], rotationStep:90,
    width: Math.round(96 * factorArea(n, modo)) + '%',
    height: Math.round(92 * factorArea(n, modo)) + '%',
    left:'center', top:'center',
    data: L.map(t=>({name:t[0], value:curvado(t[m.i]),
      textStyle:{color:colorDe(t), fontWeight: t[m.i] >= max*0.6 ? 600 : 400}}))
  };
  if (mascara) {
    serie.maskImage = mascara;
    /* El fondo se alinea con el AREA DE DIBUJO, no con el lienzo: la nube se
       dibuja centrada en un rectangulo de hpx x (hpx*aspecto), y la figura
       tiene que ocupar exactamente ese rectangulo o las palabras caen fuera de
       sus huecos. */
    if (D.ficha.fondo) {
      const hpx0 = Math.round(D.ficha.alto * 0.92 * factorArea(n, modo));
      const wpx0 = Math.round(hpx0 * (D.ficha.mascara_aspecto || 1));
      lienzo.style.backgroundImage = 'url(' + D.ficha.fondo + ')';
      lienzo.style.backgroundRepeat = 'no-repeat';
      lienzo.style.backgroundPosition = 'center';
      lienzo.style.backgroundSize = wpx0 + 'px ' + hpx0 + 'px';
    }
    /* La mascara se estira al area de dibujo. Si el area no tiene su misma
       proporcion la figura sale deformada, asi que se estrecha el area en vez
       de deformar el balon. */
    const fa = factorArea(n, modo);
    const hpx = Math.round(D.ficha.alto * 0.92 * fa);
    serie.height = hpx + 'px';
    serie.width = Math.round(hpx * (D.ficha.mascara_aspecto || 1)) + 'px';
  }
  const ch = echarts.getInstanceByDom(lienzo) || echarts.init(lienzo);
  ch.setOption({
    tooltip:{confine:true, formatter:q=>{
      const t = L.find(x=>x[0]===q.name) || [];
      return '<b>'+esc(q.name)+'</b>'+(t[4]?' · <i>'+esc(t[4])+'</i>':'')
        + '<br>'+t[1]+' ocurrencias en '+t[2]+' tuits'
        + (t[3]===null||t[3]===undefined ? '' : '<br>z = '+t[3]);}},
    series:[serie]}, true);

  /* CUÁNTAS SE DIBUJARON DE VERDAD.
     La biblioteca descarta en silencio las palabras que no caben, así que el
     número de términos que se piden no es el que se ve. Se cuentan los textos
     que zrender llegó a poner en pantalla, cuando termina de dibujar. */
  ch.off('finished');
  ch.on('finished', () => {
    let dibujadas = 0;
    try {
      const zr = ch.getZr();
      const lista = zr.storage.getDisplayList(true) || [];
      /* No se filtra por e.type: echarts-wordcloud no usa el tipo "text".
         Lo que identifica a una palabra dibujada es que traiga texto en su
         estilo. Comprobado contra un conteo a mano sobre la figura. */
      lista.forEach(e => {
        if (e && e.style && e.style.text) dibujadas++;
      });
    } catch (err) { return; }
    const panel = lienzo.closest('.panel');
    if (!panel || !dibujadas) return;
    let chip = panel.querySelector('.n-dibujadas');
    if (!chip) {
      chip = el('<span class="n n-dibujadas"></span>');
      panel.querySelector('.chips').appendChild(chip);
    }
    const perdidas = L.length - dibujadas;
    chip.textContent = dibujadas + ' dibujadas'
      + (perdidas > 0 ? ' · ' + perdidas + ' no caben' : '');
    chip.style.borderColor = perdidas > 0 ? 'var(--aviso-borde)' : '';
    chip.style.color = perdidas > 0 ? 'var(--aviso-tinta)' : '';
  });
}

function dibujar(){
  const hacer = mascara => {
    const render = () => {
      RAIZ.querySelectorAll('.bloque-nubes').forEach(x => x.remove());
      /* Referencia: la nube mas rica de esta pasada. Se recalcula al cambiar de
         medida, porque cada medida deja pasar un numero distinto de terminos. */
      NMAX = Math.max.apply(null, D.nubes.map(x => elegir(x, MODO).length).concat([1]));
      let corteActual = null, cont = null;
      D.nubes.forEach(n => {
        if (n.corte !== corteActual) {
          corteActual = n.corte;
          const b = el('<div class="bloque-nubes"></div>');
          b.appendChild(el('<h3>'+esc(D.titulos[n.corte] || n.corte)+'</h3>'));
          cont = el('<div class="rejilla"></div>');
          b.appendChild(cont); RAIZ.appendChild(b);
        }
        pintar(panel(cont, n, MODO), n, MODO, mascara);
      });
      RAIZ.appendChild(el('<p class="nota bloque-nubes" style="margin-top:22px">'+esc(D.ficha.pie)+'</p>'));
    };
    const hayZ = D.nubes.some(n => n.hay_z);
    const opciones = [['tuits','tuits en que aparece'],['ocurrencias','ocurrencias']]
      .concat(hayZ ? [['z','z de log-odds']] : []);
    const ctl = el('<div class="control"><span>Tamaño de la palabra</span>'
      + opciones.map(o=>'<button class="chip" data-m="'+o[0]+'" aria-pressed="'
        +(o[0]===MODO)+'">'+o[1]+'</button>').join(' ') + '</div>');
    RAIZ.appendChild(ctl);
    ctl.querySelectorAll('button[data-m]').forEach(b => b.onclick = () => {
      MODO = b.dataset.m;
      ctl.querySelectorAll('button[data-m]').forEach(x =>
        x.setAttribute('aria-pressed', String(x.dataset.m === MODO)));
      render();
    });
    render();
  };
  if (D.ficha.mascara) {
    const img = new Image();
    img.onload = () => hacer(img);
    img.onerror = () => { RAIZ.appendChild(el('<p class="aviso">No se pudo leer la máscara; '
      + 'las nubes van con la forma <code>'+esc(D.ficha.forma)+'</code>.</p>')); hacer(null); };
    img.src = D.ficha.mascara;
  } else hacer(null);
}

if (HAY_ECHARTS) dibujar();
</script>
</body>
</html>
"""

TITULOS = {
    "total": "Todo el corpus",
    "grupo": "Grupos de la rúbrica · calificado contra no calificado",
    "polaridad": "Polaridad del tuit · cada grupo contra el resto de los que tienen valencia",
    "criterio": "Por criterio de la rúbrica · presencia, mezclando todos los niveles",
    "criterio_valencia": "Criterio × valencia · el nivel dentro de cada criterio",
}

PIE = ("Las nubes de frecuencia describen un universo: el tamaño es cuántas veces aparece el "
       "término. Las de z comparan un grupo contra el resto de su universo con log-odds con prior "
       "informativo (Monroe, Colaresi y Quinn, 2008), y ahí el tamaño NO es la valencia sino cuán "
       "característico es el término de su grupo. "
       "No se concluye nada de los grupos chicos: son descriptivos de una rúbrica aplicada por un "
       "modelo de lenguaje, no por codificadores humanos.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", default="salida")
    ap.add_argument("--tipo", choices=("lemas", "entidades"), default="lemas")
    ap.add_argument("--salida", default=None)
    ap.add_argument("--forma", choices=FORMAS, default="circle")
    ap.add_argument("--mascara", default=None,
                    help="imagen cuya zona opaca se rellena; se embebe en el HTML")
    ap.add_argument("--fondo", default=None,
                    help="imagen que se DIBUJA detras de las palabras, alineada "
                         "con la mascara. Con ella la figura se ve; sin ella hay "
                         "que adivinarla por los huecos")
    ap.add_argument("--top", type=int, default=80,
                help="terminos como maximo por nube; por encima de ~90 se encima el texto")
    ap.add_argument("--soporte", type=int, default=3,
                    help="apariciones minimas del termino dentro de su grupo")
    ap.add_argument("--color", choices=("auto", "intensidad", "categoria", "plano"),
                    default="auto",
                    help="auto = categoria en entidades, intensidad en lemas. "
                         "`plano` deja un solo color por grupo")
    ap.add_argument("--tam", type=int, nargs=2, metavar=("MIN", "MAX"), default=[11, 44],
                    help="tamano de letra en px del termino mas chico y del mas grande")
    ap.add_argument("--curva", type=float, default=1.0,
                    help="exponente sobre el peso normalizado. 1 = lineal; "
                         ">1 amplifica la diferencia; 0.5 hace el AREA proporcional "
                         "al peso en vez de la altura")
    ap.add_argument("--sin-vacias", dest="sin_vacias", action="store_true", default=True,
                    help="excluye del DIBUJO las palabras funcion inglesas que "
                         "sobreviven a la traduccion (por omision, si)")
    ap.add_argument("--con-vacias", dest="sin_vacias", action="store_false",
                    help="las dibuja: util para auditar la traduccion")
    ap.add_argument("--base", type=float, default=0.0,
                    help="si es > 1, el tamano se MULTIPLICA por esta base en cada "
                         "unidad de peso (2 = duplica por ocurrencia). Satura pronto "
                         "y aplasta la cabeza de la distribucion; anula --curva")
    ap.add_argument("--tema", choices=tuple(TEMAS), default="claro",
                    help="`bandera` dibuja verde, blanco y rojo sobre negro")
    ap.add_argument("--ajustar-area", dest="ajustar", action="store_true", default=True,
                    help="encoge la figura de las nubes con pocos terminos, para que "
                         "la letra se vea grande en vez de perderse en un lienzo vacio "
                         "(por omision, si)")
    ap.add_argument("--area-fija", dest="ajustar", action="store_false",
                    help="misma figura para todas, aunque las chicas queden vacias")
    ap.add_argument("--area-minima", type=float, default=0.55,
                    help="fraccion minima del diametro a la que puede encoger una nube. "
                         "MEDIDO: con 0.38 la nube de 93 terminos perdia 35 por falta de "
                         "sitio; con 0.55 caben las 93 y la figura sigue siendo la mitad "
                         "de grande que la mayor, asi que la letra se sigue viendo grande")
    ap.add_argument("--alto", type=int, default=460)
    ap.add_argument("--rejilla", type=int, default=14,
                help="separacion entre palabras; mas alto = mas aire")
    args = ap.parse_args()

    import pandas as pd
    origen = os.path.join(args.datos, "frecuencias_{}.csv".format(args.tipo))
    ruta_grupos = os.path.join(args.datos, "frecuencias_grupos.csv")
    for ruta in (origen, ruta_grupos):
        if not os.path.exists(ruta):
            raise SystemExit("No existe {}. Corre antes frecuencias_corpus.py".format(ruta))

    df = pd.read_csv(origen, encoding="utf-8-sig")
    grupos = pd.read_csv(ruta_grupos, encoding="utf-8-sig")
    tema = TEMAS[args.tema]
    excluidas = VACIAS if args.sin_vacias else set()
    modo_color = args.color
    if modo_color == "auto":
        modo_color = "categoria"   # hay categoria real en los dos: POS en lemas
    nubes = preparar(df, grupos, args.top, args.soporte, excluidas, tema["grupo"])

    mascara = data_uri(args.mascara) if args.mascara else None
    if args.mascara and not os.path.exists(args.mascara):
        raise SystemExit("No existe la mascara {}".format(args.mascara))
    if args.fondo and not os.path.exists(args.fondo):
        raise SystemExit("No existe el fondo {}".format(args.fondo))
    if args.fondo and not args.mascara:
        raise SystemExit("--fondo sin --mascara dibujaria la figura con las "
                         "palabras encima, tapandola. Usa las dos.")

    datos = {
        "nubes": nubes, "titulos": TITULOS,
        "ficha": {"n_tuits": int(grupos.loc[grupos.corte == "total", "n_tuits"].iloc[0]),
                  "origen": origen, "forma": args.forma, "mascara": mascara,
                  "mascara_aspecto": proporcion(args.mascara) if args.mascara else None,
                  "mascara_nombre": args.mascara or "",
                  "fondo": data_uri(args.fondo) if args.fondo else None,
                  "alto": args.alto, "rejilla": args.rejilla,
                  "min_soporte": args.soporte, "min_terminos": 25, "pie": PIE, "top": args.top,
                  "tam": args.tam, "curva": args.curva, "base": args.base,
                  "mezcla_base": tema["mezcla_base"], "tema": args.tema,
                  "ajustar": bool(args.ajustar), "area_minima": args.area_minima,
                  "color": modo_color, "paleta_categoria": tema["categoria"],
                  "nombre_categoria": NOMBRE_CATEGORIA},
    }
    pagina = (PLANTILLA.replace("__TEMA_CSS__", "  " + tema["css"])
              .replace("__CDN_NUBE__", CDN_WORDCLOUD)
              .replace("__CDN__", CDN_ECHARTS)
              .replace("__DATOS__", json.dumps(datos, ensure_ascii=False)))

    salida = args.salida or os.path.join(args.datos, "nubes_{}.html".format(args.tipo))
    with io.open(salida, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(pagina)

    print("=" * 74)
    print("NUBES · {}  ({:.0f} KB)".format(salida, len(pagina.encode("utf-8")) / 1024))
    print("=" * 74)
    print("  forma: {}{}".format(args.forma, "  ·  máscara: " + args.mascara if args.mascara else ""))
    if excluidas:
        _fuera = sorted(set(df.termino) & excluidas)
        print("  excluidas del dibujo ({}): {}".format(len(_fuera), ", ".join(_fuera) or "ninguna"))
    print()
    print("  {:<18} {:<30} {:>6} {:>9} {:>7}".format(
        "corte", "grupo", "tuits", "terminos", "con z"))
    print("  " + "-" * 76)
    for n in nubes:
        marca = ""
        if not n["terminos"]:
            marca = "   OMITIDA"
        elif len(n["terminos"]) < 25:
            marca = "   escasa"
        print("  {:<18} {:<30} {:>6} {:>9} {:>7}{}".format(
            n["corte"], n["grupo"], n["n_tuits"], len(n["terminos"]),
            "si" if n["hay_z"] else "no", marca))
    print()
    print("  El TAMANO de la palabra se elige en la pagina: ocurrencias (por omision),")
    print("  tuits en que aparece, o z de log-odds donde el corte lo admite.")
    print("=" * 74)


if __name__ == "__main__":
    main()
