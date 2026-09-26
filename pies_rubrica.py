# -*- coding: utf-8 -*-
"""Graficas de pastel de la cobertura y de los niveles de la rubrica, en ECharts.

Cuatro pasteles sobre `tweets_calificados_anclada.csv`:

    1. cobertura      el corpus entero contra la rebanada que la rubrica califico
    2. atmosfera      los calificados de ese criterio, repartidos por nivel 1-5
    3. perspectiva politica   lo mismo
    4. imagen cultural        lo mismo

Todas las rebanadas llevan la FRECUENCIA escrita encima, no solo el porcentaje:
con 4 tuits en un nivel y 35 en otro, el porcentaje solo miente sobre cuanta
evidencia hay detras.

Las reglas de lectura de la rubrica son las del notebook (celda 6), no unas
nuevas: BLOQUEADO es dato faltante y nunca ausencia, el nivel 0 y `aplicable=NO`
son la MISMA clase (ausencia), y un tuit esta "calificado" si algun criterio
quedo en nivel > 0. Reimplementarlas aqui de otra forma haria que esta pagina
contara distinto que el resto del trabajo.

    python pies_rubrica.py
    python pies_rubrica.py --tema oscuro
    python pies_rubrica.py --paleta proyecto --salida salida/pies.html
    python pies_rubrica.py --indicadores tres
"""
import argparse
import io
import json
import os

import pandas as pd

CDN_ECHARTS = "https://cdnjs.cloudflare.com/ajax/libs/echarts/5.6.0/echarts.min.js"

RUTA_ENTRADA = "tweets_calificados_anclada.csv"

# Los tres criterios de VALENCIA, en el orden en que se piden. La saliencia de
# violencia queda fuera a proposito: su escala es de PRESENCIA, no de valencia
# --un tuit que menciona violencia no es un tuit negativo-- y un pastel "por
# nivel de sentimiento" de un criterio que no mide sentimiento seria falso.
# Su cuenta aparece igual en la ficha, para que la exclusion sea visible.
CRITERIOS = [
    {"prefijo": "rubrica_1_atmosfera_de_mexic", "corto": "atmosfera",
     "etiqueta": "Atmósfera de México",
     "nombre": "ATMÓSFERA DE MÉXICO: DIMENSIÓN SIMPÁTICA / EMOCIONAL"},
    {"prefijo": "rubrica_3_perspectiva_politi", "corto": "perspectiva_politica",
     "etiqueta": "Perspectiva política",
     "nombre": "PERSPECTIVA POLÍTICA DE MÉXICO: DIMENSIÓN FUNCIONAL"},
    {"prefijo": "rubrica_2_imagen_cultural_de", "corto": "imagen_cultural",
     "etiqueta": "Imagen cultural",
     "nombre": "IMAGEN CULTURAL DE MÉXICO: DIMENSIÓN ESTÉTICA"},
]

CRITERIO_PRESENCIA = "rubrica_4_saliencia_de_viole"

# Anclas de la escala, en las palabras de la rubrica: el 1 es odio, desprecio o
# juicio fuertemente negativo, el 3 es ambivalencia declarada y el 5 es
# fascinacion o elogio superlativo.
#
# La ETIQUETA nombra la valencia en vez de citar el ancla ("odio o desprecio",
# "fascinacion o elogio"): el ancla es la instruccion que recibio el modelo, no
# lo que el lector necesita para interpretar una rebanada. La cita textual sigue
# al pie de la pagina, que es donde explica que significan los polos.
#
# Las cinco son SIMETRICAS -- muy negativo / negativo / ambivalente / positivo /
# muy positivo -- por dos razones. Una escala con signo que se rotula
# "muy negativo, negativo moderado, ..., positivo, muy positivo" sugiere que el
# 2 y el 4 no son el mismo escalon en lados opuestos, y si lo son. Y en un
# pastel las etiquetas van fuera: "negativo moderado" no cabia en el panel de
# atmosfera y ECharts lo recortaba a "negativo moder...".
NIVELES = [
    (1, "1 · muy negativo"),
    (2, "2 · negativo"),
    (3, "3 · ambivalente o mixto"),
    (4, "4 · positivo"),
    (5, "5 · muy positivo"),
]

# Paleta de valencia. DIVERGENTE por construccion: dos polos de hue opuesto con
# un gris neutro en el 3, que es justo lo que pide una escala con signo.
#
#   proyecto   la de EvaluadorTweets (viz.py) tal cual, para que esta pagina se
#              lea igual que las figuras de las secciones 2, 14 y 15
#   accesible  identica salvo el nivel 1, oscurecido de #c62f2e a #a81f1e
#
# El motivo del cambio es medible, no de gusto: con #c62f2e el par 1-2 queda a
# 14.9 de distancia perceptual (OKLab x100) y en un PASTEL esas dos rebanadas
# son contiguas, sin nada que las separe salvo el color. En las barras de la
# seccion 2 el problema no existe porque ahi las separa la posicion. Oscurecer
# el polo lo sube a 16.2 y ademas es mas fiel a la escala: el extremo se ve
# como extremo. Por omision se usa `accesible`; `--paleta proyecto` vuelve a la
# original si lo que importa es el calco exacto de las otras figuras.
PALETAS_VALENCIA = {
    "proyecto":  ["#c62f2e", "#e8716f", "#c3c2b7", "#6da7ec", "#1c5cab"],
    "accesible": ["#a81f1e", "#e8716f", "#c3c2b7", "#6da7ec", "#1c5cab"],
}

TEMAS = {
    "claro": {
        "css": (":root{ color-scheme: light;\n"
                "    --sup:#fcfcfb; --plano:#f9f9f7; --tinta:#0b0b0b; --tinta2:#52514e;\n"
                "    --mudo:#898781; --grid:#e1e0d9; --borde:rgba(11,11,11,.10);\n"
                "    --aviso-fondo:#fff6e6; --aviso-borde:#f0d9a8; --aviso-tinta:#6a4c00; }"),
        # El borde de cada rebanada es del color de la SUPERFICIE, no una linea
        # gris: asi separa sin dibujar un contorno que compita con el dato.
        "superficie": "#fcfcfb",
        "calificado": "#eb6834", "no_calificado": "#898781",
    },
    "oscuro": {
        "css": (":root{ color-scheme: dark;\n"
                "    --sup:#141414; --plano:#0a0a0a; --tinta:#f2f2ef; --tinta2:#bdbdb6;\n"
                "    --mudo:#8a8a83; --grid:#2c2c2c; --borde:rgba(242,242,239,.14);\n"
                "    --aviso-fondo:#241d05; --aviso-borde:#5c4a12; --aviso-tinta:#e8cf85; }"),
        "superficie": "#141414",
        "calificado": "#eb6834", "no_calificado": "#8a8a83",
    },
}


def leer(ruta):
    """El CSV con los tipos que hacen falta y nada mas."""
    df = pd.read_csv(ruta, low_memory=False)
    for c in df.columns:
        if c.endswith("_nivel"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def contar_criterio(df, prefijo):
    """Frecuencias por nivel de un criterio, mas lo que queda fuera del pastel.

    `presente` son los tuits con nivel > 0: los unicos que el pastel dibuja.
    `ausencia` (nivel 0 o aplicable NO) y `faltante` (BLOQUEADO por el
    proveedor) NO son rebanadas -- son el universo del que se recorto -- y se
    devuelven aparte para que la ficha los declare en vez de esconderlos.
    """
    niv = df[prefijo + "_nivel"]
    apl = df[prefijo + "_aplicable"].astype("string").str.strip().str.upper()

    frecuencias = [int((niv == n).sum()) for n, _ in NIVELES]
    return {
        "frecuencias": frecuencias,
        "presente": int(sum(frecuencias)),
        "nivel_cero": int((niv == 0).sum()),
        "ausencia": int(((niv == 0) | ((apl == "NO") & niv.isna())).sum()),
        "faltante": int((apl == "BLOQUEADO").sum()),
    }


def construir(df, tema, paleta_valencia, indicadores):
    # Un tuit "tiene contenido" sobre un indicador cuando ese criterio quedo en
    # nivel > 0. Es la definicion del notebook; contar en cambio los
    # `aplicable = SI` daria 175, porque incluye los que el motor marco
    # aplicables y luego puntuo en 0.
    #
    # CUALES indicadores entran cambia el numero, y por eso es una opcion:
    #
    #   tres    los de VALENCIA -- atmosfera, perspectiva politica, imagen
    #           cultural -- que son los que tienen pastel de niveles.  140 tuits.
    #   cuatro  ademas la saliencia de violencia.                      144 tuits.
    #
    # Los 4 de diferencia son tuits que SOLO mencionan violencia y no dicen nada
    # sobre los otros tres. La pagina los nombra en la nota en vez de dejarlos
    # dentro de una rebanada que no los describe.
    columnas_tres = [c["prefijo"] + "_nivel" for c in CRITERIOS]
    columnas_nivel = [c for c in df.columns if c.endswith("_nivel")]

    con_tres = (df[columnas_tres] > 0).any(axis=1)
    con_cuatro = (df[columnas_nivel] > 0).any(axis=1)
    calificado = con_tres if indicadores == "tres" else con_cuatro

    n_total = int(len(df))
    n_calificado = int(calificado.sum())
    n_solo_violencia = int((con_cuatro & ~con_tres).sum())

    # Los turistas se cuentan por `author_username`, NO por `author_id`: la hoja
    # de calculo por la que paso el archivo convirtio parte de los id numericos
    # a notacion cientifica ("1.12E+18"), asi que el mismo autor aparece con dos
    # id distintos y contar por id inflaria el numero de personas.
    turistas_total = int(df["author_username"].nunique())
    turistas_calificado = int(df.loc[calificado, "author_username"].nunique())

    criterios = []
    for crit in CRITERIOS:
        cuenta = contar_criterio(df, crit["prefijo"])
        criterios.append({
            "corto": crit["corto"], "etiqueta": crit["etiqueta"],
            "nombre": crit["nombre"],
            "niveles": [{"nivel": n, "etiqueta": et, "n": f}
                        for (n, et), f in zip(NIVELES, cuenta["frecuencias"])],
            "presente": cuenta["presente"],
            "ausencia": cuenta["ausencia"],
            "faltante": cuenta["faltante"],
            "nivel_cero": cuenta["nivel_cero"],
        })

    violencia = contar_criterio(df, CRITERIO_PRESENCIA)

    # En minuscula y con "o", porque va DENTRO de una frase, no como titulo.
    lista = ("atmósfera, perspectiva política o imagen cultural" if indicadores == "tres"
             else "atmósfera, perspectiva política, imagen cultural o violencia")

    return {
        "ficha": {
            "origen": os.path.basename(RUTA_ENTRADA),
            "n_total": n_total,
            "n_calificado": n_calificado,
            "n_no_calificado": n_total - n_calificado,
            "turistas_total": turistas_total,
            "turistas_calificado": turistas_calificado,
            "violencia_presente": violencia["presente"],
            "indicadores": indicadores,
            "n_solo_violencia": n_solo_violencia,
            "lista_indicadores": lista,
            "etiqueta_con": "con calificación en " + lista,
            "etiqueta_sin": "sin calificación en ninguno de esos indicadores",
        },
        "criterios": criterios,
        "paleta_valencia": paleta_valencia,
        "color_calificado": tema["calificado"],
        "color_no_calificado": tema["no_calificado"],
        "superficie": tema["superficie"],
    }


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cobertura y niveles de la rúbrica</title>
<script src="__CDN__"></script>
<style>
__TEMA_CSS__
  *{box-sizing:border-box}
  body{margin:0;background:var(--plano);color:var(--tinta);
       font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
  .wrap{max-width:1180px;margin:0 auto;padding:24px 16px 64px}
  h1{font-size:21px;margin:0 0 4px} h2{font-size:15px;margin:0 0 2px}
  .sub{color:var(--tinta2);font-size:13px;margin:0 0 18px}
  .nota{color:var(--mudo);font-size:12px;margin:6px 0 0}
  .panel{background:var(--sup);border:1px solid var(--borde);border-radius:10px;
         padding:14px 16px;margin:0 0 14px}
  .chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 4px}
  .n{border:1px solid var(--grid);border-radius:999px;padding:2px 9px;
     font-size:11px;color:var(--tinta2);font-variant-numeric:tabular-nums}
  .aviso{background:var(--aviso-fondo);border:1px solid var(--aviso-borde);color:var(--aviso-tinta);
         border-radius:8px;padding:9px 12px;margin:8px 0 0;font-size:12.5px}
  .lienzo{width:100%}
  /* Los tres criterios en rejilla: son el MISMO pastel sobre universos
     distintos y se leen comparandolos. La cobertura va sola y a lo ancho
     porque no compara con nadie.
     DOS columnas, no tres: con tres, el lienzo baja de 360 px de ancho y
     ECharts recorta las etiquetas de fuera a "5 · fa...". Una etiqueta
     truncada no dice el nivel, que es justo lo que el pastel reparte. */
  .rejilla{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:14px}
  table{border-collapse:collapse;font-size:12px;width:100%;
        font-variant-numeric:tabular-nums;margin-top:8px}
  th,td{text-align:right;padding:3px 7px;border-bottom:1px solid var(--grid)}
  th:first-child,td:first-child{text-align:left}
  .punto{display:inline-block;width:9px;height:9px;border-radius:2px;
         margin-right:6px;vertical-align:-1px}
  details{margin-top:8px} summary{cursor:pointer;font-size:12px;color:var(--tinta2)}
  /* El boton de descarga vive en el encabezado de su panel, no en una barra
     aparte: asi no hay que averiguar cual de los cuatro PNG se va a bajar. */
  h2{display:flex;align-items:baseline;justify-content:space-between;gap:12px}
  .png{border:1px solid var(--grid);background:var(--sup);color:var(--tinta2);
       border-radius:999px;padding:3px 11px;font-size:11px;cursor:pointer;
       font-family:inherit;letter-spacing:.04em;white-space:nowrap}
  .png:hover{border-color:var(--tinta2);color:var(--tinta)}
  .barra{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:0 0 16px}
  /* Los tres paneles de criterio comparten layout exacto. Las dos piezas de
     alto variable se reservan para que las donas queden a la misma altura y el
     "Ver los números" alinee entre paneles:
       .sub-criterio  el nombre largo del criterio, que en pantallas estrechas
                      pasa de uno a dos renglones segun el criterio
       .aviso-reservado  el aviso, que no todos los criterios tienen */
  .rejilla .sub-criterio{margin:0 0 6px;font-size:12px;min-height:2.9em}
  .aviso-reservado{min-height:1.55em}
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
const mil = n => n.toLocaleString('es-MX');
const pct = (n,t) => t ? (100*n/t).toFixed(1).replace('.',',') + ' %' : '—';

RAIZ.appendChild(el('<h1>Cobertura de la rúbrica y niveles por criterio</h1>'));
RAIZ.appendChild(el('<p class="sub">'+mil(D.ficha.n_total)+' tuits de '+D.ficha.turistas_total
  +' turistas. Calificado por <code>'+esc(D.ficha.origen)+'</code>; cada rebanada lleva su '
  +'<b>frecuencia</b> y su porcentaje.</p>'));

if (typeof echarts === 'undefined') {
  RAIZ.innerHTML = '<div class="fallo"><h1>No se pudo cargar la biblioteca de gráficas</h1>'
    + '<p>Esta página dibuja con Apache ECharts desde <code>__CDN__</code> y la petición no llegó.'
    + ' Los datos están dentro del archivo: recupera la conexión y recarga.</p></div>';
} else {
  dibujar();
}

/* Reparte una etiqueta en renglones, sin cortar palabras. */
function envolver(texto, ancho) {
  const lineas = [''];
  String(texto).split(' ').forEach(p => {
    const i = lineas.length - 1;
    if (!lineas[i]) { lineas[i] = p; }
    else if ((lineas[i] + ' ' + p).length <= ancho) { lineas[i] += ' ' + p; }
    else { lineas.push(p); }
  });
  return lineas;
}

/* Una etiqueta de rebanada, en UNO o DOS renglones, nunca tres.

   Hace falta porque las etiquetas van FUERA de la rebanada: la de cobertura
   mide 79 caracteres ("con calificacion en atmosfera, perspectiva politica,
   imagen cultural o violencia") y en un solo renglon se sale del lienzo o
   ECharts la recorta con puntos suspensivos.

   Dos decisiones:

   - Lo que cabe en UN renglon no se parte. Las etiquetas de nivel miden 22
     caracteres o menos y forzarlas a dos daria "3 · ambivalente / o mixto",
     peor que dejarlas enteras.
   - Lo que no cabe se parte con el ancho MINIMO que logra dos renglones, no con
     un ancho fijo. Un ancho fijo de 38 parte la de cobertura en tres
     (29 + 37 + 11); buscando el minimo salen dos parejos (41 + 37). El ancho
     mas chico que cabe en dos es, por construccion, el mas equilibrado.

   El corte es por palabras y no con `overflow:'break'` de ECharts, que parte a
   media palabra.

   Todo vive DENTRO de la funcion y no en `const` de modulo: `dibujar()` se
   llama mas arriba, y un `const` de modulo declarado aqui sigue en su zona
   muerta temporal cuando ECharts evalua el formateador. La serie se caia entera
   y quedaba el pastel en blanco con la leyenda ya dibujada. */
function partir(texto) {
  const UN_RENGLON = 38;
  const t = String(texto);
  if (t.length <= UN_RENGLON) return [t];
  for (let ancho = Math.ceil(t.length / 2); ancho <= t.length; ancho++) {
    const lineas = envolver(t, ancho);
    if (lineas.length <= 2) return lineas;
  }
  return [t];
}

/* Un pastel, con la frecuencia SIEMPRE escrita fuera de la rebanada.
   Fuera y no dentro: los niveles de 4 y 9 tuits dan rebanadas de menos de un
   grado y una etiqueta dentro no cabria; con las cinco fuera, todas se leen
   igual y ninguna queda a merced de su tamano. */
function pastel(nodo, datos, opciones) {
  opciones = opciones || {};
  const total = datos.reduce((a,b) => a + b.value, 0);

  /* La leyenda va en DOS renglones fijos, no en los que le toquen al ajustarse
     al ancho: asi los cuatro pasteles tienen la leyenda de la misma altura y
     los circulos quedan alineados entre paneles. Una sola leyenda con salto
     automatico da tres renglones en un panel y uno en otro, y los pasteles
     dejan de estar a la misma altura.
     Son dos componentes `legend`, cada uno con su mitad y su propia distancia
     al borde: ECharts no sabe partir una leyenda en renglones a peticion. */
  const nombres = datos.map(d => d.name);
  const corte = Math.ceil(nombres.length / 2);
  const renglones = [nombres.slice(0, corte), nombres.slice(corte)]
    .filter(r => r.length);
  /* CANVAS y no SVG a proposito: con el renderizador SVG, `getDataURL` devuelve
     un data URI de SVG y el archivo descargado seria un .svg con nombre .png,
     que Word y PowerPoint no abren. Con canvas sale un PNG de verdad, y ademas
     se puede pedir a 3x para que no se vea pixeleado al imprimirlo. */
  const grafica = echarts.init(nodo, null, {renderer:'canvas'});
  grafica.setOption({
    animation: false,
    tooltip: {
      trigger:'item',
      valueFormatter: v => mil(v) + ' tuits',
      confine: true
    },
    legend: renglones.map((data, i) => ({
      type: 'plain', data,
      bottom: (renglones.length - 1 - i) * 21, left: 'center',
      itemWidth: 11, itemHeight: 11, itemGap: 14,
      /* La leyenda lleva tinta de TEXTO, no el color de su serie: el color ya
         lo carga el cuadrito de al lado. */
      textStyle: {color: opciones.tinta2, fontSize: 12}
    })),
    series: [{
      type: 'pie',
      /* Dona y no disco: el hueco es donde va el total, que es el dato que
         mas se consulta y que un pastel normal obliga a sumar a ojo. */
      radius: ['34%', '55%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      /* minAngle EN CERO, no en 2. `minAngle` es de serie, no de rebanada: con
         2 le daba tambien 2 grados a los niveles que valen 0, y en perspectiva
         politica salian dos lineas de color -- una azul a las 12 y una gris a
         las 10 -- que parecian rebanadas diminutas y no lo eran.
         Ponerlo en 0 no cuesta nada aqui: la rebanada real mas chica es 4 de
         104 = 3,8 %, o sea 13,8 grados, muy por encima de lo que `minAngle`
         habria rescatado. */
      minAngle: 0,
      padAngle: 1.2,
      itemStyle: {
        /* 2 px del color del fondo entre rebanadas. Es lo que permite leer
           como dos al par de rojos contiguos de los niveles 1 y 2. */
        borderColor: opciones.superficie, borderWidth: 2, borderRadius: 3
      },
      label: {
        color: opciones.tinta2, fontSize: 11.5, lineHeight: 15,
        formatter: p => partir(p.name).map(l => '{b|' + l + '}').join('\n')
                        + '\n{v|' + mil(p.value) + '}{p| · ' + pct(p.value, total) + '}',
        rich: {
          b: {color: opciones.tinta2, fontSize: 11.5},
          v: {color: opciones.tinta, fontSize: 13, fontWeight: 600,
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace'},
          p: {color: opciones.mudo, fontSize: 11.5}
        }
      },
      labelLine: {length: 12, length2: 12, lineStyle: {color: opciones.grid}},
      emphasis: {scale: true, scaleSize: 4},
      data: datos
    }],
    graphic: opciones.centro ? [{
      type:'group', left:'center', top:'42%', children:[
        {type:'text', style:{text: opciones.centro.cifra, textAlign:'center',
          fill: opciones.tinta, font:'600 26px ui-monospace, SFMono-Regular, Menlo, monospace'}},
        {type:'text', top: 28, style:{text: opciones.centro.pie, textAlign:'center',
          fill: opciones.mudo, font:'11px system-ui, sans-serif'}}
      ]
    }] : []
  });
  return grafica;
}

function tabla(filas, total, colores) {
  const cuerpo = filas.map((f,i) =>
    '<tr><td><span class="punto" style="background:'+colores[i]+'"></span>'+esc(f.etiqueta)+'</td>'
    + '<td>'+mil(f.n)+'</td><td>'+pct(f.n,total)+'</td></tr>').join('');
  return '<table><thead><tr><th>nivel</th><th>tuits</th><th>%</th></tr></thead>'
    + '<tbody>'+cuerpo+'</tbody>'
    + '<tfoot><tr><td><b>total</b></td><td><b>'+mil(total)+'</b></td><td>100 %</td></tr></tfoot></table>';
}

function dibujar() {
  const raiz = getComputedStyle(document.documentElement);
  const op = {
    tinta:  raiz.getPropertyValue('--tinta').trim(),
    tinta2: raiz.getPropertyValue('--tinta2').trim(),
    mudo:   raiz.getPropertyValue('--mudo').trim(),
    grid:   raiz.getPropertyValue('--grid').trim(),
    superficie: D.superficie
  };
  const graficas = [];

  const BARRA = el('<div class="barra">'
    + '<button class="png todas">Descargar las cuatro en PNG</button>'
    + '<span class="nota" style="margin:0">También hay un botón por gráfica, '
    + 'a la derecha de su título.</span></div>');
  RAIZ.appendChild(BARRA);

  /* ---- 1. cobertura ---------------------------------------------------- */
  const f = D.ficha;
  const pCob = el('<section class="panel">'
    + '<h2>El corpus completo y la rebanada que la rúbrica calificó'
    + '<button class="png" data-i="0" data-n="cobertura">PNG</button></h2>'
    + '<div class="chips">'
    + '<span class="n">'+mil(f.n_total)+' tuits</span>'
    + '<span class="n">'+f.turistas_total+' turistas</span>'
    + '<span class="n">'+mil(f.n_calificado)+' con calificación · '+pct(f.n_calificado,f.n_total)+'</span>'
    + '<span class="n">de '+f.turistas_calificado+' turistas</span>'
    + '</div>'
    + '<div class="lienzo" style="height:400px"></div>'
    + '<p class="nota">Un tuit entra en la rebanada naranja cuando la rúbrica le dio '
    + 'nivel mayor que 0 en al menos uno de esos indicadores. Los '+f.turistas_total
    + ' turistas son los autores del corpus entero; los '+mil(f.n_calificado)
    + ' tuits vienen de '+f.turistas_calificado+' de ellos, así que '
    + (f.turistas_total-f.turistas_calificado)+' no aportaron ninguno.'
    + (f.indicadores === 'cuatro' && f.n_solo_violencia
        ? ' De esos '+mil(f.n_calificado)+', '+f.n_solo_violencia+' lo son sólo por '
          + 'saliencia de violencia y no aparecen en ningún pastel de niveles: '
          + 'esa escala es de presencia, no de valencia.'
        : '')
    + '</p>'
    + '<details><summary>Ver los números</summary><div class="t"></div></details>'
    + '</section>');
  RAIZ.appendChild(pCob);

  const filasCob = [
    {etiqueta: f.etiqueta_con, n:f.n_calificado},
    {etiqueta: f.etiqueta_sin, n:f.n_no_calificado}
  ];
  const colCob = [D.color_calificado, D.color_no_calificado];
  graficas.push(pastel(pCob.querySelector('.lienzo'),
    filasCob.map((x,i) => ({name:x.etiqueta, value:x.n, itemStyle:{color:colCob[i]}})),
    Object.assign({}, op, {centro:{cifra: mil(f.n_total), pie:'tuits en total'}})));
  pCob.querySelector('.t').innerHTML = tabla(filasCob, f.n_total, colCob);

  /* ---- 2-4. un pastel por criterio de valencia ------------------------- */
  const rejilla = el('<div class="rejilla"></div>');
  RAIZ.appendChild(rejilla);

  D.criterios.forEach(c => {
    /* LOS CINCO NIVELES entran siempre, incluso los que valen 0.
       Los tres paneles tienen entonces la misma leyenda (3 + 2 renglones), el
       mismo alto y el mismo tamano de dona: puestos uno al lado del otro son
       comparables, que es para lo que existen. Si cada panel dibujara solo sus
       niveles con casos, el de perspectiva politica tendria una leyenda de dos
       elementos, su dona quedaria mas grande y a otra altura que las otras dos.

       Un nivel en 0 aporta su entrada de leyenda y NADA MAS: angulo cero, y sin
       etiqueta ni linea guia, que apuntarian a un punto del borde y solo
       estorbarian. Cuales estan vacios lo dice el aviso del panel. */
    const vacios = c.niveles.filter(n => n.n === 0).map(n => n.nivel);
    const avisos = [];
    if (vacios.length) avisos.push('sin casos en el nivel ' + vacios.join(' ni el '));
    if (c.faltante) avisos.push(mil(c.faltante) + ' bloqueados por el proveedor');

    const panel = el('<section class="panel">'
      + '<h2>'+esc(c.etiqueta)
      + '<button class="png" data-i="'+graficas.length+'" data-n="'+esc(c.corto)+'">PNG</button></h2>'
      + '<p class="sub sub-criterio">'+esc(c.nombre)+'</p>'
      + '<div class="chips">'
      + '<span class="n">'+mil(c.presente)+' tuits calificados</span>'
      + '<span class="n">'+pct(c.presente, D.ficha.n_total)+' del corpus</span>'
      + '</div>'
      + '<div class="lienzo" style="height:380px"></div>'
      /* El aviso se RESERVA aunque este vacio: si solo lo pusieran los paneles
         que tienen algo que avisar, los otros quedarian un renglon mas cortos y
         el `details` de abajo no alinearia entre paneles. */
      + '<p class="nota aviso-reservado">'
      + (avisos.length ? esc(avisos.join(' · '))+'.' : '')+'</p>'
      + '<details><summary>Ver los números</summary><div class="t"></div></details>'
      + '</section>');
    rejilla.appendChild(panel);

    graficas.push(pastel(panel.querySelector('.lienzo'),
      c.niveles.map(n => Object.assign(
        {name:n.etiqueta, value:n.n, itemStyle:{color: D.paleta_valencia[n.nivel-1]}},
        n.n ? {} : {label:{show:false}, labelLine:{show:false}})),
      Object.assign({}, op, {centro:{cifra: mil(c.presente), pie:'tuits calificados'}})));

    panel.querySelector('.t').innerHTML = tabla(c.niveles, c.presente,
      c.niveles.map(n => D.paleta_valencia[n.nivel-1]));
  });

  RAIZ.appendChild(el('<p class="nota">La escala de valencia ancla el 1 en odio, desprecio o '
    + 'juicio fuertemente negativo, el 3 en ambivalencia declarada y el 5 en fascinación o elogio '
    + 'superlativo. El cuarto criterio de la rúbrica —saliencia de violencia, presente en '
    + mil(D.ficha.violencia_presente)+' tuits— no tiene pastel aquí: su escala es de '
    + '<b>presencia</b>, no de valencia, y un tuit que menciona violencia no es un tuit negativo.</p>'));

  /* ---- descarga en PNG ------------------------------------------------- */
  /* 3x: el pastel se ve a ~560 px en pantalla y sale de ~1680 px, que aguanta
     una pagina impresa y una diapositiva sin verse pixeleado.
     El fondo va SOLIDO y del color del tema: un PNG transparente pegado en una
     diapositiva oscura deja las etiquetas negras sobre negro. */
  const PIXELES = 3;

  function descargar(i, nombre) {
    const url = graficas[i].getDataURL({
      type: 'png', pixelRatio: PIXELES, backgroundColor: D.superficie
    });
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pie_' + nombre + '.png';
    document.body.appendChild(a); a.click(); a.remove();
  }

  RAIZ.addEventListener('click', ev => {
    /* `.todas` tambien lleva la clase .png por el estilo, pero no tiene indice:
       su manejador es el de abajo. */
    const b = ev.target.closest('.png');
    if (b && !b.classList.contains('todas')) descargar(Number(b.dataset.i), b.dataset.n);
  });

  /* Las cuatro de una vez, escalonadas: los navegadores bloquean una rafaga de
     descargas simultaneas del mismo origen y solo llegaria la primera. */
  BARRA.querySelector('.todas').addEventListener('click', () => {
    const botones = Array.from(RAIZ.querySelectorAll('.png'));
    botones.forEach((b, k) => setTimeout(
      () => descargar(Number(b.dataset.i), b.dataset.n), k * 350));
  });

  addEventListener('resize', () => graficas.forEach(g => g.resize()));
}
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entrada", default=RUTA_ENTRADA)
    ap.add_argument("--salida", default=os.path.join("salida", "pies_rubrica.html"))
    ap.add_argument("--tema", choices=tuple(TEMAS), default="claro")
    ap.add_argument("--paleta", choices=tuple(PALETAS_VALENCIA), default="accesible",
                    help="accesible separa los niveles 1 y 2, contiguos en el pastel; "
                         "proyecto calca la paleta de EvaluadorTweets")
    ap.add_argument("--indicadores", choices=("cuatro", "tres"), default="cuatro",
                    help="cuatro incluye la saliencia de violencia (144 tuits); "
                         "tres deja solo los criterios con pastel de niveles (140)")
    args = ap.parse_args()

    if not os.path.exists(args.entrada):
        raise SystemExit("no encuentro {}".format(args.entrada))

    df = leer(args.entrada)
    datos = construir(df, TEMAS[args.tema], PALETAS_VALENCIA[args.paleta],
                      args.indicadores)

    pagina = (PLANTILLA.replace("__TEMA_CSS__", "  " + TEMAS[args.tema]["css"])
              .replace("__CDN__", CDN_ECHARTS)
              .replace("__DATOS__", json.dumps(datos, ensure_ascii=False)))

    carpeta = os.path.dirname(args.salida)
    if carpeta and not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    with io.open(args.salida, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(pagina)

    f = datos["ficha"]
    print("corpus      : {} tuits · {} turistas".format(f["n_total"], f["turistas_total"]))
    print("calificados : {} tuits ({:.1f} %) · {} turistas".format(
        f["n_calificado"], 100 * f["n_calificado"] / f["n_total"], f["turistas_calificado"]))
    for c in datos["criterios"]:
        print("  {:<22} n={:<4} {}".format(
            c["corto"], c["presente"],
            "  ".join("{}:{}".format(n["nivel"], n["n"]) for n in c["niveles"])))
    print("PIES · {}  ({:.0f} KB)".format(args.salida, len(pagina.encode("utf-8")) / 1024))


if __name__ == "__main__":
    main()
