## 1. Dimensiones e hipótesis

- [x] 1.1 Sustituir el conjunto de dimensiones por ambiente, imagen cultural y perspectiva política, cada una con sus tres hipótesis en español y en inglés
- [x] 1.2 Eliminar la dimensión de hospitalidad de la definición de dimensiones
- [x] 1.3 Mover el ancla geográfica a la plantilla de hipótesis y redactar las etiquetas sin ella
- [x] 1.4 Reescribir las cuatro etiquetas del grupo de violencia y seguridad sin el ancla, coherentes con la plantilla
- [x] 1.5 Cambiar el idioma de las hipótesis a español
- [x] 1.6 Corregir el comentario que afirma que las etiquetas de violencia se mantienen idénticas al código actual, que dejará de ser cierto
- [x] 1.7 Confirmar que el número de pasadas por texto sigue derivándose del número de etiquetas y que da trece
- [x] 1.8 Actualizar el texto de la sección que explica las dimensiones para que describa el conjunto nuevo y el ancla en la plantilla
- [ ] 1.9 Correr la batería y comparar los valores contra la corrida previa, dejando registro de qué cambió

## 2. Verificación del ancla

- [x] 2.1 Añadir un interruptor que permita construir las hipótesis con el ancla dentro de las etiquetas en lugar de en la plantilla
- [ ] 2.2 Evaluar la batería con ambas variantes y registrar la distribución de relevancia de cada una
- [ ] 2.3 Comprobar si la variante con ancla en las etiquetas desplaza la relevancia hacia abajo y cuántas dimensiones cruzan el umbral de dimensión muda en cada variante
- [x] 2.4 Dejar el resultado de la comparación embebido en la salida de figuras, para que la elección quede respaldada por el número
- [ ] 2.5 Si el efecto previsto no aparece, documentarlo y revisar la decisión antes de continuar

## 3. Batería reacomodada

- [x] 3.1 Reasignar la frase de gobernanza a la dimensión de perspectiva política, conservando sus seis versiones
- [x] 3.2 Reasignar el texto de comida a la dimensión de imagen cultural como sonda positiva, conservando sus seis versiones
- [x] 3.3 Reasignar la frase de hospitalidad a control sin contenido evaluable, conservando sus seis versiones
- [x] 3.4 Redactar la frase nueva de ambiente positivo en los seis idiomas y declarar la procedencia de sus traducciones
- [x] 3.5 Actualizar el campo de objetivo y el de qué prueba cada frase, para que describan la asignación nueva
- [x] 3.6 Actualizar la tabla de la sección que presenta los textos a evaluar
- [x] 3.7 Confirmar que la batería produce treinta textos y que cada una de las cinco dimensiones recibe al menos un texto que la activa

## 4. Demostración entre idiomas

- [x] 4.1 Repuntar la demostración de sesgo entre idiomas a la dimensión de perspectiva política, usando las seis versiones de la frase de gobernanza
- [x] 4.2 Cambiar la clave de la aserción de coherencia entre la batería y la demostración, de la frase de hospitalidad a la de gobernanza
- [x] 4.3 Hacer visible la inversión de signo entre idiomas, no solo la dispersión
- [x] 4.4 Actualizar el texto de la sección para que describa el argumento nuevo, incluyendo que el valor es exacto por no incorporar el sentimiento
- [x] 4.5 Confirmar que el rango y la desviación que imprime la sección coinciden con los que recalcula la figura

## 5. Escalas, métodos y tercera vía

- [x] 5.1 Actualizar las claves de la declaración de escalas al conjunto de dimensiones nuevo
- [x] 5.2 Declarar que la dimensión de imagen cultural la produce un solo método
- [x] 5.3 Actualizar la clave de la declaración de valores escalonados a la dimensión de perspectiva política
- [x] 5.4 Actualizar el mapeo entre dimensiones y listas de palabras del método léxico
- [x] 5.5 Actualizar la lista de dimensiones que recorre la celda de comparación
- [x] 5.6 Añadir la medición del método léxico sobre la columna de traducción como un tercer valor de la columna de método, sin columnas nuevas en el marco
- [x] 5.7 Registrar en el marco sobre qué columna de texto se calculó cada fila de método léxico
- [x] 5.8 Excluir de la vía traducida las filas sin traducción y contarlas, sin sustituirlas por el texto original
- [x] 5.9 Confirmar que la guardia de columnas numéricas sigue vigente tras añadir métodos y columnas

## 6. Carga del corpus

- [x] 6.1 Añadir el modo de entrada de corpus junto a la batería y los textos pegados a mano
- [x] 6.2 Localizar el archivo en el directorio de trabajo y detenerse con la lista de lo encontrado si hay cero o más de uno
- [x] 6.3 Leer el archivo respetando la marca de orden de bytes, de modo que el nombre de la primera columna quede limpio
- [x] 6.4 Declarar el mapeo de columnas en la celda de configuración y validarlo contra el encabezado antes de cargar ningún modelo
- [x] 6.5 Fallar con un mensaje que enumere las columnas presentes cuando falte una declarada
- [x] 6.6 Poblar identificador, fecha e idioma en las columnas de procedencia que el marco ya tiene reservadas
- [x] 6.7 Interpretar los valores booleanos de forma insensible a mayúsculas
- [x] 6.8 Cargar las filas sin fecha con la fecha marcada como no disponible e informar cuántas son
- [x] 6.9 Permitir elegir qué columna de texto alimenta al modelo
- [x] 6.10 Implementar el tope de muestra e informar cuántos textos se omitieron
- [x] 6.11 Deduplicar por identificador e informar cuántas filas se descartaron
- [x] 6.12 Informar el tiempo total, el tiempo por texto y el costo estimado del corpus completo
- [ ] 6.13 Correr con un tope de doscientos textos y extrapolar antes de comprometer el corpus completo

## 7. Evaluación por lotes

- [x] 7.1 Agrupar las llamadas al modelo de inferencia por lotes con tamaño configurable
- [x] 7.2 Conservar la forma de la salida por texto y por etiqueta, sin cambios para quien la consume
- [x] 7.3 Comprobar sobre un mismo conjunto de textos que los valores con lotes y sin lotes coinciden
- [ ] 7.4 Medir la mejora de tiempo y registrarla

## 8. Estratos e idiomas del corpus

- [x] 8.1 Incorporar al marco los campos de consulta de origen y modalidad de recolección
- [x] 8.2 Derivar la lista de idiomas de los datos cargados en lugar de un conjunto fijo de grupos
- [x] 8.3 Agrupar los códigos que indican ausencia de idioma detectable en una categoría explícita
- [x] 8.4 Indicar el número de observaciones de cada idioma y excluir explícitamente los que no alcanzan el mínimo
- [x] 8.5 Informar cuántos textos pertenecen a idiomas sin ninguna palabra en las listas del método léxico, como resultado y no como ausencia de datos
- [x] 8.6 Desglosar por estrato las figuras que promedian sobre el corpus
- [x] 8.7 Emitir alerta escrita cuando un promedio mezcle estratos cuya consulta buscaba expresamente la dimensión promediada, indicando qué proporción del corpus proviene de ellas

## 9. Figuras y rotulación

- [x] 9.1 Convertir el rótulo de procedencia en tres estados: batería, textos propios y corpus
- [x] 9.2 Rotular las figuras sobre el corpus con su tamaño y con la advertencia de que no están validadas contra codificación humana
- [x] 9.3 Declarar explícitamente que el corpus no trae codificación manual y que la validación de acuerdo sigue pendiente
- [x] 9.4 Excluir la dimensión de imagen cultural de las figuras que comparan métodos y explicar la exclusión en la propia figura
- [x] 9.5 Distinguir los tres métodos por forma de marcador y etiqueta directa además del tono, y comprobarlo en escala de grises
- [x] 9.6 Declarar en la figura que la vía traducida mide el léxico junto con la calidad de la traducción y que ambos efectos no se separan
- [x] 9.7 Embeber en la ficha técnica el conjunto de dimensiones nuevo, la plantilla con el ancla y el texto literal de cada hipótesis
- [x] 9.8 Actualizar el texto de la sección de figuras y el de la sección final de lectura para que describan el conjunto de dimensiones nuevo

## 10. Validación

- [x] 10.1 Ejecutar de principio a fin en sesión limpia con la batería y confirmar que no hay excepción y que se producen todas las figuras
- [ ] 10.2 Confirmar que el control mudo nuevo da relevancia baja en las tres dimensiones, y dar por redefinida la tarea equivalente del change anterior
- [ ] 10.3 Confirmar que el texto de comida da relevancia alta en imagen cultural, que es lo que justifica su ascenso
- [x] 10.4 Confirmar que ninguna fórmula del método actual ni del rediseño fue modificada
- [x] 10.5 Confirmar que ninguna celda falla por la ausencia de la dimensión de hospitalidad
- [x] 10.6 Ejecutar con el modo de textos pegados a mano y confirmar que sigue deteniéndose con los textos de relleno sin sustituir
- [ ] 10.7 Ejecutar con el corpus completo y registrar el tiempo real
- [x] 10.8 Confirmar que las figuras que comparan idiomas se construyen con los idiomas realmente presentes y no fallan por los grupos ausentes
- [ ] 10.9 Confirmar que el bloque en japonés se mide, revisando además la distribución de etiquetas del modelo de sentimiento sobre ese bloque y declarando la limitación si degrada
- [x] 10.10 Buscar en todo el código y en los datos serializados cualquier producto de valencia por relevancia y confirmar que no existe
- [x] 10.11 Cambiar el umbral de mudez, reejecutar y confirmar que todas las figuras reflejan el corte nuevo
- [x] 10.12 Abrir el archivo de figuras generado fuera del notebook y confirmar que se ve y exporta correctamente
- [ ] 10.13 Contar cuántos textos del corpus se truncan en el corte de caracteres e informarlo
- [ ] 10.14 Revisar si las filas sin fecha constituyen un estrato propio y dejar constancia de la conclusión


## 11. Exportación de resultados

- [x] 11.1 Conservar el marco de origen del CSV para poder devolver el archivo con las columnas de resultados añadidas
- [x] 11.2 Declarar en la celda de configuración las rutas de salida y una carpeta propia para ellas
- [x] 11.3 Construir la tabla ancha: una fila por texto, una columna por dimensión y método, la relevancia aparte
- [x] 11.4 Unir las columnas originales por identificador y no por posición
- [x] 11.5 Exportar las probabilidades crudas de cada hipótesis como columnas, tras un interruptor
- [x] 11.6 Construir la tabla larga a partir del marco de valores
- [x] 11.7 Escribir en codificación que permita a Excel leer acentos y japonés
- [x] 11.8 Repetir a la salida la guardia que impide combinar valencia y relevancia en un escalar
- [x] 11.9 Ofrecer la descarga desde Colab y explicar la alternativa cuando no esté disponible
- [x] 11.10 Imprimir la procedencia, cuántas filas salen de cuántas, y la advertencia de no validado
- [x] 11.11 Funcionar sin archivo de origen, cuando la entrada sea la batería o textos propios
- [x] 11.12 Impedir que la autodetección del CSV de entrada tropiece con los archivos que el propio notebook escribe

## Notas de ejecución

**Qué queda abierto y por qué**

Doce tareas necesitan una corrida real con `joeddav/xlm-roberta-large-xnli` en GPU, que no
existe fuera de Colab. La maquinaria de cada una está implementada y verificada; lo que falta
es el número que sale del modelo, no el código que lo produce:

- `1.9`, `3.7` (activación), `10.2`, `10.3` — comparar contra la corrida previa y confirmar que
  el control mudo da relevancia baja y el texto de comida la da alta en `imagen_cultural`.
- `2.2`, `2.3`, `2.5` — la comparación A/B del ancla. **El mecanismo sí quedó hecho** (`2.1`,
  `2.4`): la sección 8 corre la batería con las dos variantes, compara las distribuciones de
  relevancia, embebe el resultado en la página y **emite el veredicto por el signo del delta,
  no por lo que está escrito**. Si la predicción falla, la página lo dice en rojo y pide
  revisar la decisión de diseño. Falta correrlo con el modelo real.
- `6.13`, `7.4`, `10.7`, `10.9`, `10.13` — cronometrar, medir la mejora de los lotes, correr el
  corpus completo, revisar el sentimiento en japonés y contar los textos truncados.
- `10.14` — las 69 filas sin `created_at` coinciden en número exacto con las de capitalización
  anómala (`FALSE`), lo que apunta a un lote fusionado de otra fuente. Queda constancia; no se
  resolvió.

**Cómo se verificó el resto**

`scratchpad/harness.py` ejecuta **las celdas reales del notebook** con los dos pipelines
sustituidos por dobles deterministas. Tres suites encima: `validar.py` (**38 comprobaciones**),
`validar2.py` (**13**) y `validar3.py` (**16**, la exportación). 67 en total, 0 fallos.

Cubren: el conjunto de dimensiones y la ausencia de `hospitality` —incluida la comprobación de
que solo sobrevive donde debe, la portada y las listas literales de `analyzer.py`—; el ancla en
la plantilla y no en las etiquetas; la sección 10 sobre `perspectiva_politica`; los tres métodos
en el marco con `origen_texto` distinguiendo las dos vías léxicas; procedencia y estratos
poblados; idiomas derivados de los datos con los códigos de «sin idioma» agrupados; la guardia
de columnas numéricas; el umbral reconfigurado llegando a las figuras; el relleno sin sustituir
deteniendo la ejecución; la numeración de secciones 1–13 sin referencias cruzadas fuera de
rango; y que **las siete fórmulas de medición siguen literales**.

Tres resultados que valen por sí solos:

- **Los valores del método léxico en la sección 10 son exactos, y se calcularon a mano antes de
  escribir una línea de código:** `en +0.1600`, `es −0.1600`, `pt −0.1600`, `fr +0.1600`,
  `de/ar 0.0000`, rango `0.3200`, σ `0.1306`. La corrida los reproduce y la figura recalcula la
  misma dispersión que imprime la sección. No dependen de ninguna GPU: `perspectiva_politica` no
  incorpora el sentimiento. En inglés el método actual **puntúa +0.16 un texto que dice que la
  policía era corrupta**, porque `police` y `authorities` están en la lista positiva.
- **Los lotes:** 4 llamadas al pipeline en lugar de 390 sobre la batería, y los valores con
  lotes y sin lotes coinciden hasta el último decimal sobre 40 textos.
- **La vía traducida hace visible lo que buscaba:** sobre el corpus, un tuit japonés da
  `actual = 0.000` (el léxico es ciego) contra `traducido = −0.356`.

Y un paso de render con Chrome sin cabeza sobre tres variantes de la página: **15 gráficas** con
la batería, **16** con el A/B del ancla activo (aparece `f8`) y **16** con el corpus (aparece
`f7`, el desglose por estrato), más el banner de corpus, las tres leyendas de método y el aviso
de exclusión de `imagen_cultural` presentes en el DOM.

**Desviaciones respecto de lo planeado**

- El proposal y el diseño decían que la vía traducida **cuesta cero pasadas de modelo**. Es
  inexacto y quedó corregido en ambos: no añade ninguna pasada del modelo **NLI** —el *large*,
  que domina el costo— pero sí **una del modelo de sentimiento** (base) por tuit, porque
  `atmosfera` incorpora el sentimiento y el de la traducción hay que calcularlo.
- **El notebook gana una sección.** `2.4` pedía embeber la comparación del ancla en la salida de
  figuras; hacerlo bien exigía una sección propia que corriera las dos variantes. Pasó a ser la
  sección 8, el documento va de 12 a 13 secciones, y se renumeraron los encabezados y las 16
  referencias cruzadas. La suite comprueba que la numeración queda 1–13 en orden.
- Se tocaron dos celdas que el Impact no listaba: la tabla resumen derivaba los comparables de
  `len(metodos) == 2`, lo que con tres métodos la habría vaciado en silencio; y la plantilla
  HTML fijaba dos series por figura. Ambas pasaron a preguntar por los métodos concretos.
- `8.6` pedía desglosar por estrato «las figuras que promedian». Se implementó como una **figura
  propia** más las alertas, en vez de desglosar cada figura existente: multiplicar cada una por
  el número de estratos habría hecho la página ilegible sin añadir información que la figura del
  desglose no dé.
- **La exportación a CSV no estaba en el change.** La pidió el usuario a mitad de la
  implementación y se añadió como sección 13 y capacidad `results-export`, con su grupo de
  tareas y su spec. El notebook pasa de 13 a 14 secciones.
- **Un fallo propio, encontrado ejecutando dos veces seguidas.** Al escribir el CSV de
  resultados en el directorio de trabajo, la autodetección de la entrada encontraba tres
  archivos en la segunda corrida y **el notebook se bloqueaba a sí mismo**. Excluir por nombre
  no bastaba —depende de los nombres configurados—, así que las salidas se mudaron a `salida/`.
  No lo detectó ninguna aserción: lo detectó correr el notebook dos veces.
- La figura de cobertura léxica agrupaba por `lang` crudo, lo que volvía a separar `und`, `qme`
  y `zxx` que la celda de marcos ya había agrupado. Corregido a `lang_grupo`.

**Limitación conocida que queda en pie**

En escala de grises, `actual` (#2a78d6) y `nuevo` (#eb6834) quedan a **1.38:1** de contraste:
casi el mismo tono. Es la misma limitación que el change anterior documentó para `pos`/`neg`, y
re-escalonar la paleta sigue fuera de norma. El método que se añadió aquí, `traducido`
(#8fb8e8), está a **2.14:1** de `actual` y además lleva **trama diagonal**, así que es el mejor
separado de los tres. La mitigación para el par viejo es la ya documentada: etiqueta directa,
valor impreso sobre cada barra y vista de tabla. La figura se lee sin color, pero por etiqueta y
posición, no por tono.

**Advertencia sobre los números de esta sesión**

Todo lo medido aquí salió de **dobles deterministas**, no de los modelos. Los valores de
`NUEVO`, las relevancias y el veredicto del A/B del ancla que se vieron durante el desarrollo
**no son evidencia de nada**: sirvieron para comprobar formas, claves, agregaciones y guardias.
Los dos archivos HTML generados durante las pruebas se borraron por eso mismo. Lo único
reportable que salió de esta sesión son los valores del método léxico, que son aritmética sobre
listas de palabras y no pasan por ningún modelo.
