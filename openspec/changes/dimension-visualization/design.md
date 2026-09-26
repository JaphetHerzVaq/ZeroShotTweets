## Context

El notebook termina hoy en texto alineado con `str.format`. Sus datos, al final de una corrida:

```
resultados = [(a, n), ...]     una tupla por tuit

a = metodo_actual(texto)       n = metodo_nuevo(texto, rt, lk)
  overall_sentiment              overall_sentiment
  hospitality                    hospitality        + hospitality_relevancia
  atmosphere                     atmosphere         + atmosphere_relevancia
  governance_trust               governance_trust   + governance_trust_relevancia
  _label                         violence_salience
  _palabras{dim: [str]}          safety_perceived
                                 engagement_weight
                                 _crudo{grupo: {etiqueta: prob}}
```

La celda 17 aplana esto en una tabla de cuatro columnas y descarta todo lo demás: las probabilidades crudas, la violencia, la seguridad, el sentimiento y el peso de engagement. Es la mitad de lo que hay que graficar.

Dos restricciones que condicionan el diseño, ambas decididas con el usuario:

- **Los proyectos convergen.** ZeroShotTweets acabará calificando el mismo corpus de turistas que EvaluadorTweets. La capa de figuras debe poder recibir ese corpus sin rehacerse, aunque hoy la entrada sea una lista de textos sin fechas.
- **El destino es la tesis**, no el taller. Las figuras se imprimen, se citan y tienen que sobrevivir a la escala de grises y al cierre del notebook.

Y una restricción de escala que no se puede maquillar: el corpus de ejemplo son 24 textos. Es una **batería de prueba del instrumento**, no una muestra de nada.

## Goals / Non-Goals

**Goals:**

- Hacer visible el argumento de la sección 7: el instrumento actual varía con el idioma cuando el contenido no varía.
- Hacer visible la distinción que el rediseño introduce: `score` y `relevancia` como ejes separados, y por tanto el cero de hoy como dos cosas distintas.
- Que el notebook corra de principio a fin y produzca figuras sin que el usuario aporte datos.
- Que cada figura lleve su `n`, su umbral y su alerta escrita, en vez de dejar la conclusión al ojo.
- Que cada figura salga como vector para imprimir y que el conjunto sobreviva como archivo independiente.

**Non-Goals:**

- **Validar el rediseño.** La sección 9 del notebook pide ~200 tuits codificados a mano y alfa de Krippendorff contra umbral 0.67. Las figuras describen; no concluyen.
- Inferencia estadística: sin pruebas de hipótesis ni intervalos de confianza sobre 24 textos.
- Eje temporal, períodos y media móvil. No hay fechas mientras la entrada sea una lista de textos.
- Cambiar el método de medición. Ninguna fórmula de `metodo_actual` ni de `metodo_nuevo` se toca; graficar un instrumento no es ajustarlo.
- Sustituir el corpus real. La batería de ejemplo es el modo por defecto, no el modo único.

## Decisions

### 1. Un punto de extracción, tres formas

El proposal habla de "frame tidy único". Precisión: lo único es el **punto de extracción**, no la forma. Una función `construir_frames(resultados, textos)` recorre `resultados` una sola vez y devuelve tres marcos con claves limpias:

```
LARGO    (texto_id, metodo, dimension)  -> score, relevancia, escala
PROBS    (texto_id, grupo, etiqueta)    -> probabilidad
LEXICO   (texto_id, dimension, palabra) -> polaridad, es_subcadena
```

**Alternativa considerada**: un solo marco atómico `(texto_id, metodo, dimension, magnitud) -> valor`, con `magnitud` entre `score`, `relevancia`, `p_pos`, `p_neg`, etcétera.

Se descartó porque fuerza nulos estructurales: `relevancia` no existe para el método actual, las probabilidades crudas cuelgan del **grupo de llamada NLI** y no de la dimensión reportada, y las palabras del léxico no tienen equivalente en el rediseño. Tres claves distintas quieren tres marcos. Forzar uno solo cambia nulos por abstracción y no ahorra nada: la serialización a ECharts agrega por figura de todos modos.

La distinción entre `grupo` y `dimension` es real y hay que sostenerla: `violence_salience` y `safety_perceived` son **dos dimensiones que salen de una sola llamada NLI** de cuatro etiquetas. Colapsarlas haría que el conteo de llamadas y el de dimensiones no cuadre, que es de donde salen las 13 pasadas por tuit.

### 2. `score` y `relevancia` no se multiplican nunca

**Alternativa considerada**: un solo número, `score` por `relevancia`, "valencia ponderada por confianza". Es tentador porque simplifica toda figura a un eje.

Se descarta, y es la decisión más importante del change. Ese producto **reconstruye exactamente el defecto que el rediseño elimina**:

```
  tuit que habló y juzgó neutro    score = 0.02 · relevancia = 0.91  ->  0.018
  tuit que no habló del tema       score = 0.60 · relevancia = 0.03  ->  0.018
                                                                        =====
                                                    el mismo número otra vez
```

Es el `0.0000` ambiguo de `analyzer.py` con otro nombre. Ninguna figura, ningún resumen y ninguna columna exportada combina los dos ejes en un escalar.

Esta es la misma decisión que EvaluadorTweets tomó en su design `scoring-visualization` sección 5b para el nivel `0` de su rúbrica, con una diferencia que conviene dejar escrita porque es un argumento a favor del rediseño: allá la ausencia está **dentro** de la escala y codificada dos veces —como nivel `0` y como `aplicable=false`—, de modo que, en palabras de ese documento, "el modelo se repartirá entre ambas de forma impredecible". Aquí la ausencia es un eje propio, continuo, medido por construcción con la tercera hipótesis.

### 3. La zona muda se marca, no se filtra

**Alternativa considerada**: excluir de las figuras las filas con `relevancia` por debajo de `UMBRAL_MUDEZ`, como EvaluadorTweets excluye su nivel `0` de las series.

Aquí no aplica igual, y la diferencia es el tipo de dato. Allá la ausencia es una **categoría**: apilarla junto a los niveles la colocaría en el extremo "muy negativo", así que hay que sacarla. Aquí la ausencia es un **eje continuo**: se puede dibujar, y dibujarla *es* la evidencia. Filtrarla borraría el hallazgo.

Regla: toda figura que muestre `score` marca la banda de mudez y reporta cuántos puntos caen dentro. Ninguna la oculta. El umbral es un corte de lectura, no un filtro de datos.

**Consecuencia sobre el umbral**: `UMBRAL_MUDEZ` es arbitrario y no debe esconderse. Va en la configuración con un valor por defecto de `0.30`, y la figura de ausencia muestra la **distribución completa** de `relevancia`, de modo que el lector vea qué tan sensible es la lectura al corte elegido. En la tesis el corte se justifica o se somete a análisis de sensibilidad; no se hereda de aquí.

### 4. ECharts por CDN con renderizador SVG

Adoptar la arquitectura de `scoring-visualization` —configuración armada como diccionario de Python, serializada con `json.dumps`, inyectada con `IPython.display.HTML`, ECharts cargado por CDN, sin `pyecharts`— aunque hoy no haya volumen ni filtros que la exijan. Lo justifica la decisión de convergencia: cuando llegue el corpus, el eje temporal y el filtro por idioma se enchufan sobre la misma capa.

**Alternativa considerada**: matplotlib estático. Es más simple hoy, es nativo de la tesis y no depende de red. Se descarta por dos razones, una estratégica y otra técnica:

- Estratégica: obliga a reescribir la capa entera cuando llegue el corpus, que es precisamente lo que la decisión de convergencia quiere evitar.
- Técnica, y es la que decide: **matplotlib no hace shaping de árabe**. Uno de los seis grupos de idioma del proyecto es `ar`, y matplotlib lo dibuja desconectado y en orden inverso. El navegador aplica bidi y shaping de forma nativa. Para un proyecto cuyo argumento central es que el instrumento debe tratar igual a los seis idiomas, publicar una figura que rompe uno de los seis es una contradicción en el propio artefacto.

**Renderizador SVG, no canvas.** La tesis se imprime: un PNG a `pixelRatio` 3 es un raster grande, no una figura vectorial. Con el renderizador SVG la exportación es vector y escala sin degradarse. El costo —SVG es más lento con muchos elementos— es irrelevante con 24 textos y sigue siendo aceptable a escala de corpus para estos tipos de gráfica.

### 5. Pre-agregar en pandas, filtrar en el cliente

Igual que en el proyecto hermano y por las mismas razones: `ipywidgets` es frágil en Colab y, sobre todo, no sobrevive fuera del kernel, de modo que el artefacto exportable dejaría de funcionar.

Con 24 textos el argumento de tamaño no aplica —el agregado y los datos crudos pesan lo mismo— pero la forma se adopta igual, porque es la que sobrevive a la llegada del corpus. Lo que sí se hereda desde ya: las combinaciones vacías se omiten en vez de emitirse como cero.

### 6. La batería de ejemplo es un instrumento de prueba, no una muestra

Cuatro frases por seis idiomas, 24 textos:

| Frase | Para qué está |
|---|---|
| Hospitalidad positiva | ya existe en `MISMA_FRASE`; es el caso de la sección 7 |
| Gobernanza negativa | activa la dimensión donde el método actual es puro escalón |
| Violencia / inseguridad | única vía a `violence_salience` y `safety_perceived` |
| **Control mudo** (comida) | no habla de ninguna de las tres dimensiones |

El control mudo es el que carga el peso. Sin él no hay forma de demostrar que el eje de relevancia funciona: es el tuit que debe dar relevancia cercana a cero en gobernanza y no un juicio neutro. La celda 3 del notebook ya usa exactamente ese ejemplo —"un tuit sobre tacos preguntado por gobernanza"— para explicar por qué existe la tercera hipótesis; la batería lo convierte en medición.

**Alternativa considerada**: muestrear tuits reales del corpus de turistas. Se descarta para este propósito: el argumento de la sección 7 exige **contenido idéntico** en seis idiomas, y tuits reales no lo son. Los tuits reales entran cuando el usuario los pega o cuando llegue el corpus; la batería no los sustituye.

**Guardrail obligatorio**: la batería no es una muestra aleatoria de nada y ningún número salido de ella puede reportarse como hallazgo sobre el corpus. Las figuras generadas sobre la batería se rotulan como tales de forma visible, no en una nota al pie.

### 7. El escalón sólo se dibuja donde existe

Medido sobre las fórmulas de `analyzer.py`: `governance_trust = clamp(mg * 0.8)` no incorpora el sentimiento, así que sólo puede tomar **once valores**:

```
  -0.8  -0.64  -0.48  -0.32  -0.16  0.0  +0.16  +0.32  +0.48  +0.64  +0.8
```

`hospitality = clamp(s * 0.5 + mh)` y `atmosphere = clamp(s * 0.7 + ma)` **sí** incorporan el sentimiento, que es continuo, así que no son escalonadas: son una nube desplazada a saltos. La figura del escalón usa `governance_trust` como caso principal y dice explícitamente por qué las otras dos no lo muestran.

Esto importa más allá del dibujo: la fila "escalón ±0.2 / continuo" de la tabla introductoria del notebook es cierta sólo para una de las tres dimensiones tal como está enunciada. La figura obliga a precisarla.

### 8. El emparejamiento por subcadena se mide, no se afirma

`_mod()` usa `w in tl` sobre el texto crudo. Verificado antes de escribir este documento:

```
"The place felt unsafe at night"      -> governance_trust = +0.160   (safe dentro de unsafe)
"the crowd was unfriendly and rude"   -> activa friendly, rude, unfriendly
"she was kinda nice"                  -> hospitality +0.20           (kind dentro de kinda)
"global warming ruined the trip"      -> hospitality +0.20           (warm dentro de warming)
"La policía fue corrupta e ineficaz"  -> governance_trust =  0.000   (policia y corrupt se anulan)
```

El marco `LEXICO` guarda por cada palabra activada si el emparejamiento fue por palabra completa o por subcadena, y la figura de cobertura léxica reporta la proporción. Sobre una batería de 24 textos puede que el fenómeno casi no aparezca; el número que se reporte es el del corpus que esté cargado, y la figura lo dice. **No se corrige `_mod()`**: este change grafica el método actual tal como está en producción, y arreglarlo aquí falsearía la comparación.

### 9. Compatibilidad hacia adelante sin construir lo que no hace falta

`LARGO` reserva tres columnas opcionales —`tweet_id`, `created_at`, `lang`— vacías mientras la entrada sea una lista de textos. Ninguna figura las exige; cuando existan, el filtro por idioma se activa y el eje temporal encuentra dónde engancharse.

Lo que **no** se construye ahora: períodos, media móvil, huecos por día sin datos, multi-selección de idioma. Son la mitad de las tareas de `scoring-visualization` y aquí serían andamio de un edificio inexistente. Se deja la costura, no la obra.

Nota sobre `lang` en la batería: ahí el idioma **no es un filtro, es la variable del experimento**. Es el mismo campo con el rol invertido respecto del proyecto hermano, y la figura de dispersión lo trata como eje, no como control.

### 10. Una página, dos destinos, con la ficha del instrumento dentro

La misma función construye un documento HTML completo: dentro del notebook con `IPython.display.HTML`, y escrito a disco tal cual. No hay dos rutas de renderizado que puedan divergir. Resuelve además que en Colab cada salida vive en un iframe aislado y las figuras dejan de ser interactivas al reabrir el notebook guardado; el archivo es el artefacto que sobrevive.

La página embebe la **ficha técnica**: las frases de hipótesis textuales, `IDIOMA_HIPOTESIS`, `PLANTILLA`, los identificadores de ambos modelos y la fecha de la corrida. La celda 3 del notebook dice que las hipótesis son el instrumento de medición y que en la tesis se citan textualmente, igual que un libro de códigos; una figura que viaja sin su instrumento no es citable.

### 11. Legible en escala de grises

La tesis se imprime. Ninguna figura puede depender sólo del tono para distinguir `actual` de `nuevo`: se separan además por forma de marcador y por etiqueta directa sobre la serie, no por leyenda remota. Para `score`, paleta divergente con el cero anclado en el centro; para `relevancia`, secuencial. La comprobación es operativa: quitar el color y seguir pudiendo leer la figura.

## Risks / Trade-offs

**La batería de 24 textos se lee como si fuera un resultado** → Es el riesgo más caro, porque el destino es una tesis. Mitigación en tres capas: rótulo visible en cada figura generada sobre la batería, el `n` impreso siempre, y la advertencia por umbral cuando `n` cae por debajo de `N_MINIMO_FIGURA`. Aun así no se puede impedir que alguien cite el número; se puede hacer imposible citarlo sin ver el rótulo.

**Las traducciones de la batería pueden no ser semánticamente equivalentes** → Amenaza directa al argumento central: si la frase alemana es más entusiasta que la inglesa, parte de la dispersión que se atribuye al instrumento es artefacto de traducción. Mitigación: la batería se imprime completa en la página para que sea auditable, y la tesis debe declarar quién verificó las traducciones. Atenuante real: la dispersión del **método actual** no depende de la calidad de la traducción sino de la *ausencia* de las palabras en el léxico, y eso es verificable a simple vista en la columna de palabras activadas, que sale vacía. El riesgo pesa sobre la columna del rediseño, no sobre la del método actual.

**Dependencia del CDN** → Sin red la página queda inservible. Mitigación: mensaje explícito de por qué no cargó, en vez de una página en blanco. Empotrar ECharts la haría autosuficiente pero suma alrededor de un megabyte a cada archivo y al notebook guardado.

**Las figuras no sobreviven al guardado del notebook** → Limitación de Colab, no del diseño. Mitigada con el archivo descargable, que es el que va a la tesis.

**312 pasadas de un modelo large sólo para la batería** → El notebook ahora hace trabajo de GPU antes de que el usuario haya pegado un solo tuit. En T4 es tolerable; en CPU, que es como está configurado `Dockerfile.nlp` según la sección 9 del propio notebook, puede ser inviable. Mitigación: la corrida de la batería se cronometra y el tiempo se imprime, y debe poder desactivarse con un parámetro cuando el usuario traiga sus propios textos.

**El hallazgo de subcadenas puede no aparecer en la batería** → 24 textos controlados no tienen por qué contener `unsafe` ni `kinda`. La figura reportará una proporción baja o nula y eso es correcto: mide el corpus cargado. El riesgo es concluir que el defecto no existe. La página debe distinguir "no medido en este corpus" de "no ocurre".

**Modificar la celda 12 cambia el comportamiento de una celda existente** → A diferencia de `scoring-visualization`, que se impuso no tocar ninguna celda, aquí hay que hacerlo: el `raise ValueError` es justamente lo que impide producir figuras. Mitigación: el mecanismo de relleno se conserva —si el usuario pega textos y deja alguno de relleno, sigue fallando— y lo que cambia es el valor por defecto, de relleno inválido a batería válida.

**Se puede leer el change como si validara el rediseño** → No lo hace, y el notebook ya dice qué haría falta: alfa de Krippendorff sobre unos 200 tuits codificados a mano, umbral 0.67, infraestructura en `wc2026_analyzer/validation/agreement.py`. Esa advertencia debe quedar escrita junto a las figuras, no sólo en la sección 9.

## Migration Plan

1. Añadir la celda de configuración de figuras con los umbrales y la ruta de salida, antes de la sección 6.
2. Sustituir el contenido de la celda 12 por la batería de ejemplo, conservando la validación de relleno.
3. Insertar la celda de construcción de los tres marcos después de la celda 13.
4. Reescribir la celda 17 para que lea de `LARGO` en vez de construir su tabla a mano, lo que de paso elimina su dependencia oculta de `filas_demo`.
5. Insertar la sección de figuras después de la tabla resumen.
6. Ejecutar en sesión limpia de arriba a abajo y confirmar que no queda estado residual.
7. Abrir el HTML generado fuera del notebook y comprobar que las figuras y la exportación a SVG funcionan.

**Vuelta atrás**: las celdas nuevas se borran y la celda 12 recupera sus dos textos de relleno. El change no escribe sobre ningún dato existente; sólo genera un archivo HTML nuevo.

## Open Questions

- **¿Las cuatro frases de la batería las traduce quién?** Para la tesis hace falta poder decirlo. Si son traducción automática, la limitación tiene que estar escrita y acota lo que la figura de dispersión puede afirmar.
- **¿`UMBRAL_MUDEZ = 0.30` se sostiene?** El valor es arbitrario. Una opción es derivarlo empíricamente del control mudo de la batería —el nivel de relevancia que alcanza un tuit que efectivamente no habla del tema— pero con seis puntos eso es anecdótico. Queda pendiente hasta tener corpus.
- **¿La figura de descomposición `pos` / `neg` / `na` entra en la tesis o es sólo de depuración?** Es la que permite ver si las hipótesis están mal calibradas, lo cual es un argumento metodológico legítimo; pero son 24 barras apiladas y puede no leerse impresa.
- **¿El sentimiento entra como sexta dimensión o se queda como covariable?** `overall_sentiment` es idéntico en ambos métodos —sale del mismo modelo— así que no discrimina entre ellos, pero es el término que hace continuas a `hospitality` y `atmosphere` en el método actual y explica por qué no se ven escalonadas.
- **Cuando llegue el corpus, ¿las figuras de comparación de métodos sobreviven?** Comparar `actual` contra `nuevo` sobre miles de tuits produce nubes densas donde el par de puntos deja de leerse. Probablemente haga falta pasar a densidad o a hexbin, lo cual es otro change.
