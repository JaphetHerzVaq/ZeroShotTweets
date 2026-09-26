## 1. Base del notebook v3

- [x] 1.1 Crear `rediseno_zeroshot_colab_v3.ipynb` como copia de la v2, sin salidas, y actualizar la portada: qué cambia respecto de la v2, entradas esperadas en `/content` y orden de secciones
- [x] 1.2 Portar de la v1 la configuración de salida (`SALIDA_DIR`, nombres de archivo), el global `CORPUS_DF` en la carga del corpus y la exclusión de las salidas propias en la autodetección
- [x] 1.3 Configurar `RUTA_CSV = "/content/tweets_calificados_anclada.csv"` y `N_MUESTRA = None`, y verificar que el mapeo de columnas valida contra los 68 encabezados del archivo
- [x] 1.4 Confirmar que la deduplicación por `id` conserva las 2 631 filas y que los identificadores `local:` se tratan como texto
- [x] 1.5 Ampliar la celda de instalación con spaCy, `es_core_news_lg`, `sentence-transformers`, `umap-learn`, `hdbscan` (con respaldo a scikit-learn) y `statsmodels`, instalando solo lo que falte y verificando después que `transformers` sigue en 4.x
- [x] 1.6 Renumerar las secciones según el diseño y actualizar las referencias cruzadas entre secciones en textos y comentarios

## 2. Sección 2 · Resultados de la rúbrica

- [x] 2.1 Detectar los criterios desde los nombres de columna del archivo y omitir la sección y sus dependientes con aviso si no hay columnas de rúbrica
- [x] 2.2 Construir el marco `RUBRICA` (tuit × criterio) con la codificación única: NO y nivel 0 → ausencia con nivel 0, BLOQUEADO → faltante, 1–5 → valencia o presencia, y guardar el origen de la ausencia
- [x] 2.3 Declarar el tipo de escala por criterio (valencia R1–R3, presencia R4) con sus paletas, sin reutilizar para R4 un color de valencia negativa
- [x] 2.4 Informar por criterio los conteos de ausencia (desglosados por origen), valencia o presencia, y faltante
- [x] 2.5 Definir el grupo calificado (algún nivel > 0) y verificar 144 calificados, 2 487 no calificados y 9 no calificados con bloqueo
- [x] 2.6 Derivar la fecha local en `America/Mexico_City`, el período con los tres cortes declarados, el idioma con la categoría sin idioma y la autosuficiencia, y verificar 999 tuits autosuficientes
- [x] 2.7 Calcular los agregados por día, criterio, clase, nivel, idioma y autosuficiencia, y el volumen diario por idioma
- [x] 2.8 Dibujar con ECharts el volumen diario, la saliencia diaria, la serie de valencia por criterio y la distribución global y por período, con filtros de idioma y autosuficiencia, proporción/absoluto y media móvil de 7 días
- [x] 2.9 Extraer los datos embebidos de `graficas_calificaciones_anclada.html` cuando exista, comparar conteos por criterio × clase × nivel e informar coincidencia o cada diferencia
- [x] 2.10 Mostrar opcionalmente el HTML original incrustado cuando esté disponible

## 3. Carga de una corrida zero-shot previa

- [x] 3.1 Añadir `CARGAR_ZEROSHOT` a la configuración y documentar su uso para iterar sin GPU
- [x] 3.2 Calcular una huella de las hipótesis, compuerta, plantillas y diseño de relevancia, y guardarla en la ficha técnica
- [x] 3.3 Escribir el volcado `zeroshot_corrida.json.gz` tras evaluar e implementar la restauración de `resultados` desde él, saltando la carga y ejecución de modelos (y la demostración y el A/B del ancla, que se restauran del volcado)
- [x] 3.4 Detener la ejecución si la huella o los identificadores no coinciden, indicando qué difiere y cuántos faltan en cada lado
- [ ] 3.5 Verificar con una corrida real que los valores reconstruidos coinciden con los exportados y que las figuras del instrumento resultan iguales

## 4. Validación convergente

- [x] 4.1 Declarar la tabla de correspondencia criterio → dimensión zero-shot → magnitud, con la nota de constructo de cada lado, y mostrarla al inicio de la sección
- [x] 4.2 Unir valores zero-shot y rúbrica por `id`, informando filas unidas y sin contraparte, sin unir por texto
- [x] 4.3 Dibujar para R1–R3 el plano relevancia–valencia con la ausencia de fondo, niveles 1–5 superpuestos como series propias y el umbral de relevancia marcado
- [x] 4.4 Añadir a cada plano la distribución de relevancia por nivel, con n y advertencia de muestra insuficiente
- [x] 4.5 Calcular el AUC de relevancia → presente y el ρ de Spearman nivel–valencia, con IC bootstrap de semilla fija y tamaños de muestra
- [x] 4.6 Señalar por escrito los criterios cuyo IC del AUC incluye 0.5 o queda por debajo, junto a su nota de constructo
- [x] 4.7 Dibujar la curva ROC de R4 contra `violence_salience` con AUC e IC, y la distribución de prominencia por clase
- [x] 4.8 Rotular toda la sección como contraste contra una rúbrica aplicada por un LLM, no contra codificación humana

## 5. Asociación entre criterios

- [x] 5.1 Construir las seis tablas 2×2 de presencia con esperados y número de excluidos por faltante
- [x] 5.2 Calcular la prueba exacta de Fisher bilateral con corrección de Holm, y la chi cuadrada solo como referencia, marcada cuando algún esperado es < 5
- [x] 5.3 Calcular φ y la razón de momios con IC, aplicando y declarando la corrección de Haldane–Anscombe en tablas con ceros
- [x] 5.4 Producir la lectura sobre el corpus completo, con la advertencia de inflación por los tuits sin ningún criterio presente
- [x] 5.5 Producir la lectura sobre los calificados, con la advertencia de sesgo de Berkson
- [x] 5.6 Declarar la regla de estratos por `base` (victimización / resto), informar su tamaño y calcular la OR de Mantel–Haenszel con la prueba de homogeneidad
- [x] 5.7 Dibujar la matriz de φ con el valor en cada celda para las tres lecturas
- [x] 5.8 Añadir la nota de traslape definicional al par perspectiva política × saliencia de violencia

## 6. NLP · preparación y agrupamiento

- [x] 6.1 Definir y aplicar la limpieza mínima (URLs y menciones a marcadores) y excluir tuits sin texto útil, informando el número por grupo
- [x] 6.2 Calcular embeddings multilingües sobre el texto original, por lotes y con GPU si está disponible
- [x] 6.3 Reducir con UMAP (una proyección 2D para la figura y otra de más dimensiones para agrupar) con semilla fija
- [x] 6.4 Agrupar con HDBSCAN con parámetros visibles e informar número de clusters, tamaños y proporción de ruido por grupo
- [x] 6.5 Dibujar el mapa 2D con ECharts, coloreado por cluster y con capa o filtro de calificados, y tooltip con texto original y traducción
- [x] 6.6 Registrar semilla, parámetros, modelos y versiones en la ficha técnica

## 7. NLP · spaCy, tópicos y grafos

- [x] 7.1 Declarar en una celda editable el diccionario `MEXICO` con sus categorías (país y gentilicios, estados y ciudades sede, estadios, instituciones, figuras políticas, crimen organizado)
- [x] 7.2 Construir el pipeline `es_core_news_lg` con `EntityRuler` antes del NER, procesar la traducción por lotes e informar cuántos tuits mencionan México por grupo
- [x] 7.3 Declarar en la sección el uso de la traducción automática y las cinco traducciones completadas a mano
- [x] 7.4 Calcular los tópicos por cluster con c-TF-IDF sobre lemas de sustantivos, nombres propios y adjetivos, y mostrar por cluster tamaño, proporción de calificados, términos y ejemplos
- [x] 7.5 Construir el grafo de co-ocurrencia de entidades normalizadas con PMI, `TOP_NODOS` y co-ocurrencia mínima, y dibujarlo con layout force y filtro por grupo
- [x] 7.6 Extraer tripletas sujeto–verbo–objeto con al menos una entidad y frecuencia mínima, y dibujar el grafo dirigido con el verbo como etiqueta y la advertencia de carácter exploratorio
- [x] 7.7 Calcular log-odds con prior informativo de lemas y entidades entre calificados y no calificados, y mostrar los términos característicos de cada grupo

## 8. NLP · lecturas analíticas

- [x] 8.1 Construir la auditoría de la colecta: figura y tabla de cluster × consulta × período con la proporción de calificados por cluster
- [x] 8.2 Declarar `UMBRAL_SALIENCE_FN` en la configuración, revisar la ROC de R4 y congelarlo antes de listar candidatos
- [x] 8.3 Listar candidatos a falso negativo (no calificado + menciona México + relevancia ≥ umbral en alguna dimensión o prominencia ≥ umbral) con motivo, valores, justificaciones y cluster, sin calcular tasas de error
- [x] 8.4 Declarar los umbrales de temas fuera de la rúbrica y listar los clusters con alta mención de México y baja proporción de calificados, con descripción y ejemplos

## 9. Descarga de resultados

- [x] 9.1 Portar la sección de descarga de la v1 adaptándola a las claves crudas de la v2, incluidas las probabilidades de la compuerta
- [x] 9.2 Añadir al archivo ancho la clase y el nivel numérico por criterio, el grupo, cluster, tópico, mención de México, coordenadas UMAP, candidato a falso negativo y motivo
- [x] 9.3 Completar el volcado de la corrida con la demostración entre idiomas y el A/B del ancla, y añadir la huella del instrumento como columna del archivo ancho
- [x] 9.4 Escribir `candidatos_fn.csv` con columna vacía para la decisión del revisor, sin escribir un archivo vacío si no hay candidatos
- [x] 9.5 Escribir `asociacion_criterios.csv` con una fila por par y lectura
- [x] 9.6 Incluir las secciones nuevas en el HTML de figuras exportado y verificar que abre sin el notebook
- [x] 9.7 Mantener la guardia contra columnas que combinen valencia y relevancia, la codificación `utf-8-sig` y la oferta de descarga

## 10. Lectura y verificación final

- [x] 10.1 Ampliar "Cómo leer esto" con la codificación de ausencia, el alcance de la validación entre instrumentos automáticos, el sesgo de Berkson, el traslape R3/R4 y el carácter de candidatos de los falsos negativos
- [x] 10.2 Actualizar el rótulo de procedencia del corpus para indicar que hay contraste contra la rúbrica LLM y que la validación humana sigue pendiente
- [ ] 10.3 Ejecutar la v3 completa en Colab con GPU sobre los 2 631 tuits y registrar el tiempo de cada sección
- [x] 10.4 Verificar que los conteos de la sección 0 coinciden con el HTML original
- [ ] 10.5 Confirmar que los AUC y ρ de la corrida nueva son coherentes con la vista previa (atmósfera ≈ 0.70, imagen ≈ 0.71, política ≈ 0.42) y documentar cualquier diferencia
- [x] 10.6 Ejecutar de nuevo con `CARGAR_ZEROSHOT` apuntando a la exportación y confirmar resultados idénticos sin cargar el modelo NLI
- [x] 10.7 Ejecutar dos veces consecutivas en el mismo directorio y confirmar que las salidas no interfieren con la entrada
