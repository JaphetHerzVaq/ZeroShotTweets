## Why

La rúbrica de EvaluadorTweets tiene **polaridad declarada** en tres de sus cuatro criterios —el nivel 1 es odio, desprecio o juicio fuertemente negativo y el nivel 5 es fascinación o elogio superlativo— y ninguna figura de la v3 la usa. Todo el análisis NLP de la sección 16 parte de `calificado` contra `no_calificado`, es decir de *presencia contra ausencia*, y colapsa en un solo grupo a los 76 tuits que admiran México y a los 45 que lo desprecian. Lo que distingue el vocabulario de la hostilidad del de la admiración no está en ninguna parte de la página.

Falta además una figura de entrada: la sección 16 abre con el mapa UMAP, que exige entender qué es un embedding antes de ver nada. No hay ninguna vista que diga de un vistazo de qué habla el corpus, ni que enfrente lo que la colecta pescó (2 631 tuits) con lo que la rúbrica reconoció (144).

## What Changes

- **Cinco nubes de palabras nuevas en la sección 16**, sobre lemas de spaCy de la traducción (`NOUN`, `PROPN`, `ADJ`), que es el único espacio donde el corpus multilingüe es comparable:

  | nube | universo | n | peso |
  |---|---|---|---|
  | corpus completo | todos los tuits | 2 631 | frecuencia |
  | calificados | algún nivel > 0 | 144 | frecuencia |
  | positivo | algún 4–5, ningún 1–2 | 76 | z de log-odds, uno contra resto |
  | negativo | algún 1–2, ningún 4–5 | 45 | z de log-odds, uno contra resto |
  | ambivalente | sólo niveles 3 | 19 | z de log-odds, uno contra resto |

- **Regla de polaridad con los polos primero y la ambivalencia como residuo.** Tomar «algún nivel 3» como definición de ambivalencia produce tres tuits en dos grupos a la vez —dos con atmósfera 4 e imagen 3, uno con atmósfera 3 pero imagen 2 y política 1—, y ninguno de los tres es ambivalente: tienen polo claro y ambivalencia en un criterio secundario. Con los polos primero la partición es **disjunta y exhaustiva**: 76 + 45 + 19 + 4 = 144. Se fija como aserción, no como suposición.
- **Los cuatro criterios no son del mismo tipo y la página lo dirá.** La saliencia de violencia es de escala `presencia`, no de valencia: un tuit que menciona violencia no es un tuit negativo. Los 4 tuits calificados sólo por ese criterio quedan **fuera de las tres nubes de polaridad y del prior**, y se cuentan en un aviso del panel.
- **Dos pesos, dos preguntas distintas, declaradas en cada panel.** Las dos primeras nubes describen: tamaño = frecuencia. Las tres de polaridad comparan: tamaño = z de log-odds con prior informativo (Monroe, Colaresi y Quinn, 2008), uno contra el resto sobre los 140 tuits con polaridad. Una nube de frecuencia cruda sobre 45 y 19 tuits se leería como hallazgo siendo ruido, y contradiría en la misma página al panel de log-odds que ya existe justo encima.
- **Aviso de vocabulario escaso.** Con `MIN_FRECUENCIA_LOGODDS = 3` el grupo ambivalente aporta unas dos decenas de términos. El panel declara en sus chips cuántos tuits y cuántos términos sostienen cada nube, para que la más pobre no se lea igual que la más rica.
- **`log_odds` se generaliza de dos grupos fijos a cualquier par.** Hoy el estimador ya recibe dos `Counter`, pero devuelve las llaves `calificados` y `no_calificados` y el panel rotula «z > 0 es característico de los calificados». Reutilizarlo tal cual haría que la página dijera «calificados» donde quiere decir «positivo».
- **Segunda dependencia de CDN con su propio modo de falla.** `echarts-wordcloud` es una extensión aparte de ECharts 5.6.0. La plantilla asume hoy un solo fallo posible; si ECharts carga y la extensión no, la página se vería sana con cinco paneles vacíos en silencio.
- **La tabla resumen de la sección 2 deja de mezclar presencia con valencia.** Hoy pone los 25 tuits que *mencionan* violencia bajo el encabezado «nivel 1», la misma columna donde, para los tres criterios de valencia, el número son tuits de odio o desprecio. El gráfico de esa sección ya excluye la violencia y el panel del criterio ya avisa que no es una escala de valencia: sólo la tabla se quedó atrás. La corrección se limita a esa tabla.
- **Las frecuencias salen de Colab.** Los lemas y las entidades son CPU pura: sólo los embeddings y el agrupamiento necesitan GPU. Se añade `frecuencias_corpus.py`, un script local que **ejecuta los bloques del propio notebook** —sin reimplementar la limpieza, el diccionario de entidades, `POS_LEMAS` ni la regla de polaridad— y publica las frecuencias como CSV, por corpus, por grupo, por polaridad y por criterio. Para que eso sea posible, las celdas de NLP se parten por su frontera real: lo que necesita acelerador queda en celdas propias y marcadas.
- **Trazado determinista.** wordcloud2 coloca por espiral sobre el lienzo y su resultado depende del tamaño del canvas y de la rotación. El notebook es reproducible en todo lo demás (`SEMILLA_NLP`, `SEMILLA_VALIDACION`, `huella_instrumento`, la aserción entre `BATERIA` y `MISMA_FRASE`): las nubes se fijan en tamaño y sin rotación, y los parámetros van a la ficha técnica.

## Capabilities

### New Capabilities

- `term-frequency-export`: obtención de las frecuencias de lemas y entidades fuera de Colab y sin GPU, reutilizando los bloques del notebook como única fuente de verdad, con los cortes declarados y las dos formas de contar en cada fila.
- `rubric-word-clouds`: derivación de la polaridad de un tuit a partir de los niveles de la rúbrica, partición disjunta de los calificados, y las cinco nubes de palabras con sus dos esquemas de peso, sus avisos de escasez y su trazado determinista.

### Modified Capabilities

Ambas viven en el change `v3-validacion-rubrica-y-nlp`, hoy en curso (65/68), todavía sin archivar.

- `corpus-nlp`: el contraste de vocabulario deja de estar atado a los grupos calificado/no calificado y pasa a ser un contraste entre dos conjuntos cualesquiera, con los rótulos derivados de los grupos comparados en vez de escritos a mano.
- `rubric-results`: la declaración de escala por criterio pasa a gobernar también las tablas, no sólo las figuras, y la cuenta de un criterio de presencia deja de compartir columna con los niveles de valencia.

## Impact

**Nuevo notebook `rediseno_zeroshot_colab_v4.ipynb`**, derivado de la v3. La v1, la v2 y la v3 quedan intactas, como en cada change anterior. Celdas tocadas respecto de la v3:

- celda 5 · `PLANTILLA_V3`: segundo `<script>` y respaldo que distingue «no cargó ECharts» de «cargó ECharts pero no la extensión».
- celda 6 · `construir_rubrica`: columna `polaridad` en `RUBRICA_TUIT` y aserción de partición. Es su lugar: el notebook declara que la regla de codificación de la rúbrica vive en un solo sitio.
- celda 7 · tabla resumen del panel «Distribución de valencia · todo el corpus»: columna propia para la cuenta de los criterios de presencia. Nada más de la sección 2 se toca.
- celda 37 · configuración: umbral de frecuencia por nube, número de términos y parámetros de trazado.
- celda 39 · `log_odds` con rótulos genéricos, y los contadores de lemas por grupo de polaridad.
- celda 41 · cinco paneles nuevos y su JS.
- celdas de NLP partidas por su frontera de acelerador, con marcador `# === BLOQUE: … ===` en las que el script necesita localizar.

**Archivo nuevo:** `frecuencias_corpus.py` y sus salidas `salida/frecuencias_lemas.csv`, `salida/frecuencias_entidades.csv` y `salida/frecuencias_grupos.csv`.

**Dependencia nueva:** `echarts-wordcloud` 2.x desde CDN. No añade dependencias de Python ni tiempo de GPU: los lemas ya están calculados en la celda 39.

**Tesis:** las nubes heredan la declaración que ya pesa sobre toda la sección 16 —la traducción automática es un uso nuevo del material y cinco traducciones las completó otro modelo el 13/09—. Las tres nubes de polaridad describen el vocabulario de **la rúbrica aplicada por un modelo de lenguaje**, no el de codificadores humanos.

**Fuera de alcance:** cambiar la rúbrica, recalificar, y tocar la colisión `aplicable`/nivel 0 del motor de EvaluadorTweets.
