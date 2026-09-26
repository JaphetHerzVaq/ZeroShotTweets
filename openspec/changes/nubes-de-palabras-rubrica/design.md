## Context

El trabajo vive en un **notebook nuevo, `rediseno_zeroshot_colab_v4.ipynb`, derivado de la v3**, como cada change anterior de este proyecto: la v3 nació de la v2 y la dejó intacta. La sección 16 de la v3 ya tiene toda la materia prima: `NLP_TUIT` con una fila por tuit, la columna `lemas` de spaCy sobre la traducción, y `log_odds(cnt1, cnt2)` con prior informativo. Lo único que falta es la polaridad y los paneles.

Tres restricciones del código existente mandan sobre el diseño:

1. **La regla de codificación de la rúbrica vive en un solo sitio.** La celda 6 lo dice explícitamente: `clasificar_calificacion` es la única función que interpreta `aplicable` y `nivel`, y `CRITERIOS_RUBRICA` declara la `escala` de cada criterio (`valencia` o `presencia`). La polaridad es una lectura más de la rúbrica y pertenece ahí, no a la sección de NLP.
2. **La página es reproducible por norma.** `SEMILLA_NLP`, `SEMILLA_VALIDACION`, `huella_instrumento`, y la aserción que compara los textos de `BATERIA` contra `MISMA_FRASE` en la celda 30. Una figura que cambia de forma al redimensionar rompería esa norma sin avisar.
3. **La página declara lo que excluye.** `IDIOMAS_ESCASOS` se informa para que la exclusión sea visible «no para dibujarlos como si fueran comparables». Las nubes escasas heredan ese hábito.

Los tamaños de grupo son el hecho que más condiciona el diseño:

```
corpus completo                                 2 631
├─ no calificados                               2 487
└─ calificados                                    144
   ├─ positivo         algún 4-5, ningún 1-2       76
   ├─ negativo         algún 1-2, ningún 4-5       45
   ├─ ambivalente      sólo niveles 3              19
   └─ sin polaridad    sólo saliencia de violencia  4
```

Medición sobre las traducciones con el umbral vigente `MIN_FRECUENCIA_LOGODDS = 3`, tokenizando sin spaCy como aproximación: el prior de los 144 calificados deja 184 tipos; por grupo sobreviven ~95 (positivo), ~43 (negativo), ~10 (ambivalente) y 0 (sin polaridad). Es un proxy —la lematización junta formas y el filtro `NOUN/PROPN/ADJ` quita verbos y adverbios, y los dos efectos se compensan a grandes rasgos—, pero el orden de magnitud es el que manda: **la nube ambivalente es de una o dos decenas de términos**.

## Goals / Non-Goals

**Goals:**

- Poner la polaridad de la rúbrica al alcance de cualquier figura de la v4, derivada una sola vez y comprobada.
- Cinco nubes en la sección 16 que no se puedan confundir entre sí: dos que describen y tres que comparan, con el peso declarado en cada panel.
- Que la nube más pobre se lea como pobre, no como las otras cuatro.
- Reutilizar `log_odds` sin duplicarlo y sin que la página nombre mal los grupos.

**Non-Goals:**

- Volver a calificar, cambiar la rúbrica o tocar la colisión `aplicable`/nivel 0 del motor de EvaluadorTweets.
- Sacar conclusiones de las nubes de polaridad. Son descriptivas de un corpus de 45 a 76 tuits calificados por un modelo de lenguaje, no por codificadores humanos.
- Sustituir el panel de log-odds que ya existe entre calificados y no calificados, ni el de tópicos por cluster.
- Añadir la polaridad a las figuras de las secciones 14 y 15. La columna queda disponible; usarla ahí es otro change.

## Decisions

### Polos primero, ambivalencia como residuo

La definición directa —«ambivalente = algún criterio en nivel 3»— produce tres tuits en dos grupos a la vez y una partición de 141 sobre 144. Los tres casos, leídos:

```
atmósfera 4 · imagen 3          "¡Llegamos a México para el viaje de cumpleaños…"
atmósfera 4 · imagen 3          "los llamados izakayas en América Latina, incluido México…"
atmósfera 3 · imagen 2 · pol 1  "un pequeño pueblo del sur de México, un carterista…"
```

Ninguno es ambivalente: los dos primeros son entusiastas y el tercero es un robo. La ambivalencia está en un criterio secundario. La regla que se adopta —positivo si hay algún 4–5 y ningún 1–2, negativo si hay algún 1–2 y ningún 4–5, ambivalente sólo si todos los criterios de valencia presentes valen 3— da 76 + 45 + 19 + 4 = 144 exacto, disjunto y exhaustivo.

**Alternativas descartadas:** promediar los niveles de los criterios presentes (mezcla constructos que §14 declara distintos: el afecto hacia el país y el juicio estético no se promedian); usar sólo el criterio de atmósfera (tira 38 tuits calificados por los otros dos); dejar que un tuit aparezca en dos nubes (rompe la lectura de uno contra resto y hace que los tamaños no sumen).

La disjunción se fija con una aserción, no con un comentario. No está garantizada por la rúbrica: hoy se cumple porque ningún tuit tiene a la vez un criterio en 1–2 y otro en 4–5, y eso puede romperse en otra corrida. Si se rompe, la ejecución se detiene y nombra los tuits en conflicto.

### `polaridad` se deriva en la celda 6, no en la 39

`RUBRICA_TUIT` ya tiene `nivel_<corto>` y `clase_<corto>` por criterio y deriva ahí `calificado`, `con_faltante` y `grupo`. La polaridad es una columna hermana de esas tres y se calcula con la misma información. Ponerla en la sección de NLP obligaría a reconstruir la lectura de niveles a 600 líneas de distancia de `clasificar_calificacion`, que es justo lo que el comentario de esa celda prohíbe.

Consecuencia deliberada: la columna queda disponible para las secciones 14 y 15 aunque este change no la use ahí.

### Dos pesos, y el porqué de cada uno

| nubes | peso | razón |
|---|---|---|
| corpus completo, calificados | frecuencia de lema | describen un universo; la pregunta es «de qué habla esto» |
| positivo, negativo, ambivalente | z de log-odds, uno contra resto | comparan; con 19 a 76 tuits la frecuencia cruda mide sobre todo el tamaño del grupo |

El estimador de Monroe, Colaresi y Quinn (2008) existe precisamente porque la frecuencia miente cuando los grupos son chicos y desiguales, y encoge hacia cero los términos sin evidencia. Eso resuelve de paso el problema del ancla: «México» aparece en todos los grupos por construcción —todas las consultas anclan ahí— y obtiene z ≈ 0, así que se encoge solo, sin lista negra manual que haya que mantener.

Usar frecuencia cruda en las tres nubes de polaridad contradiría, en la misma página y a un panel de distancia, el criterio del contraste de vocabulario que ya está publicado ahí.

### El prior son los 140 con polaridad, no los 144

Los 4 tuits calificados sólo por saliencia de violencia no tienen polaridad, así que tampoco pueden ser «el resto» de una polaridad. Entran en las dos nubes descriptivas y en la nota; quedan fuera de las tres comparaciones y de su prior. La sección 14 ya declara este criterio para ese criterio: «Constructos cercanos: ambos son presencia, no valencia».

Los datos lo confirman. De los 25 tuits con saliencia de violencia presente:

```
negativo         17
sin_polaridad     4
positivo          3
ambivalente       1
```

Los 4 que no son negativos son todos la misma figura —México es maravilloso *a pesar de* o *si evitas* el peligro—:

```
atm=5 img=4 vio=1   "una de las mejores noches que he tenido… ese paseo en
                     bote fue jodidamente increíble. Ciudad de México"
atm=5 img=5 vio=1   "no tenía ni idea de que México fuera un país tan
                     maravilloso"
atm=5 pol=4 vio=1   "la cálida hospitalidad de los mexicanos hizo que la
                     diversión se duplicara. El nivel de peligro…"
atm=3 img=3 vio=1   "les recomiendo México… si evitas que te estafen y no
                     caminas de noche"
```

Mencionan violencia y aprecian el país. Si la saliencia de violencia contribuyera a la polaridad, los cuatro se arrastrarían a `negativo`, que sería falso. Que 17 de 25 sí sean negativos es **correlación, no definición**: es exactamente la distinción que la nota del panel tiene que enseñar.

### `log_odds` se generaliza por los rótulos, no por el cálculo

La función ya recibe dos `Counter` y no está atada a nada. Lo cableado es el retorno —llaves `calificados` y `no_calificados`, campos `n_calificados` y `n_no_calificados`— y el texto del panel en la celda 41: «z > 0 es característico de los calificados». Se parametrizan los nombres de los dos lados; el cálculo no se toca. Así el panel existente sigue igual y los nuevos dicen «positivo» donde corresponde.

### Trazado determinista

`echarts-wordcloud` envuelve wordcloud2.js, que coloca por espiral sobre el canvas: el resultado depende del tamaño del lienzo y, con rotación habilitada, de un aleatorio. Se fija el alto del panel, se desactiva la rotación (`rotationRange: [0, 0]`), se fija `gridSize`, y el orden de entrada de los términos se ordena por peso de forma estable con desempate alfabético para que dos términos con la misma z no se intercambien entre corridas. Los parámetros van a la ficha técnica, como el resto de la sección.

**Alternativa descartada:** dejar la rotación por estética. Una figura de tesis que cambia de forma cada vez que se regenera el HTML no se puede citar.

### Segunda dependencia de CDN con su propio aviso

`PLANTILLA_V3` tiene hoy un solo marcador `__CDN__` y un respaldo que asume un único modo de falla. Con la extensión aparecen dos:

```
echarts ✗                  → aviso actual, la página entera no dibuja
echarts ✓ + wordcloud ✗    → hoy: cinco paneles vacíos, en silencio
                             con este change: aviso en esos cinco paneles,
                             el resto de la sección dibuja normal
```

La comprobación es la presencia del tipo de serie `wordCloud` tras cargar el script. El resto de los paneles no depende de la extensión y debe seguir funcionando.

### Colores de la paleta existente

`PALETA` está declarada con pares validados para visión con deficiencia de color, y el panel de log-odds actual ya usa `#1c5cab` para z > 0 y `#898781` para z < 0. Las dos nubes descriptivas van en tinta neutra porque ahí el color no codifica nada; las tres de polaridad toman una tinta por grupo de la paleta. Colorear término por término al azar —el valor por omisión de muchas nubes— sugeriría un significado que no existe.

### La tabla de la §2 comete el mismo error de categoría, y se corrige acotado a ella

La tabla resumen del panel «Distribución de valencia · todo el corpus» se construye así:

```js
tabla(['criterio','escala','nivel 1','nivel 2','nivel 3','nivel 4','nivel 5','ausencia','bloqueados'], filasT)
```

En la columna «nivel 1», para los tres criterios de valencia, el número son tuits de odio, desprecio o juicio fuertemente negativo. Para la saliencia de violencia son los 25 tuits que **mencionan** violencia. Dos significados en una columna, y quien la lea de arriba abajo suma 16 + 5 + 9 + 25.

El resto de la página ya lo hace bien: el gráfico apilado filtra `valCrits` y deja la violencia fuera, el panel propio de ese criterio dice «Criterio de presencia… No es una escala de valencia», y la propia tabla trae una columna `escala` que dice `presencia`. La información para leerla está ahí; el encabezado la contradice.

La corrección se limita a esa tabla: la cuenta de un criterio de presencia no comparte columna con los niveles de valencia. Ni se rediseña la sección 2, ni se tocan los demás paneles, que ya derivan su comportamiento de la escala declarada.

**Alternativa descartada:** dejarlo y explicarlo en una nota al pie. La tabla seguiría invitando a sumar la columna, y este change existe justamente para que la página deje de mezclar presencia con valencia.

## Risks / Trade-offs

- **La nube ambivalente tendrá una o dos decenas de términos** → El panel declara en sus chips cuántos tuits y cuántos términos la sostienen, y por debajo del mínimo declarado muestra un aviso en lugar de dibujarla como si fuera comparable. Si no queda ningún término, se omite con el motivo.
- **Cinco nubes juntas invitan a restarlas con el ojo** → Las dos descriptivas y las tres comparativas se separan en bloques distintos con su peso declarado en el encabezado de cada uno, para que no se lean como una serie homogénea.
- **La partición disjunta se cumple hoy por los datos, no por la rúbrica** → Aserción que detiene la ejecución y nombra los tuits en conflicto, en vez de un comentario que se puede ignorar.
- **El proxy de vocabulario se midió sin spaCy** → Los umbrales (`MIN_FRECUENCIA_NUBE`, mínimo de términos para el aviso) se revisan contra los conteos reales en la primera corrida con GPU y se congelan antes de leer las nubes, no después.
- **Las nubes de polaridad describen la rúbrica aplicada por un modelo, no por personas** → La declaración ya vigente en toda la sección 16 se repite en estos paneles, junto con la de la traducción automática y las cinco traducciones completadas a mano el 13/09.
- **Segundo punto de falla de red** → Aviso propio por panel; el resto de la sección 16 no se ve afectado.
- **La sección 16 crece** → Las nubes se colocan al inicio de la sección, antes del mapa UMAP, que es la figura que más contexto exige; las nubes son la entrada barata y el mapa el desarrollo.

## Migration Plan

La v3 queda intacta y la v4 es un archivo nuevo: el retroceso completo es no abrir la v4. No hay migración de datos ni cambio de formato de salida. La página se regenera desde el notebook y `pagina_v3()` incorpora los paneles nuevos sin tocar los existentes. El retroceso es quitar los paneles y el segundo `<script>`: nada más depende de ellos.

## Open Questions

- ¿Los umbrales finales (`MIN_FRECUENCIA_NUBE`, número máximo de términos por nube, mínimo de términos para el aviso de escasez) se mantienen iguales a los del log-odds vigente o se separan? Se decide con los conteos reales de la primera corrida y se congela antes de leer las figuras.
- ¿Las entidades merecen su propia nube, como ya tienen su propio panel de log-odds? Fuera de alcance aquí; se decide después de ver las de lemas.
