# Prompt — rediseño de las hipótesis zero-shot

> Copia todo lo que sigue a partir de la línea de guiones y pégalo como un solo mensaje.

---

## Rol

Eres un metodólogo especializado en medición con modelos NLI zero-shot. Vas a rediseñar
las hipótesis de un instrumento que ya corrió y que muestra fallas diagnosticadas. No
escribes código: entregas frases y el razonamiento que las justifica.

## Cómo funciona el instrumento (no lo cambies, es el contexto)

Cada dimensión son **tres hipótesis que compiten**: positiva, negativa y de irrelevancia.
Se evalúan con `transformers.pipeline("zero-shot-classification")` sobre
`joeddav/xlm-roberta-large-xnli` con `multi_label=False`, es decir un **softmax sobre los
tres logits de entailment**, de modo que:

```
P(pos) + P(neg) + P(na) = 1

valencia   = P(pos) − P(neg)      va de −1 a 1
relevancia = 1 − P(na)            va de 0 a 1
```

Consecuencia algebraica que debes tener presente: `|valencia| ≤ relevancia` siempre.

Las hipótesis se insertan en una plantilla única para todos los textos:

```
"Este texto sobre Mexico dice que {}."
```

El corpus es multilingüe (inglés 2006, japonés 417, y una cola de otros idiomas sobre
2562 tuits). XNLI es translingüístico: la hipótesis va en **un solo idioma** para todos los
textos, de modo que el instrumento sea idéntico entre idiomas.

## Restricción de diseño que NO debes tocar

El ancla geográfica «México» va en la **plantilla**, nunca dentro de las etiquetas. Razón:
el softmax es invariante a un desplazamiento constante entre las tres etiquetas; metida
dentro de cada etiqueta, el ancla deja de ser constante — encarece las dos afirmaciones y
**abarata la negación**, porque es trivialmente cierto que un texto no menciona X *en
México* si no menciona México. Eso empuja masa hacia `na` y hunde la relevancia por
artefacto de redacción.

Por lo tanto: **ninguna de tus frases puede mencionar México ni ningún lugar.**

## Definición canónica de las dimensiones

Estas definiciones son el criterio. Las hipótesis deben operacionalizar esto y nada más.

| Dimensión | Qué mide |
|---|---|
| `atmosfera` | el ánimo que se vive: alegre y emocionante contra desagradable y estresante |
| `imagen_cultural` | comida, lugares y cultura: hermosos e impresionantes contra decepcionantes |
| `perspectiva_politica` | el gobierno y sus autoridades: competentes y legales contra corruptos |

## Hipótesis actuales (textual, en español e inglés)

```python
"atmosfera": {
    "pos": "el ambiente fue alegre y emocionante para los visitantes",
    "neg": "el ambiente fue desagradable y estresante para los visitantes",
    "na":  "no menciona el ambiente ni el estado de animo que se vive",
},
"imagen_cultural": {
    "pos": "la comida, los lugares y la cultura son hermosos e impresionantes",
    "neg": "la comida, los lugares y la cultura son decepcionantes y poco atractivos",
    "na":  "no menciona la comida, los lugares ni la cultura",
},
"perspectiva_politica": {
    "pos": "el gobierno y sus autoridades actuaron de forma competente, legal y justa",
    "neg": "el gobierno y sus autoridades actuaron de forma corrupta, criminal e incompetente",
    "na":  "no menciona al gobierno, a sus politicos ni a sus autoridades",
},
```

## Evidencia observada, que es lo que hay que corregir

**1. El eje de relevancia no separa nada.** Sobre 2562 tuits reales, **ninguna** observación
cae por debajo de `relevancia = 0.30` en `atmosfera` ni en `imagen_cultural`. El mínimo
observado ronda 0.35–0.45. La hipótesis `na` prácticamente nunca gana.

**2. El control mudo no sale mudo.** En la batería de prueba hay una frase escrita a
propósito para no hablar de ninguna dimensión («la gente fue amable»). Debería dar
`relevancia ≈ 0` en las tres. Da **0.83**.

**3. `imagen_cultural` no se decide.** Su nube de valencia está aplastada contra el cero
(casi todo entre −0.5 y +0.5) pese a relevancia alta, mientras que `atmosfera`, con la misma
mecánica, llena todo el rango hasta ±1. En la batería, ninguna sonda superó 0.58 en `pos` y
todas quedaron apretadas entre 0.41 y 0.58.

**4. Contaminación entre dimensiones.** Una sonda escrita sobre violencia obtiene valencia
+0.29 en `imagen_cultural`, por encima del propio control mudo (+0.21).

## Defectos que sospecho, para que los confirmes o los descartes

- **Conjunción de sujetos.** `imagen_cultural` pregunta por tres sujetos unidos con «y»
  (comida, lugares y cultura). Un tuit que solo habla de comida no puede entrañar la
  afirmación completa, así que `pos` y `neg` reciben valores intermedios y la resta se va a
  cero. `atmosfera` tiene un solo sujeto y sí se decide.
- **Asimetría de intensidad.** «hermosos e impresionantes» son elogios fuertes; «poco
  atractivos» es una negación suavizada. Eso sesga la valencia hacia arriba por redacción.
- **La negación como tercera hipótesis.** Los modelos de entailment puntúan mal las
  hipótesis negadas («no menciona X») aunque sean ciertas, lo que subestima `P(na)` de forma
  sistemática y explica los puntos 1 y 2.

## Lo que debes entregar

**A. Diagnóstico.** Para cada defecto sospechado: confírmalo, descártalo o corrígelo, con el
mecanismo lingüístico o del modelo que lo explica. Si crees que la causa real es otra, dilo.

**B. Hipótesis nuevas.** El bloque `DIMENSIONES` completo, en **español e inglés**, listo
para pegar, con la misma estructura de tres etiquetas por dimensión. Reglas:

- Estructura paralela entre `pos` y `neg`: mismo sujeto, misma construcción, **intensidad
  equivalente** en los adjetivos. La única diferencia debe ser la polaridad.
- Las tres etiquetas de una dimensión comparten el mismo sujeto, para que el softmax compare
  polaridad y no temas distintos.
- Ningún nombre de lugar.
- Que discriminen entre dimensiones: la frase de una dimensión no debe ser entrañable por un
  texto de otra.
- Las versiones en español e inglés deben ser equivalentes en contenido e intensidad.

**C. El problema del `na`.** Si concluyes que reformular la negación no basta, dilo
explícitamente y propón la alternativa de diseño (por ejemplo, sacar la relevancia de la
competencia de tres y medirla como una pregunta binaria afirmativa aparte), con sus
implicaciones sobre las fórmulas de arriba.

**D. Cómo se comprobaría.** Qué debería pasar en la batería de prueba si tu rediseño
funciona, en números concretos: qué relevancia esperas para el control mudo, y qué separación
esperas entre cada sonda y su dimensión.

## Criterio de parada, que importa más que las frases

Las hipótesis se ajustan contra la batería de prueba —30 frases escritas a propósito, de
contenido controlado— y **nunca contra los promedios del corpus**. Reescribirlas hasta que el
resultado sobre el corpus se vea bien es elegir el instrumento por la respuesta que produce.

Estas frases **son** el instrumento de medición y van citadas textualmente en la tesis, igual
que se cita un libro de códigos. Redáctalas para ser defendidas, no para rendir bien.
