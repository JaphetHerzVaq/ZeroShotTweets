## Why

El corpus ya tiene una segunda medición independiente: EvaluadorTweets calificó los 2 631 tuits con la rúbrica de imagen de país (Gemini, cuatro criterios aislados) y dejó el resultado en `tweets_calificados_anclada.csv`. Hasta ahora el notebook zero-shot se leía como «descriptivo, NO validado» porque no había contra qué contrastarlo. Ahora lo hay, y una vista previa sobre la corrida del 11/09 ya muestra que el contraste cambia conclusiones: `atmosfera` separa bien (AUC 0.70, nivel ordena valencia con ρ = 0.64) pero es **ciega al nivel 1** —hostilidad hacia México da relevancia ≈ 0.07—; `imagen_cultural` separa pero no ordena; `perspectiva_politica` rinde **peor que el azar (AUC 0.42)** porque mide un constructo más estrecho que la rúbrica.

Además, 2 487 tuits no obtuvieron ningún nivel > 0. Son el 95% del corpus y nadie ha mirado qué son: ruido de las consultas, falsos negativos de la rúbrica o temas que la rúbrica no contempla. Y la v2 del notebook, que tiene el instrumento vigente (compuerta de relevancia), **perdió la sección de descarga de resultados** que sí tenía la v1.

## What Changes

- **Nuevo notebook único `rediseno_zeroshot_colab_v3.ipynb`**, derivado de la v2. La v1 y la v2 quedan intactas.
- **Sección inicial de resultados de la rúbrica, sin GPU.** Recalcula desde el CSV los agregados de `graficas_calificaciones_anclada.html` —volumen diario, saliencia por criterio, valencia en todo el corpus y por período— con la zona horaria y los tres períodos de EvaluadorTweets, y opcionalmente muestra el HTML original si está en el directorio de trabajo.
- **Codificación única de la ausencia.** El nivel 0 de la rúbrica es ausencia en los cuatro criterios; `aplicable = NO` es una segunda codificación del mismo caso introducida por el motor de calificación y se trata como nivel 0. `BLOQUEADO` es dato faltante, nunca ausencia ni nivel bajo.
- **Entrada del instrumento:** `tweets_calificados_anclada.csv` (los 54 identificadores que Excel había redondeado ya vienen reparados), corpus completo por defecto y unión con la rúbrica por identificador. Se añade la opción de **cargar una corrida zero-shot previa** en lugar de volver a ejecutar el modelo.
- **Validación convergente zero-shot contra rúbrica:** plano relevancia–valencia con el nivel 0 como fondo y los niveles 1–5 superpuestos en paleta divergente, distribución de relevancia por nivel, AUC por dimensión, correlación nivel–valencia y curva ROC de saliencia de violencia, con el desajuste de constructo declarado por dimensión.
- **Asociación entre criterios:** presencia = nivel > 0; prueba exacta de Fisher con corrección por comparaciones múltiples, φ y razón de momios con intervalo, lectura sobre el corpus completo y sobre los calificados (con advertencia de sesgo por condicionamiento), y estratificación por consulta de victimización. La chi cuadrada se reporta solo como referencia porque todas las tablas tienen esperados < 5.
- **Análisis NLP del corpus**, sobre dos grupos definidos por la rúbrica —calificados (algún nivel > 0, 144) y resto (2 487)— en un espacio común: agrupamiento por embeddings multilingües del texto original, tópicos por lemas de spaCy sobre la traducción, entidades con un diccionario de México, grafo de co-ocurrencia de entidades y grafo de relaciones sujeto–verbo–objeto, todo en Apache ECharts. Tres salidas analíticas: auditoría de la colecta, **candidatos** a falso negativo para revisión manual y temas fuera de la rúbrica.
- **Descarga de resultados restaurada** desde la v1 y ampliada con las columnas de validación y NLP, más un archivo de candidatos a falso negativo.

## Capabilities

### New Capabilities

- `rubric-results`: carga de las calificaciones de EvaluadorTweets, codificación única de ausencia y faltante, derivación de los grupos y reproducción de los agregados del HTML de calificaciones por período.
- `convergent-validation`: contraste de las magnitudes zero-shot contra los niveles de la rúbrica, con figuras y métricas por dimensión y el desajuste de constructo declarado.
- `criterion-association`: asociación entre la presencia de los cuatro criterios con pruebas exactas, tamaño de efecto, corrección múltiple y estratificación.
- `corpus-nlp`: agrupamiento, tópicos, entidades, grafos y las tres lecturas analíticas (auditoría, candidatos a falso negativo, temas nuevos) sobre los dos grupos.

### Modified Capabilities

Ambas viven en el change `dimensiones-mexico-y-csv`, hoy en curso (81/93), y todavía no están archivadas.

- `corpus-csv`: la entrada pasa a ser el CSV calificado, cuyas columnas de rúbrica deben viajar sin interferir con el mapeo, y se añade la carga de una corrida zero-shot previa.
- `results-export`: la exportación incorpora las columnas de validación y NLP y un tercer archivo de candidatos a falso negativo.

## Impact

**Notebook:** nuevo `rediseno_zeroshot_colab_v3.ipynb`. Parte de las celdas de la v2 (instrumento, carga, marcos, figuras) y recupera la sección 13 de la v1 (descarga). Añade cuatro secciones nuevas.

**Dependencias nuevas en Colab:** `spacy` con `es_core_news_lg` (~560 MB), `sentence-transformers` con un modelo multilingüe, `umap-learn`, `hdbscan` (o el de `scikit-learn` ≥ 1.3), `scipy` y `statsmodels` para las pruebas. Apache ECharts sigue viniendo del CDN que ya usa el notebook.

**Costo:** el zero-shot completo tarda ~11 min en una T4 (621 s medidos para 2 562 textos); los embeddings y spaCy añaden unos minutos. La carga de una corrida previa permite iterar el NLP sin volver a pagar la GPU.

**Datos de entrada:** `tweets_calificados_anclada.csv` (con las 5 traducciones completadas a mano el 13/09, que se declaran como tales) y, opcional, `graficas_calificaciones_anclada.html`.

**Tesis:** usar la traducción al español como entrada de NLP es un uso nuevo —EvaluadorTweets la produjo como apoyo para lectura humana— y debe declararse, igual que las 5 traducciones hechas por otro modelo. Los candidatos a falso negativo no son falsos negativos hasta que una persona los revise.

**Fuera de alcance:** corregir la colisión `aplicable`/nivel 0 en el motor de EvaluadorTweets (change `anclar-semantica-de-ausencia` de ese repositorio) y volver a calificar.
