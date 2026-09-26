## 0. Base del notebook v4

- [x] 0.1 Copiar `rediseno_zeroshot_colab_v3.ipynb` a `rediseno_zeroshot_colab_v4.ipynb` y dejar la v3 intacta, como cada change anterior de este proyecto
- [x] 0.2 Actualizar la celda de título: notebook 4, qué cambia respecto de la v3 y la advertencia de que las nubes de polaridad son descriptivas

## 1. Polaridad en la codificación de la rúbrica

- [x] 1.1 En la celda 6, escribir `polaridad_de_tuit(niveles_valencia)` con la regla de polos primero: `positivo` si hay algún 4–5 y ningún 1–2, `negativo` si hay algún 1–2 y ningún 4–5, `ambivalente` si todos los criterios de valencia presentes valen 3, `sin_polaridad` si no hay ninguno presente
- [x] 1.2 Tomar los criterios de valencia leyendo `escala == "valencia"` de `CRITERIOS`, nunca por nombre de criterio, para que añadir o quitar un criterio a la rúbrica no exija tocar esta función
- [x] 1.3 Añadir la columna `polaridad` a `RUBRICA_TUIT` junto a `calificado`, `con_faltante` y `grupo`, ignorando niveles `NaN` (faltante `BLOQUEADO`) y el nivel 0
- [x] 1.4 Añadir la aserción de partición: la suma de los cuatro grupos es igual al número de calificados y ninguno se solapa; al fallar, detener nombrando los identificadores en conflicto y sus niveles por criterio
- [x] 1.5 Extender el reporte impreso de la celda 6 con el recuento por polaridad, en el mismo formato que ya usa para los grupos
- [x] 1.6 Verificar con `tweets_calificados_anclada.csv` que da 76 positivo, 45 negativo, 19 ambivalente, 4 sin polaridad, y que suman 144

## 2. Generalización del contraste de vocabulario

- [x] 2.1 En la celda 39, dar a `log_odds` dos parámetros de rótulo para los lados y devolver las llaves y los campos `n_<lado>` con esos nombres en vez de `calificados` / `no_calificados`
- [x] 2.2 Actualizar la llamada existente de `LOG_ODDS` para pasar los rótulos `calificados` y `no_calificados`, sin cambiar umbrales ni cálculo
- [x] 2.3 En la celda 41, leer los rótulos desde los datos en vez de escribirlos en el JS, y ajustar el texto del panel para que nombre los lados comparados
- [x] 2.4 Comprobar que el panel «Vocabulario característico» sigue mostrando exactamente los mismos términos y puntuaciones que antes del cambio

## 3. Conteos de lemas por grupo

- [x] 3.1 Propagar `polaridad` a `NLP_TUIT` desde `RUBRICA_TUIT`, junto a `grupo` y `calificado`
- [x] 3.2 Construir los contadores de lemas de las dos nubes descriptivas: corpus completo y calificados
- [x] 3.3 Construir los contadores de los tres grupos de polaridad y calcular cada uno contra el resto con `log_odds`, con el prior restringido a los tuits con polaridad y los `sin_polaridad` fuera
- [x] 3.4 Quedarse con los términos de z positiva de cada grupo y ordenarlos por peso con desempate alfabético estable
- [x] 3.5 Registrar por nube el número de tuits y el número de términos que la sostienen, y marcar las que quedan por debajo del mínimo declarado
- [x] 3.6 Calcular el reparto de los tuits con saliencia de violencia presente por grupo de polaridad, derivándolo de la escala declarada y no del nombre del criterio, y dejarlo en los datos de la sección para la nota del paso 6.7

## 4. Configuración y umbrales

- [x] 4.1 Añadir a la celda 37 `MIN_FRECUENCIA_NUBE`, `TOP_TERMINOS_NUBE` y `MIN_TERMINOS_NUBE` (umbral del aviso de escasez), con comentario de qué hace cada uno
- [x] 4.2 Añadir los parámetros de trazado determinista: alto del panel, `gridSize`, rotación desactivada
- [x] 4.3 Incorporar los cinco parámetros a la ficha técnica de la sección 16, junto a los que ya se publican
- [x] 4.4 Revisar los umbrales contra los conteos reales y congelarlos antes de leer las nubes, dejando constancia del valor elegido y de por qué. Se añadió `MIN_SOPORTE_NUBE = 3`: sin él la nube ambivalente salía con 39 términos (22 de una sola ocurrencia) y nunca disparaba el aviso de escasez

## 5. Carga de la extensión y modos de falla

- [x] 5.1 Declarar `CDN_ECHARTS_WORDCLOUD` (echarts-wordcloud 2.x) junto a `CDN_ECHARTS`, en las mismas celdas donde hoy se declara el CDN
- [x] 5.2 Añadir el segundo marcador y el segundo `<script>` a `PLANTILLA_V3` en la celda 5
- [x] 5.3 Distinguir en el respaldo los dos modos de falla comprobando la disponibilidad del tipo de serie `wordCloud` tras la carga
- [x] 5.4 Hacer que, faltando la extensión, los cinco paneles de nube muestren un aviso que la nombre y el resto de la sección 16 siga dibujándose
- [x] 5.5 Probar los dos modos de falla bloqueando cada script por separado en el navegador

## 6. Paneles de las nubes

- [x] 6.1 Escribir el ayudante de JS que dibuja una nube con el `panel(...)` existente, recibiendo términos, pesos, color y rótulo del peso
- [x] 6.2 Dibujar las dos nubes descriptivas en tinta neutra, cada una declarando su universo y su número de tuits
- [x] 6.3 Añadir al bloque descriptivo la lectura de la colecta contra la rúbrica: qué trajo la consulta y qué reconoció la rúbrica
- [x] 6.4 Dibujar las tres nubes de polaridad con un color por grupo tomado de `PALETA`, declarando en cada panel que el tamaño es la z de log-odds y citando a Monroe, Colaresi y Quinn (2008)
- [x] 6.5 Mostrar en los chips de cada nube su número de tuits y de términos
- [x] 6.6 Mostrar el aviso de vocabulario escaso en las nubes por debajo del mínimo, y omitir con motivo la nube que se quede sin términos
- [x] 6.7 Añadir la nota de los tuits `sin_polaridad` con el reparto completo de los tuits con saliencia de violencia presente por grupo de polaridad (hoy 17 negativo, 4 sin polaridad, 3 positivo, 1 ambivalente), para que la nota enseñe con cifras que presencia no es valencia en lugar de afirmarlo
- [x] 6.8 Repetir en estos paneles la declaración de la traducción automática vigente en la sección 16
- [x] 6.9 Colocar los paneles al inicio de la sección 16, antes del mapa UMAP, separando el bloque descriptivo del comparativo

## 7. Verificación

- [ ] 7.1 Comprobar que la partición sigue cuadrando tras una corrida completa y que la aserción no salta
- [x] 7.2 Comprobar que «México» queda con z cercana a cero en las tres nubes de polaridad y no domina ninguna. Verificado con lemas reales: por frecuencia es el término n.º 1 de los tres grupos; por z cae al puesto 33 de 50 (positivo), 16 de 17 (negativo) y desaparece en ambivalente
- [ ] 7.3 Regenerar la página dos veces con los mismos datos y comprobar que las cinco nubes salen idénticas
- [ ] 7.4 Redimensionar la ventana y comprobar que la disposición no se recompone
- [ ] 7.5 Comprobar que el HTML exportado por la sección 17 trae las cinco nubes y funciona fuera del notebook
- [ ] 7.6 Leer las cinco nubes y escribir en la sección 18 cómo se leen y qué no se puede concluir de ellas

## 8. Tabla resumen de la sección 2

- [x] 8.1 En la celda 7, dar a los criterios de presencia una columna propia en la tabla del panel «Distribución de valencia · todo el corpus», separada de las columnas `nivel 1` a `nivel 5`
- [x] 8.2 Derivar la forma de la fila de la `escala` declarada del criterio, nunca de su nombre, para que añadir otro criterio de presencia no exija volver a tocar la tabla
- [x] 8.3 Comprobar que las columnas de valencia quedan sumables: que todos los números de una columna signifiquen lo mismo
- [x] 8.4 Comprobar que los totales por criterio siguen cuadrando con el corpus (25 + 2 604 + 2 = 2 631 para saliencia de violencia) y que ningún otro panel de la sección 2 cambia

## 9. Frecuencias fuera de Colab

- [x] 9.1 Partir las celdas de NLP por su frontera de acelerador: preparación de texto / embeddings y clusters, y spaCy / vocabulario y grafos / tópicos por cluster
- [x] 9.2 Poner un marcador `# === BLOQUE: <nombre> ===` al inicio de cada celda que el script necesita localizar
- [x] 9.3 Escribir `frecuencias_corpus.py`, que localiza los bloques por marcador, se detiene si falta alguno y ejecuta sólo los de CPU
- [x] 9.4 Calcular las frecuencias por corpus, grupo de rúbrica, polaridad y criterio, con ocurrencias y tuits en cada fila
- [x] 9.5 Publicar `frecuencias_grupos.csv` con el tamaño de cada grupo y si su corte es disjunto
- [x] 9.6 Verificar que el script corre sobre el corpus real y comprobar los totales contra la sección 2
- [ ] 9.7 Decidir qué hacer con las entidades que el NER parte por mayúsculas (`yonna` / `Yonna`) y con las que etiqueta sobre verbos («Tengo», «Pensé»)
- [ ] 9.8 Exportar estas mismas tablas desde la sección 17, para que el CSV local y el de Colab sean el mismo dato

## 10. Cruce criterio x valencia y nubes locales

- [x] 10.1 Anadir el corte criterio x valencia a las frecuencias, con la valencia tomada del nivel de ese criterio y no de la polaridad global
- [x] 10.2 Anadir la columna z a los CSV, calculada con el log_odds del propio notebook, vacia en los cortes que se solapan
- [x] 10.3 Declarar en frecuencias_grupos.csv el universo contra el que se contrasta cada grupo
- [x] 10.4 Escribir nubes_corpus.py, que lee los CSV y dibuja una nube por grupo en Apache ECharts sin volver a pasar spaCy
- [x] 10.5 Elegir el peso segun el corte: frecuencia si se solapa, z si admite uno-contra-resto, declarado en cada panel
- [x] 10.6 Soportar forma built-in y mascara embebida como data URI, con respaldo si la mascara no carga
- [x] 10.7 Arreglar el empalme de texto: una sola columna, 80 términos y rejilla 14. Dos columnas daban lienzos de la mitad de ancho, y nubes de geometría distinta no son comparables entre sí
- [x] 10.8 Distinguir «sin contraste» de «se solapa»: la nube del corpus decía que se solapaba con algo, y es el corpus entero
- [x] 10.9 Colorear codificando un dato: intensidad por peso en lemas, categoría de la entidad en entidades (`MX_*` del diccionario contra lo que reconoce el NER), con leyenda y piso de contraste 0.55
- [x] 10.10 Verificar renderizando en Chrome headless que las nubes dibujan, que no se empalman y que dos corridas dan capturas idénticas
- [x] 10.11 Colorear los lemas por categoria gramatical (ADJ evalua / NOUN tema / PROPN situa), reutilizando el filtro POS_LEMAS que ya existia y que tiraba la etiqueta
- [x] 10.12 Poner el TAMANO como eleccion de lectura en la pagina, no congelada al generarla: ocurrencias (por omision), tuits en que aparece, o z de log-odds donde el corte lo admite
- [x] 10.13 Avisar en cada nube que medida esta activa y que implica: con frecuencia los terminos comunes dominan, con z el tamano no es la valencia
- [x] 10.14 Escribir mascara_desde_trazo.py: separa el interior del exterior por conectividad (el blanco de dentro y el de fuera son el mismo color y no se pueden separar por umbral)
- [x] 10.15 Documentar que el area rellenable debe ser NEGRO PURO #000000: con (17,17,17) la nube sale vacia sin avisar, y eso no esta en la documentacion de la biblioteca
- [x] 10.16 Respetar la proporcion de la mascara: se estira al area de dibujo, y con un lienzo ancho una mascara cuadrada deforma la figura
- [x] 10.17 Avisar en el panel que con mascara se descartan terminos sin decir cuantos
- [x] 10.18 Anadir --fondo: dibujar la figura DETRAS de las palabras, alineada con el area de dibujo. Con la figura visible el balon se reconoce; como mascara invisible nunca se reconocio, porque una nube dibuja siluetas y la identidad de un balon esta en sus lineas internas
- [x] 10.19 Construir mascara y fondo desde el MISMO archivo: con dos encuadres distintos las palabras siguen a uno y el dibujo al otro, y se salen de la figura
- [x] 10.20 Hacer construir() consciente del alfa: convertir a gris volvia NEGRO el transparente, es decir trazo, e impedia usar el mismo PNG para mascara y fondo
- [x] 10.21 Anadir --tam y --curva para amplificar la diferencia de tamano, con el color siguiendo la misma curva
- [x] 10.22 Anadir --base (exponencial) y comprobar por que NO sirve: satura a las 4 ocurrencias, donde vive el 82% de los terminos, y deja del mismo tamano a terminos de 8 y de 106
- [x] 10.23 Poner TUITS como medida por omision: cuenta en cuantos tuits se dice algo, no cuantas veces se tecleo, asi que un tuit repetitivo no infla un termino
- [x] 10.25 Anadir lista de palabras funcion inglesas que sobreviven a la traduccion (37 terminos), excluidas del DIBUJO pero conservadas en los CSV
- [x] 10.26 Aplicar el soporte a la MEDIDA ACTIVA: filtraba por ocurrencias mientras se mostraban tuits, asi que un termino dicho 3 veces en un solo tuit pasaba como si tuviera respaldo
- [x] 10.27 Ajustar el area de dibujo por nube con la raiz del numero de terminos, y declararlo en un chip: sin esto una nube de 93 terminos se dibuja en la misma figura que una de 1000 y la letra se ve chica por sobrar lienzo, no por ser rara
- [x] 10.28 Anadir tema `bandera`: verde, blanco y rojo sobre negro, con los tonos aclarados respecto de los oficiales porque sobre negro no alcanzan el contraste legible. El color sigue codificando la categoria gramatical
- [x] 10.29 Mezclar el color hacia el FONDO y no siempre hacia el blanco: sobre negro, aclarar los terminos de peso bajo los hacia saltar en vez de apagarlos
- [ ] 10.24 El techo de --tam descarta el termino MAS frecuente: a 78 px «mexico» no cabia en ningun panel y desaparecia en silencio. Hacer que el panel cuente cuantos terminos se dibujaron de verdad, no en lineas internas: el balon no se reconoce porque su identidad son las costuras, y una nube dibuja siluetas, no estructura interna: con ella se descartan terminos que no caben y la silueta compite con el dato
