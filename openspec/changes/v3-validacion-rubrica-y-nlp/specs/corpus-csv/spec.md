## ADDED Requirements

### Requirement: Entrada calificada con columnas de rúbrica
El notebook SHALL aceptar como corpus un archivo que, además de las columnas del mapeo, traiga columnas de calificación por criterio, y esas columnas SHALL conservarse sin intervenir en el mapeo ni en la evaluación del instrumento.

#### Scenario: Columnas adicionales
- **WHEN** el archivo de entrada contiene columnas de rúbrica además de las del mapeo
- **THEN** la validación del mapeo SHALL pasar, las columnas de rúbrica SHALL quedar disponibles para las secciones que las usan, y el costo informado del instrumento NO SHALL cambiar

#### Scenario: Corpus completo por defecto
- **WHEN** se configura la corrida sobre el archivo calificado
- **THEN** el tope de muestra por defecto SHALL ser ninguno, de modo que se evalúen todas las filas, y un tope declarado SHALL informar cuántas filas calificadas quedan fuera de la validación

#### Scenario: Identificadores no numéricos
- **WHEN** el archivo contiene identificadores reparados con un prefijo no numérico
- **THEN** SHALL tratarse como identificadores válidos y distintos, y NO SHALL convertirse a número

### Requirement: Carga de una corrida zero-shot previa
El notebook SHALL permitir reconstruir los resultados del instrumento desde un archivo exportado por una corrida anterior en lugar de volver a evaluar, y SHALL verificar que ese archivo corresponde al mismo instrumento y al mismo corpus antes de usarlo.

#### Scenario: Carga válida
- **WHEN** se declara la ruta de un archivo exportado cuyas hipótesis e identificadores coinciden con los de la configuración y la entrada actuales
- **THEN** los marcos de valores y probabilidades SHALL reconstruirse desde ese archivo, y el modelo NO SHALL cargarse ni ejecutarse

#### Scenario: Instrumento distinto
- **WHEN** la huella de las hipótesis del archivo no coincide con la configuración actual
- **THEN** la ejecución SHALL detenerse indicando qué difiere

#### Scenario: Corpus distinto
- **WHEN** los identificadores del archivo no coinciden con los de la entrada
- **THEN** la ejecución SHALL detenerse informando cuántos faltan en cada lado

#### Scenario: Valores idénticos a la corrida original
- **WHEN** se reconstruyen los marcos desde el archivo
- **THEN** las valencias y relevancias SHALL ser iguales a las exportadas, y las secciones posteriores SHALL producir los mismos resultados que con la corrida original
