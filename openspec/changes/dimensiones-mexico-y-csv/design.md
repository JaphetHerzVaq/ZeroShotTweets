## Context

El notebook mide cuatro dimensiones genéricas sobre 24 frases escritas a propósito. Este change le cambia las dimensiones —a las de la tesis, ancladas a México— y le da de comer corpus real por primera vez.

El archivo es `turistas_traducido.csv`: 2 631 filas, 52 columnas, del 1 de junio al 31 de julio de 2026. Lo que la inspección encontró condiciona casi todas las decisiones de abajo:

```
  lang         en 2059 (78%)   ja 432 (16%)   qme 64   und 21
               es 12   zxx 8   ht 5   in/art/tl 4   pt 3   fr 3   ...
               de 0    nl 0    ar 0                    23 valores distintos

  columnas     text + traducción (español, 99.8% lleno, incluidos los tuits en inglés)
               lang, id, created_at, base, corpus_type, like_count, retweet_count
               tipo, justificacion  ← VACÍAS en las 2 631 filas

  estratos     base: 8 valores, 1 055 filas (40%) de consultas de victimización
               corpus_type: volume 2 577 / consolidated 54

  suciedad     BOM en la primera columna
               is_retweet/is_quote con 'False' y 'FALSE' conviviendo
               69 filas sin created_at · 51 id repetidos · 6 sin traducción
               longitud media 110 caracteres, máxima 568
```

Tres supuestos del diseño vigente no sobreviven a ese cuadro. **Primero**, los seis grupos de idioma (`en`, `pt`, `fr`, `es_foreign`, `de_nl`, `ar`) no existen en el corpus: tres de ellos están en cero. **Segundo**, el japonés —16% del corpus— nunca se contempló. **Tercero**, el corpus no es una masa homogénea sino ocho estratos con intenciones de búsqueda distintas.

Y una restricción que no cambia: `dimension-visualization` sigue en curso (77/79). Este change modifica tres de sus capacidades antes de que se archiven.

## Goals / Non-Goals

**Goals:**

- Medir las dimensiones de la tesis —ambiente, imagen cultural, perspectiva política, violencia y seguridad— en vez de las genéricas heredadas.
- Anclar el instrumento a México sin que el ancla contamine el reparto de probabilidad entre hipótesis.
- Ejecutar el notebook sobre el corpus real sin que ninguna figura haya que rehacerla.
- Responder con números la objeción «traduce todo y usa el léxico», que el corpus ya permite contestar gratis.
- Que ningún número agregado mezcle estratos con intención de búsqueda distinta sin decirlo.
- Conservar el argumento de sesgo entre idiomas, que es lo que justifica el rediseño ante un revisor.

**Non-Goals:**

- **Validar el rediseño.** El corpus no trae codificación humana: `tipo` y `justificacion` están vacías en las 2 631 filas. La validación contra alfa de Krippendorff sigue pendiente y este change no la desbloquea.
- **Eje temporal.** El corpus trae dos meses de `created_at` y por primera vez sería posible; es un change aparte.
- **Cambiar las fórmulas de medición.** Ni `metodo_actual` ni `metodo_nuevo` se tocan. Cambian las hipótesis que entran, no la aritmética que sale.
- **Limpiar el corpus.** Nada de filtrar tuits fuera de tema por reglas: el eje de relevancia existe precisamente para medir eso, y filtrarlo a mano antes de medirlo sería decidir el resultado.
- **Reescribir la capa de figuras.** Ya es genérica; se le añade el desglose por estrato y poco más.

## Decisions

### 1. El ancla geográfica va en la plantilla, no en las etiquetas

`multi_label=False` calcula `softmax(logit_pos, logit_neg, logit_na)` sobre los logits de entailment. El softmax es invariante a un desplazamiento **constante** entre las tres etiquetas — y el ancla, metida dentro de cada etiqueta, no es constante:

```
  ancla EN LAS ETIQUETAS                        ancla EN LA PLANTILLA
  ─────────────────────────────────────         ─────────────────────────────────
  pos: "el ambiente EN MÉXICO fue alegre"       "Este texto sobre México dice que
  neg: "el ambiente EN MÉXICO fue desagr."       {}"
  na : "NO menciona el ambiente ... EN MÉXICO"
                                                 pos: "el ambiente fue alegre..."
  afirmación + predicado  → más difícil          neg: "el ambiente fue desagr..."
  negación   + predicado  → MÁS FÁCIL            na : "no menciona el ambiente..."

  → masa hacia na → relevancia ↓                 → prefijo idéntico en las 3
  → alerta de "dimensión muda" por redacción     → se cancela en el softmax
```

El corpus agrava el problema: el 78% son tuits en inglés que hablan de la Copa sin nombrar México, y algunos ni siquiera hablan de la Copa. Con el ancla dentro de las etiquetas, `relevancia = 1 − P(na)` caería en bloque bajo `UMBRAL_MUDEZ = 0.30` y las tres dimensiones dispararían la alerta de `UMBRAL_DIMENSION_MUDA = 0.70` por un artefacto de redacción, no por el corpus.

*Alternativa considerada:* dejar el ancla en las etiquetas y bajar `UMBRAL_MUDEZ`. Rechazada: mueve el umbral para tapar un defecto del instrumento, que es exactamente lo que el notebook advierte en su propia celda de configuración.

*Verificación:* el argumento es mecánico, no medido. La batería corre con las dos variantes tras un interruptor y se comparan las distribuciones de relevancia. Si el efecto no aparece, la decisión se revisa con el número delante.

### 2. La demostración entre idiomas se muda a `perspectiva_politica`

`hospitality` desaparece y con ella el sujeto de la sección 9. La frase de gobernanza, que ya existe en los seis idiomas de la batería, la sustituye sin traducir nada. Y es mejor demostración, por tres razones que el cálculo confirma:

```
  "La policía fue corrupta y no hizo nada, las autoridades nos fallaron"

  en   +0.1600   + [authorities, police] / − [corrupt]
  es   −0.1600   −  [corrupt]     ← por SUBCADENA dentro de "corrupta"
  pt   −0.1600   −  [corrupt]     ← por SUBCADENA dentro de "corrupta"
  fr   +0.1600   +  [police]
  de   +0.0000   (ninguna)
  ar   +0.0000   (ninguna)
                 rango 0.3200 · σ 0.1306
```

En inglés el método actual **puntúa positivo un texto que dice que la policía era corrupta**, porque `police` y `authorities` viven en la lista positiva. En español y portugués puntúa negativo. Es inversión de signo, no dispersión.

Además: `governance_trust = clamp(mg * 0.8)` no incorpora el sentimiento, así que el número es exacto, determinista y reproducible sin GPU —citable en la tesis sin depender de una corrida—; y los emparejamientos `corrupt ⊂ corrupta` pueblan con ejemplos reales la figura de cobertura léxica, que con las frases de hospitalidad probablemente reportaba «no observado en este corpus».

*Alternativa considerada:* conservar `hospitality` como cuarta dimensión. Rechazada por el usuario: no entra en la tesis, y costaría 16 pasadas por texto en vez de 13 (+23% sobre 2 631 tuits).

### 3. La batería se reacomoda; una sola frase nueva

```
  frase existente      objetivo hoy        objetivo nuevo              ¿traduce?
  ───────────────────────────────────────────────────────────────────────────────
  gobernanza_neg       governance_trust →  perspectiva_politica + §9      no
  control_mudo/tacos   (mudo)           →  imagen_cultural (pos)          no
  hospitalidad_pos     hospitality      →  CONTROL MUDO de las 3          no
  violencia            violence_salience→  igual                          no
  ambiente_pos  NUEVA  —                →  atmosfera (pos)            sí, ×6
```

Los tacos dejaban de ser mudos de todas formas: son comida, es decir `imagen_cultural`. En vez de pelearlo, se ascienden. Y «la gente fue amable» no habla de ánimo de México, comida, lugares ni gobierno, así que sirve de control mudo del trío nuevo conservando sus seis traducciones.

La aserción de coherencia entre `BATERIA` y `MISMA_FRASE` que vive en la celda de figuras cambia de clave: de `hospitalidad_pos` a `gobernanza_neg`, que es la que la sección 9 pasa a imprimir.

### 4. Comparación a tres vías, con la tercera gratis

```
  (a) léxico   ← text          método actual
  (b) léxico   ← traducción    la alternativa barata      ← CERO pasadas de modelo
  (c) zeroshot ← text          el rediseño

  costo NLI: 13 pasadas/tuit · 34 203 en total — el mismo que correr solo (a) y (c)
  costo extra de (b): 1 pasada del modelo de SENTIMIENTO (base) por tuit
```

Un revisor va a preguntar por qué no traducir todo y seguir con el léxico. El corpus ya trae la traducción y el léxico es emparejamiento de strings, así que la respuesta casi no cuesta. **Casi**, no del todo: `atmosfera = clamp(s×0.7 + ma)` incorpora el sentimiento, y el sentimiento de la traducción hay que calcularlo, no heredarlo. Es una pasada de un modelo *base* por tuit; ninguna del *large*, que es el que fija el tiempo de la corrida. `(b)` entra en `LARGO` como un tercer valor de la columna `metodo`, no como una columna nueva: la forma del marco no cambia y las figuras lo recogen solas.

*Alternativa considerada:* añadir `(d)` zero-shot sobre la traducción, para probar si el modelo multilingüe necesita que le traduzcan. Duplicaría el cómputo NLI a 68 406 pasadas. Queda como interruptor apagado por defecto.

*Consecuencia que hay que declarar:* `(b)` mide el léxico **más** la calidad de una traducción automática. Si `(b)` gana a `(a)`, parte del mérito es del traductor y no del léxico, y eso se dice en la figura.

### 5. Los grupos de idioma se derivan del corpus

El notebook declara seis grupos; el corpus tiene 23 valores de `lang`, tres de los grupos en cero, y un idioma no contemplado que pesa 16%. La lista de idiomas de toda figura sale de `LARGO["lang"].value_counts()`, no de una constante, con un mínimo de observaciones por idioma para no dibujar puntos sobre `n = 1`.

Los códigos `qme`, `und`, `zxx`, `qam`, `qst` son marcas de Twitter para «sin idioma detectable», no idiomas: se agrupan en una categoría `sin_idioma` explícita en vez de dibujarse como si lo fueran.

El japonés deja de ser una ausencia y pasa a ser el hallazgo: **432 tuits que el léxico de `analyzer.py` no puede ver**, porque no contiene una sola palabra en japonés. Sobre la batería eso era una hipótesis; sobre el corpus es un número.

*Alternativa considerada:* mapear los 23 valores a los seis grupos del proyecto. Rechazada: inventaría los grupos vacíos y escondería el japonés dentro de un cajón de sastre.

### 6. Estratos en el marco, desglose en las figuras

`base` y `corpus_type` entran como columnas de `LARGO` junto a la procedencia. Toda figura que promedie se desglosa por estrato, y emite alerta escrita cuando un promedio mezcla estratos con intención de búsqueda distinta.

El caso que lo obliga: 1 055 filas (40%) vienen de consultas de victimización. Un `violence_salience` promedio sobre el corpus completo mide sobre todo la consulta que lo recolectó. No es un matiz metodológico: es la diferencia entre un número citable y uno que no lo es.

### 7. La entrada: tres modos y un mapeo declarado

```
  FUENTE = "bateria" | "propios" | "csv"

  csv → RUTA_CSV (autodetección del único .csv del directorio de trabajo;
                  si hay cero o más de uno, se detiene y los lista)
        encoding="utf-8-sig"        ← el archivo trae BOM
        COLUMNA_TEXTO = "text" | "traducción"
        COLUMNAS = {texto, id, created_at, lang, likes, retweets, base, corpus_type}
        N_MUESTRA   tope para cronometrar antes de comprometer el corpus
        DEDUPE      por id (51 repetidos de 2 631)
```

El mapeo se declara y se valida contra el encabezado real: si falta una columna, el error imprime las 52 que sí están, en vez de reventar con un `KeyError` a mitad de la corrida. Los booleanos se parsean insensibles a mayúsculas, porque `False` y `FALSE` conviven en el archivo.

`META` ya tiene los huecos `tweet_id`, `created_at` y `lang` reservados con el comentario «se puebla cuando la entrada sea el corpus». Esta es esa entrada: el contrato se cumple, no se reinventa.

### 8. Evaluación por lotes

`_nli()` llama hoy al pipeline texto por texto. Con 24 textos da igual; con 2 631 son 34 203 pasadas de un modelo *large* de a una. Se pasa una lista al pipeline con `batch_size` configurable. La forma de la salida no cambia —sigue devolviendo `{etiqueta: probabilidad}` por texto— así que `metodo_nuevo` y todo lo que cuelga de él quedan igual.

El notebook ya cronometra con `TIEMPO_CORRIDA` y lo imprime en la ficha técnica. Con `N_MUESTRA` se mide sobre 200 y se extrapola antes de lanzar las 2 631.

### 9. El rótulo de procedencia se vuelve de tres estados

Hoy es binario: `ES_BATERIA` decide si una figura lleva el sello «instrumento de prueba, no reportable». Con el CSV hacen falta tres estados —batería, textos propios, corpus— porque el rótulo del corpus no es «no reportable» sino otro: **descriptivo pero no validado**, ya que no hay codificación humana contra la cual contrastar. Es el rótulo más importante del notebook a partir de ahora: 2 631 tuits reales invitan a leer los números como hallazgos firmes justo cuando todavía no lo son.

### 10. Los resultados salen a disco en dos formas, y las salidas no viven donde la entrada

El notebook no escribía ningún archivo de datos. Ahora escribe dos:

```
  salida/resultados_enriquecidos.csv   1 fila por tuit
                                       52 columnas originales + 28 de resultados
                                       para Excel y para compartir

  salida/resultados_largo.csv          1 fila por texto x metodo x dimension
                                       para analizar y graficar
```

Dos formas y no una porque responden a preguntas distintas, igual que los tres marcos: el ancho se abre y se lee, el largo se filtra y se agrupa. Forzar una sola obligaría a elegir entre columnas ilegibles o un archivo que no se puede abrir en una hoja de cálculo.

El ancho se une al archivo original **por identificador, no por posición**: el dedupe y el muestreo ya movieron las filas de sitio. Y va en `utf-8-sig`, por la misma razón por la que el archivo de entrada trae BOM: sin él, Excel abre los acentos y el japonés como basura.

**Las salidas van a `salida/`, nunca al directorio de entrada.** No es orden por gusto: la autodetección del CSV busca en el directorio de trabajo, así que con las salidas ahí la segunda corrida encuentra tres archivos y el notebook se bloquea a sí mismo. Se descubrió ejecutándolo dos veces seguidas, no razonándolo.

*Alternativa considerada:* excluir por nombre los archivos que el notebook escribe. Se implementó y **no basta** — la exclusión depende de los nombres configurados, así que renombrar la salida vuelve a romperlo. Queda como segundo cinturón, por si alguien pone `SALIDA_DIR = "."`.

**La guardia de valencia × relevancia se repite a la salida**, que es donde más importa: un CSV se abre en Excel y ahí nadie recuerda por qué esas dos columnas no se podían multiplicar.

## Risks / Trade-offs

**El ancla en la plantilla podría no bastar** → El prefijo «sobre México» es constante entre etiquetas, pero el modelo puede seguir penalizando textos sin relación con México. Mitigación: la corrida A/B de la batería mide el efecto, y la distribución completa de relevancia se dibuja con el corte superpuesto, así que se ve en vez de deducirse.

**El corpus es mayormente ruido** → Las primeras filas inspeccionadas hablan de Apple TV y de actores de voz japoneses. Si casi todo da relevancia baja, las figuras de valencia se quedan sin observaciones. Mitigación: no se filtra nada; la proporción de mudez **es** el resultado, y el umbral mínimo de observaciones por figura ya existe y avisa.

**`(b)` mide traducción y léxico a la vez** → Si gana, no se sabe cuánto es mérito de cada uno. Mitigación: declararlo en la figura y en la tesis. No hay forma de separarlos sin traducciones de referencia humanas.

**El japonés podría no funcionar en el sentimiento** → `twitter-xlm-roberta-base-sentiment` cubre ocho idiomas y el japonés no está entre ellos; XLM-R-XNLI sí lo cubre. Mitigación: comprobar la distribución de etiquetas de sentimiento del bloque japonés y declarar la limitación si degrada. Afecta a `atmosfera` en el método actual, cuya fórmula incorpora el sentimiento; no afecta al rediseño.

**El CSV exportado viaja más lejos que el notebook** → Un archivo se reenvía, se abre en Excel y se cita sin el contexto que lo rodeaba. Mitigación: la celda imprime la procedencia y la advertencia de no-validado al exportar, y los nombres de columna llevan el método dentro (`__actual`, `__traducido`, `__nuevo`) para que no se puedan confundir entre sí.

**Sobreinterpretación de 2 631 tuits sin validar** → Es el riesgo más caro del change, porque es el que se cuela en la tesis sin hacer ruido. Mitigación: el rótulo de tres estados, la advertencia explícita de que `tipo` y `justificacion` están vacías, y mantener a la vista que la validación contra codificación humana sigue pendiente.

**Cuatro celdas de medición cambian a la vez** → Dimensiones, ancla, idioma de hipótesis y entrada. Si los números salen raros, no se sabrá cuál lo causó. Mitigación: el orden de la migración de abajo, que introduce un cambio por paso y corre la batería entre paso y paso.

**`dimension-visualization` se modifica en vuelo** → Sus tareas `10.5` y `10.14` siguen abiertas y `10.5` deja de tener sentido. Mitigación: se redefine explícitamente contra el control mudo nuevo en vez de darla por buena.

## Migration Plan

Un cambio por paso, con la batería corrida entre cada uno, para que cualquier movimiento raro en los números tenga un solo culpable posible:

1. **Dimensiones e hipótesis** con ancla en la plantilla e `IDIOMA_HIPOTESIS = "es"`. Batería. Comparar contra la corrida previa.
2. **A/B del ancla.** Confirmar o refutar la decisión 1 con la distribución de relevancia.
3. **Batería reacomodada** y sección 9 sobre `perspectiva_politica`. Verificar que la dispersión impresa coincide con la que recalcula la figura.
4. **Tercera vía `(b)`** y `ESCALAS` con `imagen_cultural` a un solo método. Verificar que las figuras 1, 3 y 6 la excluyen y lo explican.
5. **Rama CSV** con `N_MUESTRA = 200`. Cronometrar y extrapolar.
6. **Lotes.** Verificar que los valores son idénticos a los de la corrida sin lotes.
7. **Corpus completo**, estratos y rótulo de tres estados.

Rollback: existe `rediseno_zeroshot_colab.ipynb.bak`, y cada paso es una celda. El paso 6 es el único que podría alterar valores en silencio, de ahí que su verificación sea comparar contra la corrida previa y no solo que no reviente.

## Open Questions

- **¿Qué hacer con los 69 tuits sin `created_at`?** No molesta mientras no haya eje temporal, pero coinciden en número exacto con las filas de casing anómalo (`FALSE`), lo que sugiere un lote fusionado de otra fuente. Vale la pena confirmar si son un estrato propio.
- **`text` vs `text_completo`** son idénticas en las 2 631 filas. Se usa `text`; si en una recolección futura divergen, la decisión hay que rehacerla.
- **El corte a 512 caracteres** afecta a pocos tuits (máximo observado: 568). Queda como está, pero conviene contar cuántos se truncan y decirlo.
- **¿Los seis tuits sin traducción** se excluyen de `(b)` o se les pasa el original? Propuesta: excluirlos y contarlos, nunca sustituirlos en silencio.
