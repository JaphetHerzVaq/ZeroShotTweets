## Why

El notebook demuestra con números que el rediseño zero-shot mide mejor que el léxico actual, pero los entrega como texto alineado con `str.format`. La sección 7 —el argumento central de la tesis, que el instrumento actual varía con el idioma cuando el contenido no varía— termina en dos líneas que dicen `rango 0.6000 desv.est. 0.2449`. Un revisor no puede ver eso; tiene que creerlo.

Además el notebook **no corre de arriba a abajo**: la celda 12 lanza `ValueError` con los tuits de relleno, así que hoy no hay forma de ejecutarlo y obtener una figura sin pegar datos propios primero.

## What Changes

- **Corpus de ejemplo embebido** de 24 textos: cuatro frases —hospitalidad positiva, gobernanza negativa, violencia, y un control mudo sobre comida— traducidas a los seis grupos de idioma que el proyecto recolecta (`en`, `es`, `pt`, `fr`, `de`, `ar`). Sustituye a los dos textos de relleno que hoy abortan la ejecución. El control mudo es el que prueba el eje de relevancia: un tuit sobre tacos debe dar `relevancia ≈ 0` en gobernanza, no un juicio neutro.

- **Frame tidy único** del que salen todas las figuras y también la tabla resumen actual. Hoy la celda 17 construye su tabla a mano y en el camino descarta `violence_salience`, `safety_perceived`, `overall_sentiment`, `engagement_weight` y todas las probabilidades crudas de `_crudo`, que son justamente lo que hace falta graficar.

- **Sección de figuras** con seis gráficas, cada una respondiendo una pregunta y con su umbral y su alerta escrita, al modo del `distribucion()` de EvaluadorTweets:

  | Figura | Pregunta que responde |
  |---|---|
  | Dispersión entre idiomas, ACTUAL vs NUEVO | ¿el instrumento mide lo mismo cuando el contenido es el mismo? |
  | Plano `score` × `relevancia` | ¿cuántos de los ceros de hoy son "no habló" y cuántos "juzgó neutro"? |
  | El escalón | ¿qué valores puede tomar cada método? |
  | Ausencia por dimensión | ¿esta dimensión mide algo en este corpus, o está muda? |
  | Descomposición `pos` / `neg` / `na` | ¿a dónde se va la masa de probabilidad del modelo? |
  | Cobertura léxica por idioma | ¿en cuántos idiomas el léxico llega a activarse? |

- **La ausencia nunca se apila con la escala.** `score` y `relevancia` son ejes ortogonales y ninguna figura los colapsa: no se promedia `score` sin condicionar por `relevancia`, y la zona `relevancia < UMBRAL_MUDEZ` queda marcada en toda figura que muestre `score`. Es la misma decisión que EvaluadorTweets tomó para su nivel `0`, con la diferencia de que aquí la ausencia se mide por construcción en vez de remendarse después.

- **Gráficas con Apache ECharts por CDN**, configuración serializada desde Python con `json.dumps` e inyectada con `IPython.display.HTML`. Misma arquitectura que `scoring-visualization` de EvaluadorTweets, por la decisión de que ambos proyectos convergerán sobre el corpus de turistas: cuando eso ocurra, el eje temporal y el filtro por idioma se enchufan sin rehacer la capa de figuras.

- **Compatibilidad hacia adelante con el corpus**: el frame tidy reserva columnas opcionales `tweet_id`, `created_at` y `lang`, vacías mientras la entrada sea una lista de textos y pobladas cuando la entrada sea el CSV de turistas. Ninguna figura las exige.

- **Salida para tesis**: cada figura exportable como PNG a `pixelRatio` 3 desde la barra de herramientas de ECharts, legible en escala de grises, y con el número reportable impreso al pie. Más un HTML autocontenido que sobrevive al cierre del notebook.

- **Ficha técnica del instrumento** embebida en la página: las frases de hipótesis textuales, `IDIOMA_HIPOTESIS`, la plantilla y los modelos con su versión. La celda 3 del notebook dice que las hipótesis son el instrumento de medición y que en la tesis van citadas textualmente; la figura que produce el resultado debe cargar consigo el instrumento que lo produjo.

- **Segundo defecto del método actual, medido**: `_mod()` empareja por subcadena sobre el texto crudo (`w in tl`). Verificado: `"The place felt unsafe at night"` da `governance_trust = +0.160` porque `safe` está dentro de `unsafe`; `"unfriendly"` activa `friendly`; `"kinda"` activa `kind`; `"global warming"` activa `warm`; y `"La policía fue corrupta e ineficaz"` da exactamente `0.000` porque `policia` y `corrupt` se anulan. La figura de cobertura léxica cuenta cuántos emparejamientos del corpus son de este tipo. Es independiente del argumento de idiomas y no requiere GPU.

## Capabilities

### New Capabilities

- `example-corpus`: Proveer un corpus de ejemplo embebido, balanceado por idioma y por dimensión e incluido un control sin contenido evaluable, que permita ejecutar el notebook de principio a fin y producir todas las figuras sin que el usuario aporte datos, sin impedir que los sustituya por los suyos.
- `dimension-results-frame`: Construir una sola vez, a partir de los resultados de ambos métodos, un frame en formato largo que conserve las cinco dimensiones, las probabilidades crudas, la relevancia y la procedencia de cada valor, y que sirva de sustrato único para toda figura y toda tabla.
- `dimension-visualization`: Renderizar el frame como figuras interactivas de Apache ECharts que mantienen separados el eje de valencia y el eje de ausencia, comparan el método actual contra el rediseño, disparan alertas escritas al cruzar umbrales configurables, y se exportan como PNG apto para impresión y como HTML autocontenido.

### Modified Capabilities

Ninguna. `openspec/specs/` está vacío: este es el primer change del proyecto.

## Impact

**Notebook**: `rediseno_zeroshot_colab.ipynb`. La celda 12 cambia de comportamiento —deja de abortar y trae el corpus de ejemplo—; la celda 17 pasa a leer del frame tidy en vez de construir su tabla a mano. El resto de las celdas existentes no se toca. Se añaden una celda de configuración de figuras, una de construcción del frame y la sección de figuras.

**Dependencias**: ninguna nueva del lado de Python. `pandas` ya se usa en la celda 17; `json` e `IPython.display` vienen con Colab. ECharts se carga por CDN dentro de la página generada.

**Costo de ejecución**: el corpus de ejemplo son 24 textos × 13 pasadas de NLI = 312 pasadas de un modelo *large*, más 24 de sentimiento. Es el precio de que el notebook produzca figuras sin datos del usuario, y hay que medirlo y dejarlo escrito, porque la sección 9 del notebook advierte que en CPU esto puede ser inviable.

**Dependencia oculta que queda saldada**: hoy la celda 17 usa `filas_demo`, que nace en la celda 15, así que ejecutar la tabla resumen sin haber corrido la sección 7 revienta con `NameError`. El frame único elimina el acoplamiento.

**Escala**: con 24 textos, el plano `score` × `relevancia` y el histograma de ausencia son ilustrativos, no concluyentes. Toda figura declara su `n` y advierte cuando cae por debajo del umbral, en vez de dibujar con aplomo sobre cuatro puntos.

**Convergencia con EvaluadorTweets**: este change adopta deliberadamente la arquitectura de `scoring-visualization` —pre-agregar en pandas, filtrar en el cliente, ECharts por CDN, doble salida— aunque hoy no haya eje temporal ni volumen que lo exijan. Lo que no adopta son los períodos, la media móvil ni los huecos por día sin datos: no hay fechas en este notebook mientras la entrada sea una lista de textos.

**Lo que este change no hace**: no valida el rediseño. La sección 9 del notebook pide codificar a mano ~200 tuits y calcular el alfa de Krippendorff contra cada método con umbral 0.67. Las figuras describen; no sustituyen esa validación, y deben decirlo donde se leen.
