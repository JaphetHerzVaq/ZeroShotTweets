## 1. Configuración

- [x] 1.1 Añadir una celda de configuración de figuras antes de la sección 6, con: umbral de mudez (0.30), umbral de dimensión muda, número mínimo de observaciones por figura, ruta del archivo HTML de salida e interruptor para omitir la batería de ejemplo
- [x] 1.2 Declarar los umbrales con un comentario que diga que el de mudez es arbitrario y debe justificarse en la tesis
- [x] 1.3 Declarar por dimensión su escala —valencia de menos uno a uno, o prominencia de cero a uno— y si tiene relevancia asociada, sin que ninguna figura infiera esto de los valores observados

## 2. Batería de ejemplo

- [x] 2.1 Redactar las cuatro frases —hospitalidad positiva, gobernanza negativa, violencia o inseguridad, y control mudo sobre comida— en los seis grupos de idioma, con la frase de origen y el idioma declarados por texto
- [x] 2.2 Reutilizar las seis versiones de la frase de hospitalidad que ya existen en `MISMA_FRASE`, en lugar de redactarlas de nuevo
- [x] 2.3 Sustituir el contenido de la celda 12 por la batería, conservando la validación que detiene la ejecución si queda algún texto de relleno
- [x] 2.4 Registrar quién o qué produjo las traducciones, para poder declararlo en la tesis
- [x] 2.5 Cronometrar la evaluación de la batería e imprimir el tiempo, el número de textos y el número de pasadas de modelo
- [x] 2.6 Derivar el número de pasadas del número de etiquetas de cada grupo, no de la constante 13
- [x] 2.7 Advertir antes de empezar cuando no haya GPU disponible
- [x] 2.8 Implementar el interruptor que omite la batería cuando el usuario aporta textos propios

## 3. Marcos de datos

- [x] 3.1 Escribir la función que recorre los resultados una sola vez y devuelve los tres marcos
- [x] 3.2 Marco de valores: una fila por texto, método y dimensión, con valencia, relevancia y escala
- [x] 3.3 Marco de probabilidades: una fila por texto, grupo de hipótesis y etiqueta
- [x] 3.4 Marco de emparejamientos léxicos: una fila por texto, dimensión y palabra activada, con polaridad y si el emparejamiento fue por palabra completa o por subcadena
- [x] 3.5 Incorporar al marco de valores las dimensiones que hoy se descartan: prominencia de violencia, seguridad percibida, sentimiento general y peso de engagement
- [x] 3.6 Dejar la relevancia como no disponible para el método actual, nunca como cero
- [x] 3.7 Añadir las columnas opcionales de procedencia —identificador, fecha e idioma— vacías cuando la entrada sea una lista de textos
- [x] 3.8 Poblar la columna de idioma desde la batería de ejemplo
- [x] 3.9 Verificar que ningún marco, ninguna tabla y ningún dato serializado contiene una magnitud que combine valencia y relevancia en un escalar

## 4. Reescritura de la tabla resumen

- [x] 4.1 Reescribir la celda 17 para que derive su tabla del marco de valores
- [x] 4.2 Eliminar su dependencia de `filas_demo`, que nace en la celda 15
- [x] 4.3 Confirmar que la tabla resultante contiene al menos la misma información que la actual, más las dimensiones recuperadas

## 5. Preparación de los datos de cada figura

- [x] 5.1 Calcular una sola vez, en Python, los datos que cada figura necesita
- [x] 5.2 Omitir las combinaciones sin observaciones en lugar de emitirlas como cero
- [x] 5.3 Calcular el rango y la desviación entre idiomas por método y por dimensión
- [x] 5.4 Calcular la proporción de observaciones bajo el umbral de mudez por dimensión
- [x] 5.5 Calcular la cobertura léxica por idioma y la proporción de emparejamientos por subcadena
- [x] 5.6 Calcular los valores discretos alcanzables por el método actual en las dimensiones cuya fórmula no incorpora el sentimiento
- [x] 5.7 Informar el tamaño del conjunto embebido
- [x] 5.8 Serializar con `json.dumps` sin incluir textos completos más allá de lo que la batería necesita mostrar

## 6. Andamiaje de la página

- [x] 6.1 Construir la plantilla HTML con la carga de ECharts desde el CDN
- [x] 6.2 Inicializar cada gráfica con el renderizador SVG, no con canvas
- [x] 6.3 Mostrar un mensaje explicativo si la biblioteca no carga, en vez de dejar la página en blanco
- [x] 6.4 Embeber la ficha técnica: frases de hipótesis textuales, idioma de las hipótesis, plantilla, identificadores de ambos modelos y fecha de la corrida
- [x] 6.5 Embeber los textos completos de la batería para que las traducciones sean auditables
- [x] 6.6 Rotular de forma visible toda figura construida sobre la batería como instrumento de prueba, y omitir el rótulo cuando la entrada sean textos del usuario
- [x] 6.7 Incluir la advertencia de que las figuras describen y no sustituyen la validación contra codificación humana
- [x] 6.8 Imprimir el número de observaciones en cada figura y la advertencia cuando quede bajo el umbral

## 7. Figuras

- [x] 7.1 Dispersión entre idiomas: un par de valores por idioma, actual contra rediseño, misma escala, con el rango y la desviación de cada método impresos como el número reportable
- [x] 7.2 Generar la dispersión para cada dimensión léxica en un bucle, sin que el conjunto de dimensiones aparezca fijo
- [x] 7.3 Plano de valencia contra relevancia, uno por dimensión con relevancia, con la banda de mudez delimitada y nombrada y el conteo de observaciones dentro
- [x] 7.4 Excluir de ese plano las dimensiones sin relevancia y explicar la exclusión en la propia figura
- [x] 7.5 Permitir identificar el texto y el idioma de origen de cada observación del plano
- [x] 7.6 Figura de valores posibles: actual contra rediseño, con la referencia de acuerdo perfecto dibujada
- [x] 7.7 Marcar los once valores discretos alcanzables en la dimensión de confianza institucional
- [x] 7.8 Indicar en las otras dos dimensiones que no son escalonadas porque su fórmula incorpora el sentimiento, en lugar de marcar valores discretos inexistentes
- [x] 7.9 Distribución completa de relevancia por dimensión con el umbral superpuesto
- [x] 7.10 Alerta escrita cuando una dimensión supera el umbral de dimensión muda, y mensaje explícito cuando ninguna lo supera
- [x] 7.11 Presentar la ausencia como magnitud propia, nunca apilada junto a los valores de valencia
- [x] 7.12 Descomposición de probabilidades por grupo de hipótesis, con las etiquetas legibles y sin que el número de etiquetas aparezca fijo
- [x] 7.13 Señalar cuando la hipótesis de irrelevancia domina casi todas las observaciones de un grupo
- [x] 7.14 Cobertura léxica por idioma, con la cobertura nula explicada como "las dimensiones léxicas valen lo mismo por construcción"
- [x] 7.15 Reportar la proporción de emparejamientos por subcadena con ejemplos del corpus cargado
- [x] 7.16 Distinguir "no observado en este corpus" de "no ocurre" cuando no haya emparejamientos por subcadena
- [x] 7.17 Mostrar un aviso de ausencia de datos cuando una figura no tenga nada que dibujar, en lugar de un lienzo vacío o un error

## 8. Presentación para impresión

- [x] 8.1 Escala divergente centrada en cero para la valencia, secuencial para la relevancia
- [x] 8.2 Distinguir actual de rediseño por forma de marcador y etiqueta directa, además del tono
- [x] 8.3 Comprobar cada figura con el color eliminado y confirmar que sigue siendo legible
- [x] 8.4 Confirmar que la exportación produce un archivo vectorial que no se degrada al ampliarse
- [x] 8.5 Confirmar que las etiquetas en árabe se renderizan con la forma y el orden correctos

## 9. Doble salida

- [x] 9.1 Construir el documento una sola vez y usarlo para ambos destinos
- [x] 9.2 Mostrarlo en la salida de la celda con `IPython.display.HTML`
- [x] 9.3 Escribir el archivo autocontenido en la ruta configurada y ofrecer la descarga desde Colab
- [x] 9.4 Documentar en la celda que las figuras dejan de ser interactivas al reabrir el notebook guardado y que el archivo es el artefacto que va a la tesis

## 10. Validación

- [x] 10.1 Ejecutar de principio a fin en sesión limpia sin modificar ninguna celda y confirmar que no hay excepción y que se producen todas las figuras
- [x] 10.2 Confirmar que dejar un texto de relleno sigue deteniendo la ejecución con el mensaje correspondiente
- [x] 10.3 Sustituir la batería por textos propios y confirmar que todas las figuras se construyen sin cambios de código
- [x] 10.4 Ejecutar la tabla resumen sin haber ejecutado la sección de demostración entre idiomas y confirmar que no falla
- [ ] 10.5 Confirmar que el control mudo da relevancia baja en las tres dimensiones léxicas, que es la demostración de que el eje de relevancia funciona
- [x] 10.6 Confirmar que cada una de las cinco dimensiones recibe al menos un texto que la activa
- [x] 10.7 Cambiar el umbral de mudez en la configuración, reejecutar y confirmar que todas las figuras reflejan el nuevo corte
- [x] 10.8 Buscar en todo el código y en el JSON embebido cualquier producto de valencia por relevancia y confirmar que no existe
- [x] 10.9 Abrir el archivo generado fuera del notebook y confirmar que las figuras y la exportación funcionan
- [x] 10.10 Simular la caída del CDN y confirmar que aparece el mensaje explicativo en vez de una página en blanco
- [x] 10.11 Confirmar que ninguna fórmula de `metodo_actual` ni de `metodo_nuevo` fue modificada
- [x] 10.12 Confirmar que las celdas 0 a 11 y 13 a 16 no fueron modificadas
- [x] 10.13 Contrastar el rango y la desviación que reporta la figura de dispersión contra los que imprime hoy la sección 7, y confirmar que coinciden
- [ ] 10.14 Registrar el tiempo real de la batería y compararlo contra lo que costaría un corpus del tamaño previsto

## Notas de ejecución

**Pendiente, requiere GPU y los modelos reales**

- `10.5` y `10.14` son los dos únicos puntos que no se pueden cerrar fuera de Colab. La
  maquinaria está verificada —el control mudo se mide, se compara contra el umbral y la
  página imprime el veredicto en verde o en rojo— pero el número sale de una corrida con
  `joeddav/xlm-roberta-large-xnli`, no de un doble de prueba. Igual el cronómetro: está
  instrumentado e imprime, pero el tiempo real es el de la T4.

**Cómo se verificó el resto**

Dos suites en `scratchpad/`, ambas ejecutan **las celdas reales del notebook** con los dos
pipelines sustituidos por dobles deterministas:

- `smoke.py` — corre el notebook de principio a fin y comprueba 27 invariantes.
- `validate2.py` — los escenarios que el humo no cubre: relleno sin sustituir, textos
  propios, ejecutar la tabla resumen sin la sección 9, umbral reconfigurado, y que las
  celdas de medición siguen byte a byte como estaban.

Y un paso de inspección visual con Chrome sin cabeza, que encontró tres defectos que
ninguna aserción habría detectado: la llamada a `dibujar()` colocada antes de las
constantes que usa, el nombre del eje X solapando la leyenda, y `pos`/`neg` colapsando al
mismo tono en escala de grises.

**Desviaciones respecto de lo planeado**

- `10.12` decía que las celdas 0–11 y 13–16 no se tocarían. La celda de comparación **sí**
  se modificó, porque `2.5` pedía cronometrar la corrida y ahí es donde ocurre; el cambio
  es aditivo y no altera ninguna medición. Además se renumeraron los encabezados de
  sección y las referencias cruzadas, porque el documento gana tres secciones. `validate2`
  comprueba que las celdas de medición son idénticas a la versión previa y que las ocho
  fórmulas siguen intactas.
- `2.2` pedía reutilizar las seis versiones de `MISMA_FRASE` en lugar de volver a
  redactarlas. Como la celda que las define va **después** de la batería y no debía
  modificarse, son los mismos literales más una aserción en la celda de figuras que falla
  si alguien edita una y no la otra. `10.13` comprueba además que el rango y la σ que
  reporta la figura coinciden con los que imprime la sección 9.
- El CDN estaba mal: `echarts/5.5.1` no existe en cdnjs y devolvía 404. Se corrigió a
  `5.6.0`. Lo detectó el render, no una aserción.

**Limitación conocida que queda en pie**

En escala de grises, `pos` (azul) y `neg` (rojo) caen casi en el mismo tono. Re-escalonar
la paleta está fuera de norma, así que la mitigación es la documentada: separación de 2 px
entre segmentos, valor dentro de cada uno, nombre de la serie rotulado en la primera barra
y vista de tabla. La figura se lee sin color, pero por etiqueta y posición, no por tono.
