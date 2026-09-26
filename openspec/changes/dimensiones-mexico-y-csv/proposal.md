## Why

Las dimensiones del notebook son genéricas —«el ambiente», «las autoridades», «la gente local»— y la tesis no es sobre turismo en abstracto: es sobre **la imagen de México**. Tres de las cuatro dimensiones hay que reescribirlas, una sobra (`hospitality`) y falta la que más importa (`imagen_cultural`: comida, lugares, cultura).

Y ya hay corpus real: `turistas_traducido.csv`, 2 631 tuits del 1 de junio al 31 de julio de 2026. El notebook no puede leerlo —su única entrada es una batería de 24 frases escritas a propósito— y el corpus, al inspeccionarlo, contradice tres supuestos del diseño actual que conviene corregir ahora y no después.

## What Changes

### El instrumento

- **BREAKING — se elimina `hospitality`.** El conjunto medido pasa a ser `atmosfera`, `imagen_cultural`, `perspectiva_politica`, `violence_salience` y `safety_perceived`. El costo se mantiene en 13 pasadas de NLI por texto: tres dimensiones de tres hipótesis más el grupo de violencia de cuatro.

- **BREAKING — la sección 9 se repunta a `perspectiva_politica`.** Es la demostración central de sesgo entre idiomas y hoy corre sobre `hospitality`. Se muda a la frase de gobernanza que ya existe en los seis idiomas, sin traducir nada nuevo. El argumento mejora: el léxico actual le da **+0.1600 en inglés** a un texto que dice que la policía era corrupta —porque `police` y `authorities` están en la lista positiva— y **−0.1600 en español y portugués**. Misma frase, seis idiomas, inversión de signo. Como `governance_trust` no incorpora el sentimiento, el número es exacto y reproducible sin GPU.

- **El ancla «México» va en la plantilla, no en las etiquetas.** `PLANTILLA = "Este texto sobre México dice que {}."` con hipótesis genéricas. Dentro de las etiquetas el ancla no se cancela en el softmax: encarece las dos afirmaciones (`pos`, `neg`) y **abarata la negación** (`na`), porque es trivialmente cierto que un texto no menciona el ánimo *en México* si no menciona México. Empuja masa hacia `na`, hunde `relevancia = 1 − P(na)` bajo el umbral de mudez y dispara la alerta de «dimensión muda» por artefacto de redacción. En la plantilla el ancla es idéntica para las tres etiquetas y se cancela.

- **`IDIOMA_HIPOTESIS` pasa a `"es"`.** Invalida los números de la corrida previa; sigue siendo una sola lengua para todos los grupos, que es lo que el diseño exige.

- **La batería se reacomoda reusando las traducciones existentes.** Los tacos dejan de ser control mudo —son comida, luego `imagen_cultural`— y ascienden a sonda positiva de esa dimensión. La frase de hospitalidad, que se queda sin dimensión, pasa a ser el nuevo control mudo: no habla de ánimo, comida, lugares ni gobierno. Solo hace falta redactar **una** frase nueva en seis idiomas, la sonda positiva de `atmosfera`.

### El corpus

- **Carga de `turistas_traducido.csv` como tercer modo de entrada**, junto a la batería y los textos pegados a mano. El archivo se localiza en el directorio de trabajo, se declara el mapeo de columnas y la procedencia —`id`, `created_at`, `lang`— puebla las columnas que el marco ya tiene reservadas.

- **Comparación a tres vías.** El léxico corre sobre `text` **y** sobre `traducción`; el zero-shot sobre `text`. El emparejamiento de palabras es gratis y **no añade ninguna pasada del modelo NLI** —que es el *large* y el que domina el costo—: siguen siendo 13 por tuit, 34 203 en total. Lo que sí añade es **una pasada del modelo de sentimiento** (base, ~1.1 GB) por tuit, porque `atmosfera` incorpora el sentimiento y hay que calcularlo sobre la traducción, no heredarlo del original. Responde la objeción que un revisor hará seguro —«¿por qué no traduces todo y usas el léxico?»— con el número en la mano en lugar de con un argumento.

- **BREAKING — los grupos de idioma se derivan del corpus, no se declaran.** El notebook asume seis grupos (`en`, `pt`, `fr`, `es_foreign`, `de_nl`, `ar`). El corpus real tiene 23 valores de `lang` y **cero** en alemán, neerlandés y árabe; el español son 12 filas y el portugués y el francés tres cada uno. El 78% es inglés y el **16% es japonés**, un idioma que el diseño nunca contempló. XLM-R-XNLI cubre japonés; el léxico de `analyzer.py` no tiene una sola palabra en japonés, así que 432 tuits son estructuralmente invisibles para el método actual. Eso deja de ser una hipótesis de la batería y pasa a ser un hallazgo sobre el corpus.

- **Los estratos viajan y las figuras los desglosan.** 1 055 de 2 631 filas (40%) vienen de consultas de victimización y 54 de 2 631 son `corpus_type=consolidated`. Promediar violencia sobre un corpus donde cuatro de cada diez tuits se buscaron *por* violencia no es reportable, así que `base` y `corpus_type` entran como columnas y toda figura agregada se desglosa por estrato, con alerta escrita cuando un promedio mezcla intenciones de búsqueda distintas.

- **Robustez de lectura derivada del archivo real:** BOM en la primera columna, `is_retweet` e `is_quote` con mayúsculas inconsistentes (`False` y `FALSE` conviven), 69 filas sin `created_at`, 51 `id` repetidos de 2 631 filas, y seis filas sin traducción. Nada de esto es hipotético: está en el archivo.

- **Exportación de resultados a CSV.** El notebook no escribía ningún archivo de datos: producía figuras y marcos en memoria. Ahora escribe dos, en una carpeta `salida/` propia. El **ancho** trae una fila por tuit con las 52 columnas originales del archivo más 28 de resultados —una por dimensión y método, la relevancia aparte, y las 13 probabilidades crudas— en `utf-8-sig` para que Excel lea los acentos y el japonés. El **largo** trae una fila por texto × método × dimensión, que es la forma con la que se analiza.

- **Muestreo, deduplicación y lotes.** Tope de muestra configurable para cronometrar antes de comprometer el corpus completo, deduplicación por `id`, y evaluación por lotes: hoy `_nli()` llama al pipeline texto por texto, lo cual da igual con 24 textos y no con 2 631.

## Capabilities

### New Capabilities

- `hypothesis-design`: el conjunto de dimensiones medidas, la redacción de sus hipótesis, dónde vive el ancla geográfica y en qué lengua se formulan. Hoy vive implícito en una celda; es el instrumento de medición y merece contrato propio.
- `corpus-csv`: carga del corpus real desde el archivo del proyecto, con mapeo de columnas, procedencia, estratos, columna de entrada seleccionable, muestreo, deduplicación y evaluación por lotes.
- `results-export`: escritura de los resultados a disco en dos formas, con las columnas de origen conservadas y la guardia que impide exportar una magnitud que combine valencia y relevancia.

### Modified Capabilities

Las tres viven en el change `dimension-visualization`, hoy en curso (77/79). Este change las modifica antes de que se archiven.

- `example-corpus`: cambia la composición de la batería —qué frase prueba qué dimensión— y cuál es el control mudo.
- `dimension-results-frame`: cambia el conjunto de claves de dimensión, una dimensión pasa a tener un solo método, el marco gana una tercera vía de comparación (léxico sobre traducción) y debe poblarse desde un CSV con estratos.
- `dimension-visualization`: la demostración entre idiomas cambia de dimensión y deja de asumir seis grupos fijos; las figuras que comparan métodos explican la exclusión de la dimensión que solo tiene uno; las figuras agregadas se desglosan por estrato.

## Impact

**Notebook `rediseno_zeroshot_colab.ipynb`** — celdas a tocar: 3 y 4 (dimensiones e hipótesis), 8 (mapeo del léxico), 10 (lotes), 12 (configuración, `ESCALAS`, umbrales), 13 y 14 (batería y nueva rama de CSV), 15 (`LEX` y la comparación a tres vías), 17 (`SETS_LEXICO`, estratos, procedencia), 18 y 19 (sección 9), 23 (una clave fija y el desglose por estrato), 25 (texto de lectura).

**Intacto:** celdas 0–2, 5–7, 9, 11, 16, 20–22, 24 y 26. Ninguna fórmula de `metodo_actual` ni de `metodo_nuevo` se toca. La celda de figuras ya es genérica —recorre `ESCALAS`, `DIMENSIONES` y `VIOLENCIA`, y deriva los comparables de `len(metodos) == 2`— y su única dependencia fija es la aserción de coherencia con la sección 9.

**Change `dimension-visualization`:** su tarea `10.5` —confirmar que el control mudo da relevancia baja en las tres dimensiones léxicas— queda sin sentido con el control mudo actual, porque los tacos pasan a ser un positivo. Se redefine contra el control mudo nuevo.

**Lo que el corpus NO trae:** las columnas `tipo` y `justificacion` están vacías en las 2 631 filas. No hay codificación humana, así que la validación contra alfa de Krippendorff que pide la sección 12 **sigue pendiente** y este change no la desbloquea. Conviene decirlo en voz alta: el notebook va a producir números sobre 2 631 tuits reales, y eso invita a leerlos como hallazgos validados cuando todavía no lo están.

**Fuera de alcance:** el eje temporal. El corpus trae `created_at` con dos meses de rango, así que por primera vez es posible, pero es un change aparte y meterlo aquí lo desenfoca.

**Convergencia con EvaluadorTweets:** las claves de dimensión quedan en español mientras `analyzer.py` las tiene en inglés. Hace falta una tabla de correspondencia el día que los proyectos se junten; no se resuelve aquí.
