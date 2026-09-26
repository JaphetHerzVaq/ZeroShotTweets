## ADDED Requirements

### Requirement: Frecuencias obtenibles sin GPU y fuera de Colab
El proyecto SHALL ofrecer un script local que produzca las frecuencias de lemas y de entidades del corpus sin GPU y sin ejecutar el notebook entero, porque el etiquetado lingüístico y el conteo son deterministas y de CPU, y sólo los embeddings y el agrupamiento necesitan acelerador.

#### Scenario: Ejecución sin acelerador
- **WHEN** se ejecuta el script con el corpus y el notebook presentes
- **THEN** SHALL producir las tablas de frecuencias sin cargar modelos de embeddings, de reducción de dimensión ni de agrupamiento

#### Scenario: Dependencia ausente
- **WHEN** falta el analizador lingüístico o su modelo
- **THEN** el script SHALL detenerse con un mensaje que diga exactamente qué instalar, y NO SHALL producir tablas parciales

### Requirement: Una sola fuente de verdad para las reglas
El script NO SHALL reimplementar la limpieza del texto, el diccionario de entidades, las categorías gramaticales, la regla de polaridad ni la codificación de la rúbrica. SHALL ejecutar los bloques del propio notebook que ya las definen, de modo que no exista una segunda copia que mantener sincronizada.

#### Scenario: Cambio en el diccionario de entidades
- **WHEN** se edita el diccionario de entidades en el notebook
- **THEN** la siguiente ejecución del script SHALL reflejar ese cambio sin que haya que tocar el script

#### Scenario: Bloques localizados por marcador
- **WHEN** el script busca los bloques que necesita
- **THEN** SHALL localizarlos por un marcador declarado al inicio de cada celda y NO por su posición en el notebook

#### Scenario: Bloque ausente o duplicado
- **WHEN** falta un bloque requerido o su marcador aparece más de una vez
- **THEN** el script SHALL detenerse nombrando el bloque y explicando cómo reponer el marcador, y NO SHALL continuar con una parte del pipeline

### Requirement: Separación de los bloques por su necesidad de acelerador
El notebook SHALL mantener separados, en celdas distintas y marcadas, los bloques que sólo necesitan CPU de los que necesitan acelerador, de modo que un consumidor externo pueda ejecutar los primeros sin los segundos.

#### Scenario: Frontera respetada
- **WHEN** se ejecutan únicamente los bloques de CPU
- **THEN** SHALL obtenerse el texto preparado, los lemas y las entidades, y NO SHALL requerirse ninguna variable producida por los bloques de acelerador

### Requirement: Cortes declarados con su solapamiento
Las frecuencias SHALL calcularse sobre el corpus completo, sobre los grupos de la rúbrica, sobre los grupos de polaridad y sobre cada criterio de la rúbrica. El script SHALL publicar además una tabla de grupos que declare, para cada corte, el número de tuits y si sus grupos son disjuntos.

#### Scenario: Cortes por criterio
- **WHEN** se calculan las frecuencias por criterio de la rúbrica
- **THEN** cada grupo SHALL contener los tuits con nivel mayor que 0 en ese criterio, y el corte SHALL declararse como NO disjunto porque un tuit puede tocar varios criterios

#### Scenario: Cortes disjuntos
- **WHEN** se calculan las frecuencias por polaridad
- **THEN** el corte SHALL declararse disjunto, y la suma de sus grupos SHALL ser igual al número de tuits calificados

### Requirement: Las dos formas de contar en cada fila
Cada fila de las tablas SHALL traer tanto las ocurrencias del término como el número de tuits en que aparece, junto al tamaño de su grupo, porque las figuras del notebook cuentan lemas por ocurrencia y entidades por tuit y esa asimetría es invisible si sólo se publica una de las dos.

#### Scenario: Comparación contra las figuras
- **WHEN** alguien contrasta una tabla contra una figura del notebook
- **THEN** SHALL poder elegir la columna que corresponde a esa figura, y la asimetría SHALL estar declarada en la salida del script

#### Scenario: Categoría de la entidad
- **WHEN** se publica la tabla de entidades
- **THEN** cada fila SHALL indicar la categoría de la entidad, distinguiendo las que vienen del diccionario de las que reconoce el modelo estadístico

### Requirement: Salida estable entre corridas
Las tablas SHALL tener un orden determinista, de modo que dos ejecuciones con la misma entrada produzcan archivos idénticos y sus diferencias puedan versionarse.

#### Scenario: Dos ejecuciones seguidas
- **WHEN** se ejecuta el script dos veces con la misma entrada y las mismas versiones
- **THEN** los archivos producidos SHALL ser idénticos
