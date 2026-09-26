## Context

Hay dos notebooks y dos mediciones del mismo corpus.

```
 rediseno_zeroshot_colab.ipynb (v1)          rediseno_zeroshot_colab_v2.ipynb (v2)
 ─────────────────────────────────           ─────────────────────────────────────
 hipótesis "trio" (pos/neg/na)                compuerta de relevancia (multi_label=True)
 CORPUS_DF, SALIDA_DIR, exclusión de          + hipótesis reescritas, batería con
   salidas en la autodetección                  control logístico y sonda de frontera
 §13 Descarga de resultados  ◄── la v2 NO la tiene
                    │                                         │
                    └──────────────┬──────────────────────────┘
                                   ▼
                    rediseno_zeroshot_colab_v3.ipynb  (este change)
                                   ▲
                                   │ tweets_calificados_anclada.csv  (2631 × 68)
                                   │   52 columnas del corpus + 16 de rúbrica
 EvaluadorTweets ──────────────────┘ graficas_calificaciones_anclada.html (agregados, sin id)
```

**Lo que ya se sabe del archivo de entrada** (inspección del 13/09):

- 2 631 filas, 2 631 `id` distintos. Los 54 que Excel había redondeado a `2.07E+18` vienen reemplazados por `local:<hash>`, así que la deduplicación por `id` ya no colapsa filas.
- Por criterio, `{slug}_aplicable ∈ {SI, NO, BLOQUEADO}`, `{slug}_nivel` y `{slug}_puntaje` (vacíos cuando no es `SI`) y `{slug}_justificacion`.
- `aplicable` no existe en `rubrica.json`: lo introduce la regla 1 de la instrucción del motor (`evaluador/scoring.py`). En la rúbrica, el nivel 0 es ausencia en los cuatro criterios.
- Presencia (nivel > 0): R1 = 104, R2 = 71, R3 = 25, R4 = 25. Tuits con algún nivel > 0: **144**. Sin ninguno: **2 487** (9 con algún bloqueo). Bloqueos: 8 / 7 / 2.
- `traducción` está completa: 5 filas se llenaron a mano el 13/09 porque Gemini las bloqueó (`PROHIBITED_CONTENT`). El checkpoint de traducción las marca con `detalle`.
- "Contexto incompleto" se reproduce exactamente desde el CSV ancho: `in_reply_to_user_id` no vacío, o texto que empieza con `@`, o `is_retweet`, o `is_quote` → 999 tuits autosuficientes, igual que el tidy.

**Lo que muestra el HTML de EvaluadorTweets** (`evaluador/viz.py` + `plantilla_graficas.html`): volumen diario por idioma; saliencia diaria por criterio (valencia / (valencia + ausencia), sin fallidas en el denominador); serie diaria de valencia apilada por criterio; distribución global y por período; filtros de idioma, autosuficiencia, proporción/absoluto y media móvil de 7 días. Días cortados en `America/Mexico_City`; períodos `[2026-05-31, 2026-06-11)`, `[2026-06-11, 2026-07-06)` y `[2026-07-06, …)`. Ya trata NO_APLICABLE + nivel 0 como ausencia y BLOQUEADO como fallida.

**Restricciones:** se ejecuta en Colab (T4); los archivos se suben a `/content`; las figuras usan Apache ECharts desde el CDN que ya declara la v2 (`CDN_ECHARTS`); el estilo del notebook (comentarios que explican el porqué, validación antes de gastar GPU, rótulos de procedencia) se conserva.

## Goals / Non-Goals

**Goals:**

- Un notebook que primero muestre lo que dice la rúbrica, después mida con el instrumento zero-shot vigente, contraste las dos mediciones, estudie la asociación entre criterios, analice con NLP los tuits sin nivel y los calificados, y exporte todo.
- Una sola codificación de ausencia y faltante, aplicada en todas las secciones.
- Poder iterar las secciones de validación, asociación y NLP sin volver a ejecutar el zero-shot.

**Non-Goals:**

- Corregir el motor de EvaluadorTweets o recalificar el corpus.
- Declarar falsos negativos: el notebook produce **candidatos** para revisión humana.
- Cambiar las hipótesis, la compuerta o las fórmulas del instrumento heredado de la v2.
- Reemplazar la validación contra codificación humana: la rúbrica también es un LLM, así que esto es validez convergente entre dos instrumentos automáticos.
- Modificar la v1 o la v2.

## Decisions

### D1 · Un notebook nuevo que parte de la v2

La v3 copia las celdas de la v2 y **porta** de la v1 la sección de descarga junto con sus tres dependencias, que la v2 perdió: `SALIDA_DIR`/`SALIDA_CSV*`, el global `CORPUS_DF` que guarda el marco de origen y la exclusión de las salidas propias en `_localizar_csv`. La exportación de la v1 se ajusta a las claves crudas de la v2, que añade `_crudo["compuerta"]` y usa pos/neg sin `na` en modo compuerta.

*Alternativa descartada:* dos notebooks, uno de medición y otro de análisis. Separaría bien GPU de CPU, pero el usuario pidió uno, y D3 resuelve lo mismo con un interruptor.

### D2 · Orden de secciones

```
 1  Instalación (v2, ampliada)
 2  Resultados de la rúbrica            CPU   ← nuevo · entradas declaradas aquí
 3–10 Instrumento zero-shot (v2 2–9)    GPU   ← RUTA_CSV, N_MUESTRA, carga previa
 11 Sesgo entre idiomas (v2 10)
 12 Tabla resumen (v2 11)
 13 Figuras del instrumento (v2 12)
 14 Validación convergente              CPU   ← nuevo
 15 Asociación entre criterios          CPU   ← nuevo
 16 Análisis NLP                        GPU opcional (embeddings) ← nuevo
 17 Descarga de resultados              CPU   ← portada de v1, ampliada
 18 Cómo leer esto (v2 13)                    ← ampliada
```

La sección de la rúbrica va inmediatamente después de la instalación y no antes: la celda de instalación puede exigir reiniciar el entorno, y todo lo que se hubiera ejecutado antes se perdería. Es la primera sección de análisis porque es el hallazgo principal y no depende de la GPU. Declara además las **entradas** del notebook (archivo, HTML de contraste, corrida previa), que las secciones siguientes leen. Todas las secciones nuevas leen los marcos `RUBRICA` y `RUBRICA_TUIT` construidos en ella. Las referencias a número de sección heredadas de la v2 se renumeran.

### D3 · Carga de una corrida previa

Nueva opción `CARGAR_ZEROSHOT = None | "ruta/zeroshot_corrida.json.gz"`. Justo después de evaluar, el notebook escribe un **volcado de la corrida**: huella del instrumento, identificadores en orden, la estructura `resultados` completa, el tiempo de corrida y, al exportar, la demostración entre idiomas y el A/B del ancla. Con ruta, no se cargan modelos y la celda de evaluación restaura `resultados` desde el volcado. `construir_frames` sigue siendo el único punto de extracción, así que todas las figuras heredadas funcionan sin cambios. La restauración se valida: si la huella de las hipótesis, compuerta, plantillas y diseño de relevancia no coincide, o si los identificadores no coinciden con los del CSV de entrada, se detiene. Si coinciden como conjunto pero no en orden, se reordena por identificador.

*Alternativas descartadas:* reconstruir desde el CSV ancho, que no guarda las palabras del léxico activadas, las etiquetas de sentimiento, la demostración entre idiomas ni el A/B del ancla, de modo que varias figuras heredadas quedarían vacías. Extraer del HTML de figuras, que no trae `id` (solo texto truncado a 120 caracteres), y ya se vio que la unión por texto pierde filas.

### D4 · Codificación de la rúbrica: un solo marco

Se construye `RUBRICA` con una fila por tuit × criterio:

| aplicable | nivel en CSV | `clase` | `nivel_num` |
|---|---|---|---|
| NO | vacío | `ausencia` | 0 |
| SI | 0 | `ausencia` | 0 |
| SI | 1–5 | `valencia` (R1–R3) o `presencia` (R4) | 1–5 |
| BLOQUEADO | vacío | `faltante` | NaN |

Además, `presente = nivel_num > 0`, y a nivel tuit `calificado = any(presente)` con `faltante` que no cuenta como presente ni como ausente. Se guarda también `origen_ausencia ∈ {aplicable_no, nivel_0}` para poder informar la colisión (R1 = 3 y R4 = 79 ceros explícitos) sin que afecte los cálculos.

La escala se **tipa por criterio**: R1–R3 son `valencia` (1 muy negativo … 5 muy positivo; paleta divergente, 3 en gris) y R4 es `presencia` (solo 1; color propio, no el rojo de "muy negativo"). Esto corrige un detalle del HTML original, que pinta el nivel 1 de R4 con el primer color de la paleta divergente y muestra su "distribución de valencia" como 100% de un solo nivel.

### D5 · La sección 0 replica el HTML en el estilo de la v2

Se recalculan los mismos agregados desde `RUBRICA` + columnas del corpus (fecha local, idioma, período, autosuficiencia) y se dibujan con ECharts en el HTML de figuras del notebook, con los mismos cuatro controles. Se comprueba contra el HTML original: si `graficas_calificaciones_anclada.html` está en el directorio de trabajo, se extrae su bloque de datos y se compara el conteo por criterio × clase × nivel. Una diferencia se informa como error de réplica. Opcionalmente, el HTML original se muestra incrustado.

*Alternativa descartada:* solo incrustar el HTML. No permite unir por `id` ni reutilizar los agregados.

### D6 · Validación convergente: qué se compara con qué

| rúbrica | zero-shot | figura | métricas |
|---|---|---|---|
| R1 atmósfera | `atmosfera` + `_relevancia` | plano | AUC(relevancia → presente), ρ Spearman(nivel 1–5, valencia) |
| R2 imagen cultural | `imagen_cultural` + `_relevancia` | plano | ídem |
| R3 perspectiva política | `perspectiva_politica` + `_relevancia` | plano | ídem |
| R4 violencia | `violence_salience` | ROC + cajas por nivel | AUC(salience → presente) |

**Plano**: nube de fondo con los tuits en ausencia (gris, sin interacción masiva: se agrega en celdas si hace falta), niveles 1–5 superpuestos en paleta divergente, línea vertical en `UMBRAL_RELEVANCIA`, y panel lateral con la distribución de relevancia por nivel (cajas). Cada métrica lleva IC bootstrap (1 000 remuestreos, semilla fija) y su `n` por nivel. Cada dimensión incluye una nota de constructo **declarada en código** (`CONSTRUCTO`), no inferida: R1 mide afecto hacia México y su gente, y la compuerta mide el ánimo vivido; R3 incluye infraestructura, logística y gestión de seguridad, y la compuerta solo autoridades y gobierno. Así un AUC bajo se lee con su causa probable al lado.

*Alternativa descartada:* kappa entre niveles de rúbrica y zero-shot discretizado. Exige elegir cortes sobre la valencia continua, justo el tipo de umbral que el notebook pide no inventar.

### D7 · Asociación entre criterios: Fisher, no chi cuadrada

Presencia binaria por criterio, sin tuits con faltante en el par. Para cada uno de los 6 pares:

- tabla 2×2, esperados, Fisher exacta bilateral, **Holm** sobre las 6;
- φ y razón de momios con IC (Haldane-Anscombe +0.5 cuando hay ceros);
- chi cuadrada **solo como columna de referencia**, con la marca de que todas las tablas tienen esperados < 5.

Tres lecturas, en tablas y en un heatmap de φ:

1. corpus completo (n = 2 621);
2. solo calificados (n = 144), con advertencia de **sesgo de Berkson**: condicionar a "algún criterio presente" induce asociación negativa artificial;
3. estratificada por `base` en dos estratos (consultas de victimización: 1 079; resto), con **Mantel–Haenszel** (OR común + prueba de homogeneidad de Breslow–Day, vía `statsmodels`).

Se documenta que R3 × R4 (φ ≈ 0.57) está en parte **definido por la rúbrica**, porque R3 incluye "gestión de seguridad".

### D8 · NLP: embeddings sobre el original, spaCy sobre la traducción

```
 texto original ── limpieza mínima ──▶ sentence-transformers ──▶ UMAP(2D figura, 10D cluster) ──▶ HDBSCAN
 (URLs→token, @→token)                 paraphrase-multilingual-                                       │
                                        mpnet-base-v2                                                 ▼
 traducción ──▶ spaCy es_core_news_lg + EntityRuler(MEXICO) ──┬─ lemas NOUN/PROPN/ADJ ──▶ c-TF-IDF ─▶ tópico por cluster
                                                              ├─ entidades ──▶ co-ocurrencia + PMI ─▶ grafo de entidades
                                                              └─ dependencias ──▶ (suj, verbo, obj) con entidad ─▶ grafo de relaciones
```

- **Por qué embeddings sobre el original:** la geometría de los grupos no depende de la calidad de la traducción automática, y el modelo multilingüe pone en el mismo espacio el inglés y el japonés.
- **Por qué spaCy sobre la traducción:** un solo vocabulario y un solo NER para los 2 631 tuits, así cada entidad es un solo nodo del grafo sin importar el idioma del tuit.
- **`EntityRuler` antes del NER estadístico** con un diccionario `MEXICO` declarado en el notebook (país, gentilicios, estados y ciudades sede, estadios, instituciones, figuras políticas, marcas de violencia). El NER español de 4 etiquetas es débil en tuits, y el diccionario es además la señal de "menciona México" que usan los candidatos a falso negativo (D10).
- Se descartan tuits sin texto útil (solo URL, `qme`/`zxx`) y se informan.
- **Un solo ajuste para los 2 631** (embeddings, UMAP, HDBSCAN, c-TF-IDF): calificados y resto comparten el espacio, así que los clusters de uno y otro son comparables. Los 144 no se agrupan por separado porque con esa `n` los grupos no son estables. Se leen como capa de color y con **log-odds con prior informativo** (Monroe et al.) de lemas y entidades, calificados frente a resto.
- `min_cluster_size` y `n_neighbors` son parámetros visibles. Se informa la proporción de ruido de HDBSCAN (-1) en vez de forzar cada tuit a un grupo.

*Alternativas descartadas:* vectores de spaCy (promedio de palabras, pobres en textos de 100 caracteres); spaCy `en` + `ja` sobre el original (dos grafos sin entidades comunes); KMeans (obliga a elegir k y asigna el ruido a algún grupo).

### D9 · Grafos legibles

- **Entidades:** nodo = entidad normalizada (lema + etiqueta), tamaño = frecuencia, categoría = etiqueta. Arista = co-ocurrencia en el mismo tuit, con peso PMI y un mínimo de co-ocurrencias. Se muestran los `TOP_NODOS` (80 por defecto). ECharts `graph` con layout `force` y filtro por grupo (calificados / resto / todos).
- **Relaciones:** tripletas (sujeto, lema del verbo, objeto) donde al menos un extremo es entidad. La arista lleva el verbo como etiqueta y se muestra con umbral de frecuencia. Se declara que el análisis de dependencias sobre traducciones de tuits es ruidoso: es exploratorio.

### D10 · Tres lecturas analíticas

1. **Auditoría de la colecta:** tabla y treemap (o sankey) de cluster × `base` × período, con los tópicos de cada cluster y ejemplos. Responde qué consulta trajo qué ruido.
2. **Candidatos a falso negativo:** tuits no calificados que **mencionan México** (EntityRuler) **y** superan `UMBRAL_RELEVANCIA` en alguna dimensión zero-shot **o** superan `UMBRAL_SALIENCE_FN` (declarado, 0.5 por defecto) en `violence_salience`. Se exportan con texto, traducción, justificaciones de la rúbrica, valores zero-shot, cluster y motivo. No se reportan como tasa de error.
3. **Temas fuera de la rúbrica:** clusters donde la mención de México es alta y la tasa de calificados es baja. Se listan como candidatos a dimensión con sus tópicos y ejemplos.

### D11 · Exportación

La sección 16 escribe en `salida/`:

- `resultados_enriquecidos.csv`: las 68 columnas originales + zero-shot + probabilidades crudas + `rubrica_*_clase`/`_nivel_num` + `calificado` + `cluster`, `topico`, `menciona_mexico`, `candidato_fn`, `motivo_fn`, `umap_x`, `umap_y`.
- `resultados_largo.csv`, como en la v1.
- `candidatos_fn.csv`.
- `asociacion_criterios.csv`: las tres lecturas.
- `figuras_v3.html`, autocontenido, con las secciones nuevas; las figuras del instrumento siguen en `figuras_dimensiones.html`.
- `zeroshot_corrida.json.gz`: el volcado que lee `CARGAR_ZEROSHOT` (D3).

Se escribe en `utf-8-sig` y se une por `id`. El archivo ancho lleva también la huella del instrumento como columna, para que un CSV suelto diga con qué hipótesis se produjo.

### D12 · Dependencias fijadas

Se instalan con versión mínima en la celda de instalación y solo si faltan: `spacy>=3.7,<4` + `es_core_news_lg`, `sentence-transformers`, `umap-learn`, `hdbscan` (con respaldo a `sklearn.cluster.HDBSCAN`), `statsmodels`, `scikit-learn`. Se conserva la regla de la v2 de `transformers<5`, y se comprueba que `sentence-transformers` no la rompa.

## Risks / Trade-offs

- **[Los 144 no alcanzan para varias métricas]** R3 y R4 tienen 25 presentes, y los niveles sueltos tienen n = 1–4. → Toda métrica lleva `n` e IC; ninguna figura oculta un nivel escaso, lo marca.
- **[El sesgo de la consulta se confunde con asociación y con validez]** 1 079 tuits vienen de consultas de victimización. → Mantel–Haenszel en D7 y desglose por estrato en la auditoría.
- **[La traducción introduce errores en tópicos y entidades]** → Los clusters no dependen de ella (D8). Se declara el uso nuevo de la traducción y las 5 traducciones manuales.
- **[Grafos ilegibles]** → `TOP_NODOS`, mínimo de co-ocurrencia y umbral de PMI visibles como parámetros.
- **[UMAP/HDBSCAN no deterministas]** → Semilla fija, y parámetros y versiones en la ficha técnica.
- **[Conflictos de dependencias en Colab]** Los modelos suman memoria: `sentence-transformers` puede arrastrar una versión de `transformers` ≥ 5, y `es_core_news_lg` pesa ~560 MB. → Se verifica la versión tras instalar y se reinicia si hace falta, como ya hace la v2. Los embeddings se calculan en lotes y se liberan los pipelines NLI antes de la sección 15 si no hay memoria.
- **[Comparar rúbrica contra zero-shot suena a "validar" y no lo es]** → El rótulo de procedencia pasa a decir "contrastado contra rúbrica LLM, NO contra codificación humana".
- **[Candidatos a falso negativo leídos como tasa de error]** → El archivo y la figura dicen "candidatos para revisión manual" y no calculan precisión ni recall.
- **[Deriva frente al HTML original]** → Comparación automática de conteos en D5.

## Migration Plan

No hay despliegue. La v1 y la v2 se conservan como referencia reproducible de sus corridas. Flujo de uso:

1. Primera ejecución en Colab con GPU: se suben el CSV y el HTML, se ejecuta todo y se descarga `salida/`.
2. Iteraciones de NLP: `CARGAR_ZEROSHOT = "/content/salida/resultados_enriquecidos.csv"`. Sin GPU salvo para los embeddings, que también pueden correr en CPU con ~2 631 textos cortos.

## Open Questions

- ¿Estratos de `base` para Mantel–Haenszel en dos grupos (victimización / resto) o por consulta individual? Por defecto dos; las consultas pequeñas dejarían estratos con celdas vacías.
- ¿El diccionario `MEXICO` requiere revisión del usuario antes de usarse para candidatos a falso negativo? Se entrega como celda editable con la lista inicial.
- ¿`UMBRAL_SALIENCE_FN` = 0.5 es razonable? Se calibra mirando la ROC de R4 **antes** de listar candidatos, y se congela.
