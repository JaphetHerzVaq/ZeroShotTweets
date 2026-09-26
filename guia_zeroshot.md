# Cómo funciona el zero-shot, explicado desde cero

*Guía del instrumento de medición de este proyecto. No hace falta saber programar ni
estadística: solo sumar, restar y dividir.*

---

# PARTE I — LOS FUNDAMENTOS

## 1. El problema que queremos resolver

Tenemos 2 562 tuits de turistas. Queremos saber, de cada uno:

- ¿Habla del ambiente que se vivió? Y si habla, ¿fue bueno o malo?
- ¿Habla de la comida y la cultura? ¿Bien o mal?
- ¿Habla del gobierno? ¿Bien o mal?

Nadie los ha leído uno por uno, y son demasiados para hacerlo a mano.

### La forma tradicional: entrenar un modelo

1. Lees 3 000 tuits y los etiquetas a mano: «este habla bien del ambiente», «este no».
2. Le enseñas esos ejemplos a un programa.
3. El programa aprende el patrón y etiqueta los que faltan.

El problema es el paso 1: semanas de trabajo. Y si mañana añades la dimensión «seguridad»,
empiezas de nuevo.

### La forma zero-shot

**Zero-shot** significa literalmente *«con cero ejemplos»*. No le enseñas nada: le haces la
pregunta y responde.

No es magia. El truco es usar un modelo ya entrenado para **otra** tarea, y reformular tu
pregunta para que encaje en lo que ese modelo ya sabe hacer.

---

## 2. Vocabulario de NLI

Todo el método se apoya en una tarea clásica llamada **inferencia de lenguaje natural**
(*Natural Language Inference*, NLI). Estos seis términos son todo lo que hay que aprender.

### Premisa

**El texto de partida. Lo que damos por cierto.**

En este proyecto, la premisa es siempre **el tuit**. No lo escribimos nosotros: viene del
corpus, tal cual lo publicó el turista.

```
   PREMISA:  "The atmosphere in the stadium was electric,
              best night of my life!"
```

### Hipótesis

**Una afirmación cuya relación con la premisa queremos juzgar.**

La hipótesis **sí la escribimos nosotros**. Es nuestra pregunta, disfrazada de afirmación.
Aquí está toda la responsabilidad del investigador: la hipótesis *es* el instrumento de
medición.

```
   HIPÓTESIS:  "Este texto sobre Mexico dice que el ambiente
                que se vivio fue alegre y emocionante."
```

> **Importante:** la hipótesis nunca es una pregunta. El modelo no sabe responder preguntas.
> Sabe juzgar si una afirmación se sigue de un texto.

### Las tres relaciones posibles

Dada una premisa y una hipótesis, hay exactamente tres respuestas:

| Relación | Significa | Ejemplo (premisa: *«El perro negro corre por el parque»*) |
|---|---|---|
| **Entailment**<br>(implicación) | Si la premisa es verdad, la hipótesis **también** | *«Hay un animal afuera»* → se deduce |
| **Neutral** | Puede ser, pero la premisa **no lo dice** | *«El perro tiene tres años»* → ni sí ni no |
| **Contradiction**<br>(contradicción) | Si la premisa es verdad, la hipótesis es **falsa** | *«No hay ningún perro»* → imposible |

Para el zero-shot **solo nos interesa el entailment**. Nuestra pregunta siempre es «¿qué tan
fuerte se deduce esto?».

### Etiqueta candidata

**La parte variable de la hipótesis: el concepto que queremos medir.**

```
   etiqueta:  "el ambiente que se vivio fue alegre y emocionante"
```

Se llama *candidata* porque se le ofrecen varias al modelo y él decide cuál encaja mejor.

### Plantilla

**El molde fijo que convierte una etiqueta en una hipótesis completa.**

```
   PLANTILLA:  "Este texto sobre Mexico dice que {}."
                                                 ▲
                                                 │
   ETIQUETA:   "el ambiente que se vivio fue alegre y emocionante"
                                                 │
                                                 ▼
   HIPÓTESIS:  "Este texto sobre Mexico dice que el ambiente
                que se vivio fue alegre y emocionante."
```

La plantilla es **idéntica para todas las etiquetas y todos los tuits**. Eso importará mucho
en la sección 10.

### El modelo

Este proyecto usa **XLM-RoBERTa-large-XNLI**. Dos rasgos relevantes:

- **XNLI** = fue entrenado con cientos de miles de tríos premisa/hipótesis/relación.
- **XLM** = *cross-lingual*. Entrenado en 15 idiomas a la vez, así que la hipótesis puede ir en
  español y el tuit en japonés. Por eso las hipótesis de este proyecto están **todas en
  español**: así el instrumento es idéntico para todos los idiomas del corpus.

> **Detalle práctico:** cada texto se corta a 512 caracteres antes de entrar. Para tuits casi
> nunca importa, pero conviene saberlo.

---

## 3. El truco: convertir tu pregunta en una hipótesis

Aquí está la idea central de todo el zero-shot.

```
  TU TUIT        ────────►   PREMISA
  TU PREGUNTA    ────────►   HIPÓTESIS (vía plantilla)
```

Ejemplo completo:

```
PREMISA (el tuit, del corpus):
   "The atmosphere in the stadium was electric, best night of my life!"

HIPÓTESIS (nuestra, construida con la plantilla):
   "Este texto sobre Mexico dice que el ambiente que se vivio fue
    alegre y emocionante."

PREGUNTA AL MODELO:
   ¿Se deduce la hipótesis de la premisa?

RESPUESTA:
   Sí, con fuerza.  →  entailment alto
```

Cambias la etiqueta y ya estás midiendo otra cosa. Esa es la flexibilidad del método — y
también su punto débil, porque **cambiar las hipótesis cambia los resultados**, igual que
cambiar las preguntas de una encuesta cambia las respuestas.

---

## 4. Los números crudos: los *logits*

El modelo no devuelve «sí» o «no». Devuelve tres números, uno por relación:

```
   entailment    :   2.1
   neutral       :   0.9
   contradiction :  -1.4
```

Se llaman **logits**. Propiedades:

- Pueden ser negativos.
- No tienen tope ni suelo.
- **No son probabilidades.** No suman 1 ni nada en particular.
- Solo significan algo **comparados entre sí**. Que un logit valga 2.1 no dice nada; que 2.1
  sea mayor que 0.9 sí.

De los tres, **nos quedamos solo con el de entailment** y descartamos los otros dos.

---

## 5. Softmax: de logits a probabilidades

### Qué problema resuelve

Tienes números sueltos sin escala y quieres porcentajes interpretables que sumen 100 %. A eso
se le llama **normalizar**, y la herramienta estándar es el **softmax**.

### Cómo funciona, en dos pasos

**Paso 1 — exponencial.** A cada número le aplicas `e` elevado a ese número.

Esto hace dos cosas a la vez: vuelve todo **positivo** (necesario, porque una probabilidad
negativa no existe) y **exagera las diferencias** (un número un poco mayor se vuelve mucho
mayor).

**Paso 2 — dividir entre el total.** Así la suma da exactamente 1.

```
                    e^(logit de esta opción)
   P(opción)  =  ─────────────────────────────────────
                  suma de e^(logit) de TODAS las opciones
```

### Ejemplo numérico completo

Logits de entailment: `2.1`, `0.4`, `−0.3`.

```
   Paso 1: exponencial
      e^( 2.1)  =  8.166
      e^( 0.4)  =  1.492
      e^(-0.3)  =  0.741
      ─────────────────────
      suma      = 10.399

   Paso 2: dividir
      8.166 / 10.399  =  0.785      ← 78.5 %
      1.492 / 10.399  =  0.143      ← 14.3 %
      0.741 / 10.399  =  0.071      ←  7.1 %
                         ───────
                          1.000      ← siempre
```

Fíjate en el efecto de la exponencial: la diferencia entre 2.1 y 0.4 no era enorme, pero la
diferencia entre 78.5 % y 14.3 % sí lo es. **Softmax amplifica al ganador.**

### Tres propiedades que hay que tener presentes

**a) Siempre suma 1.** No es una opción, es la definición.

**b) Siempre reparte TODO el pastel.** Aunque las tres opciones sean malísimas, softmax
reparte el 100 % entre ellas. **No puede decir «ninguna de las tres».** Esta propiedad, que
parece inofensiva, es la causa del problema que veremos en la sección 8.

**c) Es invariante al desplazamiento.** Si le sumas la misma constante a todos los logits, el
resultado no cambia:

```
   softmax(2.1, 0.4, -0.3)  =  softmax(3.1, 1.4, 0.7)   ← idénticos
                                (le sumamos 1 a los tres)
```

La razón es aritmética: `e^(x+c) = e^x · e^c`, y ese `e^c` aparece arriba y abajo en la
división, así que se cancela.

> Esta tercera propiedad parece un tecnicismo. En la sección 10 verás que de ella depende una
> de las decisiones de diseño más importantes del proyecto.

---

## 6. Los dos modos de normalización

Hay **dos formas** de aplicar softmax a un problema zero-shot, y la elección lo cambia todo.

### Modo A — `multi_label=False`: las etiquetas **compiten**

Le das varias etiquetas y softmax las normaliza **juntas**. Se reparten un pastel de tamaño
fijo: si una sube, las otras bajan por fuerza.

Tuit: *«The atmosphere in the stadium was electric, best night of my life!»*

| Etiqueta | Hipótesis | logit |
|---|---|---|
| `pos` | …el ambiente fue alegre y emocionante | **2.1** |
| `neg` | …el ambiente fue desagradable y estresante | **0.4** |
| `na`  | …se habla de otro tema, ajeno al ambiente | **−0.3** |

Aplicando el softmax de la sección anterior:

```
   P(pos) = 0.785      P(neg) = 0.143      P(na) = 0.071
```

Como barra apilada — que es exactamente la figura 5 del proyecto:

```
   ├────────────────────────────────────────┼──────────┼─────┤
   │            pos  0.785                  │ neg 0.143│na .07│
   └────────────────────────────────────────┴──────────┴─────┘
   0                                                          1
```

### Modo B — `multi_label=True`: cada etiqueta **va por libre**

Softmax **no** se aplica entre etiquetas, sino **dentro** de cada una: compara su entailment
contra su contradiction, y nada más.

```
                      e^(logit entailment)
   P(etiqueta)  =  ──────────────────────────────────────────
                   e^(logit entailment) + e^(logit contradiction)
```

Ejemplo, etiqueta *«la comida, los lugares o la cultura»*:

```
   logit entailment     =  1.8   →   e^( 1.8) = 6.050
   logit contradiction  = -0.6   →   e^(-0.6) = 0.549
                                     ───────────────
                                     suma     = 6.599

   P  =  6.050 / 6.599  =  0.917       ← 91.7 %
```

Cada etiqueta recibe su nota independiente. **No suman 1**, ni tienen por qué: pueden salir
todas altas, todas bajas o mezcladas.

### La comparación que importa

| | `multi_label=False` | `multi_label=True` |
|---|---|---|
| Las etiquetas… | compiten por un pastel fijo | se juzgan por separado |
| ¿Suman 1? | Sí, siempre | No |
| Sirve para… | elegir **entre** opciones | preguntar «¿sí o no?» a cada una |
| Si ninguna encaja… | **reparte igual entre malas** | todas salen bajas, correctamente |

Esa última fila es el tema de la sección 8.

---

# PARTE II — EL INSTRUMENTO DE ESTE PROYECTO

## 7. Los dos números: relevancia y valencia

### Relevancia — ¿habló del tema?

```
   relevancia  ∈  [0, 1]

   0  =  el tuit no toca esta dimensión
   1  =  la trata de lleno
```

### Valencia — ¿habló bien o mal?

```
   valencia  =  P(positiva) − P(negativa)     ∈  [-1, +1]

   -1  =  demoledor
    0  =  neutro o ambivalente
   +1  =  entusiasta
```

Con el ejemplo del estadio: `valencia = 0.785 − 0.143 = +0.64`.

### Por qué hacen falta dos números y no uno

Imagina que solo tuvieras la valencia, y te encuentras un tuit con valencia `0.0`:

```
   ¿El turista fue al partido y el ambiente le pareció del montón?
                             ...o...
   ¿El turista escribió sobre el tráfico y jamás mencionó el ambiente?
```

**Son cosas distintas con el mismo número.** A eso se le llama el **cero ambiguo**, y es el
defecto que este proyecto existe para corregir.

La relevancia lo desambigua:

```
   valencia 0.0  +  relevancia 0.9   →   habló del tema, le pareció normal
   valencia 0.0  +  relevancia 0.1   →   ni siquiera habló del tema
```

---

## 8. El caso `na`: por qué el primer diseño falló

Esta sección es la más importante de la guía. Explica una decisión de diseño que se tomó, se
midió, y **resultó estar equivocada** — y cómo se corrigió.

### El diseño original

Tres hipótesis compitiendo en un solo softmax (`multi_label=False`):

```
   pos  :  "el ambiente fue alegre y emocionante"
   neg  :  "el ambiente fue desagradable y estresante"
   na   :  "no menciona el ambiente ni el estado de animo"     ← la clave

   valencia   = P(pos) − P(neg)
   relevancia = 1 − P(na)
```

`na` significa *not applicable*: «no aplica». La idea era elegante: si el tuit no habla del
tema, `na` ganará, `P(na)` será alta y la relevancia saldrá baja.

### Lo que pasó en realidad

De **2 562 tuits, ni uno solo** bajó de 0.45 de relevancia. El umbral estaba en 0.30. La
banda de «no habló del tema» salió **completamente vacía**.

Y peor: en las pruebas controladas se incluyó una frase escrita a propósito para no hablar de
ninguna dimensión. Debía dar relevancia ≈ 0. **Dio 0.83.**

### Causa nº 1: el suelo del softmax

Toma un tuit genuinamente ajeno al tema:

> *«El partido empezó a las ocho de la noche.»*

No habla del ambiente. Pero tampoco habla claramente de «otro tema ajeno al ambiente»:
simplemente no habla de nada relacionado. Los **tres** logits salen bajos y parecidos:

| Etiqueta | logit |
|---|---|
| `pos` | −1.2 |
| `neg` | −1.3 |
| `na`  | −0.9 |

```
   e^(-1.2) = 0.301
   e^(-1.3) = 0.273
   e^(-0.9) = 0.407
   ──────────────────
   suma     = 0.981

   P(pos) = 0.307     P(neg) = 0.278     P(na) = 0.415

   relevancia = 1 − 0.415 = 0.585
```

**`na` ganó, y aun así la relevancia salió 0.59.** El tuit pasa como relevante.

Esto es la propiedad (b) de la sección 5 mordiendo: **softmax siempre reparte todo el
pastel**. No puede decir «ninguna de las tres».

Llevado al extremo, si los tres logits fueran idénticos:

```
   P(pos) = P(neg) = P(na) = 1/3

   relevancia = 1 − 1/3 = 0.667
```

```
   ┌────────────────────────────────────────────────┐
   │  Un texto PERFECTAMENTE mudo  →  relevancia 0.67│
   │                                                 │
   │  No es un error del modelo.                     │
   │  Es aritmética:  1 − 1/3 = 2/3.                 │
   │  Es un SUELO ESTRUCTURAL del diseño.            │
   └────────────────────────────────────────────────┘
```

Para que la relevancia bajara de 0.30, `na` tendría que llevarse **más del 70 %** del pastel,
o sea ganarles por goleada a las otras dos. Y eso no podía pasar, por una segunda razón.

### Causa nº 2: las negaciones envenenan al modelo

La hipótesis era *«**no** menciona el ambiente **ni** el estado de ánimo»*. Una frase
**negada**. Eso es un problema serio con modelos NLI:

**El sesgo de la anotación.** Los datos de entrenamiento (MNLI/XNLI) se construyeron pidiendo
a personas que escribieran contradicciones, y la forma más fácil de contradecir algo es
negarlo. Resultado documentado: el modelo aprendió que *«no»*, *«nunca»*, *«ni»* son señales
de **contradiction**. Tu hipótesis es verdadera, pero llega vestida de contradicción y su
entailment queda deprimido.

**La composición absurda.** Metida en la plantilla queda:

```
   "Este texto sobre Mexico dice que no menciona el ambiente."
```

Un texto no «dice» que no menciona algo. Es una frase autorreferente y rara, del tipo que el
modelo nunca vio en su entrenamiento.

### El diagnóstico final

```
   `na` era la etiqueta que MÁS necesitaba ganar
   y la que PEOR equipada estaba para hacerlo.
```

Y lo decisivo: **ninguna redacción mejor de `na` podía arreglarlo**, porque el suelo de ⅔ no
depende de cómo esté escrita la frase. Es de la estructura.

### La solución: sacar la relevancia de la competencia

```
   ETAPA 1 — LA COMPUERTA                        (multi_label = TRUE)
   ┌───────────────────────────────────────────────────────────────┐
   │  "Este texto sobre Mexico habla de las emociones y el          │
   │   ambiente que se viven."                                      │
   │                                                                │
   │   · nota independiente, no compite con nadie                   │
   │   · NO hay ninguna negación                                    │
   │   · NO hay pastel que repartir  →  NO hay suelo                │
   │                                                                │
   │   relevancia = esa nota                                        │
   └───────────────────────────────────────────────────────────────┘

   ETAPA 2 — LA VALENCIA                         (multi_label = FALSE)
   ┌───────────────────────────────────────────────────────────────┐
   │  pos: "...el ambiente que se vivio fue alegre y emocionante"   │
   │  neg: "...el ambiente que se vivio fue desagradable y          │
   │        estresante"                                             │
   │                                                                │
   │   · solo DOS etiquetas: contraste puro de polaridad            │
   │                                                                │
   │   valencia = P(pos) − P(neg)                                   │
   └───────────────────────────────────────────────────────────────┘
```

Con el mismo tuit del partido:

```
   logit entailment    = -1.5   →  e^(-1.5) = 0.223
   logit contradiction = +1.2   →  e^( 1.2) = 3.320
                                   ──────────────
                                   suma     = 3.543

   relevancia = 0.223 / 3.543 = 0.063      ← correctamente mudo
```

De 0.59 a 0.06 con el mismo modelo y el mismo tuit. Lo único que cambió fue **dónde** se
normaliza.

### El efecto secundario que hay que entender

En la etapa 2 solo hay dos opciones, así que el modelo está **obligado a elegir bando** aunque
el tuit no venga al caso. Al tuit del partido le saldrá alguna valencia — quizá +0.4, quizá
−0.7 — y será **basura**.

Eso no es un fallo, es el diseño: **la compuerta decide si la valencia se mira o no.** Es el
error de lectura más fácil de cometer, y volvemos a él en la sección 12.

### Lo que se ganó de propina

En el diseño viejo, como las tres probabilidades sumaban 1:

```
   |valencia| = |P(pos) − P(neg)| ≤ P(pos) + P(neg) = 1 − P(na) = relevancia
```

O sea `|valencia| ≤ relevancia`, **siempre**. Los dos ejes estaban atados por aritmética.
Ahora se calculan por separado y esa atadura desaparece — que es lo correcto, porque nunca fue
una propiedad del fenómeno, solo del acoplamiento.

---

## 9. Cómo se construyeron las hipótesis

Las hipótesis no se escriben «a ver qué suena bien». Cada palabra responde a una regla, y cada
regla salió de un fallo observado.

### Regla 1 — Estructura paralela entre `pos` y `neg`

`pos` y `neg` deben ser **idénticas salvo la polaridad**: mismo sujeto, misma construcción
gramatical, misma longitud.

Si difieren en algo más, el softmax no está comparando polaridad — está comparando dos frases
distintas, y no sabes cuál diferencia pesó.

### Regla 2 — Adjetivos de intensidad equivalente

```
   ✗ ANTES:  pos: "hermosos e impresionantes"
             neg: "decepcionantes y poco atractivos"
```

«Hermosos e impresionantes» son elogios fuertes. «**Poco** atractivos» es una negación
suavizada — mucho más tibia. Peor aún: es un **atenuante** (*downtoner*) sobre un adjetivo
positivo, y los modelos NLI son notoriamente insensibles a los atenuantes. La palabra
«atractivos» ancla léxicamente hacia lo positivo aunque vaya precedida de «poco».

Resultado: la valencia se inclinaba hacia arriba **por redacción**, no por contenido.

```
   ✓ AHORA:  pos: "hermosa e impresionante"
             neg: "fea y decepcionante"
```

Antónimos directos, sin atenuantes, misma fuerza.

### Regla 3 — Nada de sujetos conjuntivos

Esta fue la más costosa de descubrir.

```
   ✗ ANTES:  "la comida, los lugares Y la cultura son hermosos"
```

Entrañar una conjunción exige **los tres** elementos. Un tuit que solo habla de tacos no
entraña una afirmación sobre comida **y** lugares **y** cultura. El modelo le da un valor
intermedio… **y se lo da igual a `pos` que a `neg`**, porque ambas comparten los tres sujetos.

Al restarlas, se cancelan:

```
   P(pos) ≈ 0.52     P(neg) ≈ 0.48     →     valencia ≈ +0.04
```

La nube entera quedaba aplastada contra el cero. Mientras tanto `atmosfera`, con un solo
sujeto («el ambiente»), sí se decidía y llenaba todo el rango. La comparación entre ambas
señaló al culpable.

```
   ✓ AHORA:  "la cultura del lugar, como su comida y sus sitios, ..."
```

**Hiperónimo + ejemplificación.** «La cultura del lugar» es el concepto general; «como su
comida y sus sitios» son ejemplos. Un tuit solo de comida **sí** puede entrañar esto vía el
ejemplar, y los tres sustantivos siguen presentes como anclas léxicas.

### Regla 4 — Las hipótesis, todas en un solo idioma

El corpus tiene tuits en inglés, japonés, español y más. Las hipótesis están **todas en
español**, porque el modelo es translingüístico.

La razón es de validez, no de comodidad: si tradujeras las hipótesis a cada idioma, cualquier
diferencia entre idiomas podría venir de la traducción y no del contenido. Con una sola
versión, **el instrumento es literalmente idéntico para todos**.

### Regla 5 — Que discriminen entre dimensiones

La hipótesis de una dimensión no debe ser entrañable por un texto de otra. En las pruebas se
detectó que una frase sobre violencia puntuaba +0.29 en imagen cultural — más que el propio
control. Eso es **contaminación**, y se corrige afilando los sujetos.

### Regla 6 — `na` en afirmativo (cuando se usa)

```
   ✗ ANTES:  "no menciona el ambiente ni el estado de animo"
   ✓ AHORA:  "se habla de otro tema, ajeno al ambiente y a las emociones"
```

Mismo significado, cero marcadores de negación. Por las razones de la sección 8.

### Regla 7 — Ningún nombre de lugar dentro de la etiqueta

Ver la sección siguiente: tiene su propio razonamiento y es sutil.

### Y la regla que gobierna a todas: contra qué se ajusta

> Las hipótesis se afinan contra un **banco de frases de prueba escritas a propósito**, con
> contenido controlado, del que se sabe de antemano qué debería salir.
>
> **Nunca contra los resultados del corpus.**

Reescribir las hipótesis hasta que los turistas «salgan» como esperabas es elegir el
instrumento por la respuesta que produce. Eso no se sostiene en una defensa de tesis.

Por eso, además, las hipótesis se citan **palabra por palabra** en el documento final, igual
que se cita un libro de códigos.

---

## 10. La decisión del ancla geográfica

La tesis mide la imagen de **México**, así que el instrumento debe estar anclado ahí. La
pregunta es **dónde** poner el ancla. Hay dos opciones, y no son equivalentes.

### Opción A — dentro de cada etiqueta

```
   pos:  "el ambiente EN MEXICO fue alegre"
   neg:  "el ambiente EN MEXICO fue desagradable"
   na :  "NO menciona el ambiente ... EN MEXICO"
```

### Opción B — en la plantilla (la elegida)

```
   PLANTILLA:  "Este texto sobre Mexico dice que {}."

   pos:  "el ambiente fue alegre"
   neg:  "el ambiente fue desagradable"
   na :  "se habla de otro tema, ajeno al ambiente"
```

### Por qué la opción A es una trampa

Recuerda la propiedad (c) del softmax: **es invariante al desplazamiento**. Si algo afecta a
las tres etiquetas **por igual**, se cancela y no altera el resultado.

En la plantilla, el ancla es un prefijo idéntico para las tres. Se cancela. ✓

Dentro de las etiquetas, **no** afecta por igual:

```
   pos, neg  →  son AFIRMACIONES. Añadirles "en México" las vuelve
                MÁS DIFÍCILES de entrañar: ahora hay que sostener
                también que ocurrió en México.

   na        →  es una NEGACIÓN. Añadirle "en México" la vuelve
                MÁS FÁCIL de entrañar: es trivialmente cierto que
                un texto no menciona el ambiente *en México*
                si ni siquiera menciona México.
```

El efecto neto: masa de probabilidad empujada hacia `na`, relevancia hundida, y una alerta de
«dimensión muda» **causada por la redacción y no por el corpus**.

```
   ┌──────────────────────────────────────────────────────────┐
   │  Mismo contenido. Mismo modelo. Distinto lugar del ancla.│
   │  Conclusión opuesta sobre si el corpus habla del tema.    │
   └──────────────────────────────────────────────────────────┘
```

### Y no se dio por supuesto

El notebook incluye un interruptor que genera la variante A **derivada automáticamente** de
las mismas frases, corre el banco de pruebas con las dos y compara. Si el efecto no apareciera,
la decisión se revisaría con el número delante.

Esa es la forma correcta de tomar una decisión de diseño: **medirla, no argumentarla.**

---

# PARTE III — LAS GRÁFICAS

## 11. Cómo se construyen

### Figura «valencia contra relevancia»

Diagrama de dispersión. **Cada punto es un tuit.**

```
              valencia
                 +1 ┤
                    │                    ← arriba: habló BIEN
                  0 ┼────────────────────────────────────
                    │                    ← abajo: habló MAL
                 -1 ┤
                    └─────┬──────────────────────────┬───
                    0    0.3                         1
                                  relevancia
                    └──┬──┘
                       │
              ZONA GRIS: "no habló del tema"
```

- **Horizontal** = relevancia de ese tuit en esa dimensión.
- **Vertical** = valencia de ese tuit en esa dimensión.
- **Banda gris** = por debajo del umbral de mudez.

Decisión de diseño importante: **los puntos de la banda gris se dibujan, no se esconden.** Se
verían más limpias filtrándolos, pero verlos *es* la evidencia. Si la banda está vacía, eso te
dice algo. Si está llena, también.

### Figura «reparto de probabilidad»

Barras apiladas. Cada barra es un texto o grupo, y muestra a dónde fue el 100 %:

```
   texto A  │███████████████████████│▒▒▒▒▒▒▒│░░░░░░░│
            │      pos  0.58        │na 0.27│neg 0.15│

   texto B  │███████████│▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│░░░░░░░│
            │ pos 0.28  │      na 0.52      │neg 0.20│
            └───────────────────────────────────────┘
            0                                        1
```

Todas miden lo mismo (suman 1). Lo que cambia es **dónde está el peso**. Sirve para ver *a
dónde se va* la probabilidad, más informativo que el número ya restado.

### Figura «método actual contra rediseño»

```
    rediseño
        +1 ┤                        ╱
           │                    ╱  ·
           │      ·    ·    ╱   ·
         0 ┼──────·───·─╱──────────
           │   ·   · ╱ ·
           │    ·  ╱
        -1 ┤    ╱
           └──────────────────────────
          -1          0            +1
                método actual

           ╱ = diagonal de acuerdo perfecto
```

Si ambos métodos coincidieran siempre, todo estaría sobre la diagonal. Cuanto más lejos, más
discrepan.

---

## 12. Cómo leerlas sin equivocarse

### Las zonas del plano

```
              valencia
                 +1 ┤
                    │  ZONA C          │   ZONA A
                    │  (ruido)         │   juicio positivo real
                  0 ┼──────────────────┼──────────────────────
                    │  ZONA C          │   ZONA B
                    │  (ruido)         │   juicio negativo real
                 -1 ┤                  │
                    └──────────────────┴──────────────────────
                    0        umbral                          1
                                  relevancia
```

**Zonas A y B.** Relevancia alta, valencia clara. Juicios de verdad. Lo único directamente
reportable.

**Zona intermedia** (derecha, pegada al 0). Habló del tema pero no se decantó: ambivalente, o
mezcló lo bueno con lo malo. **Ahora esto significa algo**; antes era indistinguible del mudo.

**Zona C.** Relevancia baja. **Aquí la valencia no se lee.** Es el ruido de obligar al modelo
a elegir bando sobre un tuit que no venía al caso.

### Error nº 1 — promediar toda la nube

```
   ✗ MAL:  "la valencia media de imagen_cultural es +0.31"
              (sobre los 2 562 tuits)

   ✓ BIEN: "entre los tuits que hablan de imagen cultural
            (relevancia ≥ umbral, n = 840), la valencia media es +0.44"
```

Promediar todo mezcla juicios reales con ruido de la zona C. El número parece presentable y no
significa nada.

### Error nº 2 — leer formas que son aritmética

En el diseño viejo, `|valencia| ≤ relevancia` dibujaba una cuña **inevitable**:

```
        +1 ┤                    ╱▒▒▒
           │              ╱▒▒▒▒▒▒▒▒▒
         0 ┼────────╱▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
           │              ╲▒▒▒▒▒▒▒▒▒
        -1 ┤                    ╲▒▒▒
           └──────────────────────────
           0                          1

     Los bordes NO son un hallazgo.
     Son las rectas y = x  e  y = -x.
     Saldrían igual con texto aleatorio.
```

Quien viera eso podría escribir *«los tuits menos relevantes tienden a ser más neutros»*. Sería
describir **tu propia ecuación** y presentarla como un descubrimiento sobre turistas.

> **Regla general:** antes de interpretar un patrón, pregúntate si saldría igual con datos
> aleatorios. Si la respuesta es sí, es aritmética, no evidencia.

### Error nº 3 — confundir «el modelo duda» con «la gente es tibia»

Si una nube está aplastada contra el cero, hay dos explicaciones:

```
   (a) Los turistas realmente tienen opiniones tibias.
   (b) El modelo no logra decidirse, y al restar sale ≈ 0.
```

**Desde la gráfica se ven idénticas.** Para distinguirlas hay que mirar el reparto de
probabilidad: si `pos` y `neg` están ambas en torno a 0.45, el modelo está dudando; si el
texto de verdad dice cosas buenas y malas, es ambivalencia real.

### Error nº 4 — creer que el número está validado

El instrumento mide de forma **consistente**. Eso no quiere decir que mida **lo correcto**.

Para saberlo hace falta que una persona lea una muestra, la clasifique a mano, y se compare con
el modelo. Mientras eso no exista, los resultados son **descriptivos pero no validados** — que
es justo lo que dice el cartel de las figuras de este proyecto.

---

## 13. Resumen en una página

```
   ┌──────────────────────────────────────────────────────────────────┐
   │  1. El tuit entra como PREMISA.                                  │
   │                                                                  │
   │  2. Tu pregunta se convierte en HIPÓTESIS vía una PLANTILLA:     │
   │        "Este texto sobre Mexico dice que {etiqueta}."            │
   │                                                                  │
   │  3. El modelo NLI juzga la relación y devuelve LOGITS.           │
   │     Nos quedamos solo con el de ENTAILMENT.                      │
   │                                                                  │
   │  4. SOFTMAX los convierte en probabilidades. Dos modos:          │
   │        · compitiendo  (suman 1)  → elegir ENTRE opciones         │
   │        · por separado (libres)   → preguntar SÍ/NO a cada una    │
   │                                                                  │
   │  5. De ahí salen dos números INDEPENDIENTES:                     │
   │        relevancia = ¿habló del tema?     [0, 1]                  │
   │        valencia   = ¿bien o mal?         [-1, +1]                │
   │                                                                  │
   │  6. La valencia SOLO se interpreta si la relevancia              │
   │     supera el umbral.                                            │
   └──────────────────────────────────────────────────────────────────┘
```

### Las tres ideas que hay que retener

**Las hipótesis son el instrumento.** Escribirlas es tomar decisiones de medición, igual que
redactar las preguntas de una encuesta.

**Dónde normalizas importa tanto como qué preguntas.** El mismo modelo, el mismo tuit y las
mismas palabras dieron relevancia 0.59 o 0.06 según dónde se aplicara el softmax.

**Una forma en una gráfica puede ser aritmética disfrazada de hallazgo.** Antes de
interpretarla, comprueba que no saldría igual con datos aleatorios.
