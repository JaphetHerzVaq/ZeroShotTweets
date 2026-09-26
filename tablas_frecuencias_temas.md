# Frecuencias por tema e indicador (tuits que sí hablan de la rúbrica)

Fuente de la rúbrica: `tweets_calificados_anclada.csv` (2,631 tuits). Fuente de los temas: `resultados_enriquecidos.csv` (columnas `nlp__cluster` y `nlp__topico`, la misma asignación del mapa UMAP de la sección 16 del notebook). Generado por `frecuencias_temas.py`.

Universo: los 144 tuits con nivel mayor que 0 en al menos un indicador (5.5 % del corpus). Aparecen en 18 temas; los otros 15 clusters no tienen ningún tuit calificado.

## 1. Por tema, apilado por indicador

Cada celda es el número de tuits calificados del tema que hablan de ese indicador. Un tuit puede hablar de varios, así que la suma de la barra puede superar la columna «Tuits calificados» (distintos). «Indicadores por tuit» es ese cociente.

| Tema | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Suma (barra) | Tuits calificados | Tuits del tema | % calificados | Indicadores por tuit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ruido | 31 | 7 | 19 | 6 | 63 | 44 | 897 | 4.9 % | 1.43 |
| C1 · especial, correcto, palabra, entrepierna | 0 | 1 | 0 | 0 | 1 | 1 | 147 | 0.7 % | 1.00 |
| C2 · jugador, portero, fichaje, ince | 0 | 0 | 0 | 1 | 1 | 1 | 135 | 0.7 % | 1.00 |
| C3 · yonna, streamer, chica, stream | 0 | 0 | 1 | 1 | 2 | 2 | 113 | 1.8 % | 1.00 |
| C4 · méxico, viaje, ciudad, hora | 38 | 2 | 25 | 1 | 66 | 41 | 99 | 41.4 % | 1.61 |
| C5 · partido, copa, fútbol, mundo | 2 | 0 | 0 | 0 | 2 | 2 | 95 | 2.1 % | 1.00 |
| C7 · lindo, genial, increíble, favor | 1 | 0 | 1 | 0 | 2 | 1 | 75 | 1.3 % | 2.00 |
| C8 · vegetarian, ensalada, queso, recipes | 2 | 0 | 12 | 0 | 14 | 12 | 60 | 20.0 % | 1.17 |
| C9 · rotundo, mitch, traemos, verdaderamente | 0 | 0 | 0 | 1 | 1 | 1 | 49 | 2.0 % | 1.00 |
| C10 · méxico, mexicano, gente, japón | 21 | 11 | 7 | 15 | 54 | 23 | 47 | 48.9 % | 2.35 |
| C11 · estadio, york, autobús, impresionante | 2 | 3 | 4 | 0 | 9 | 6 | 46 | 13.0 % | 1.50 |
| C15 · colega, cumpleaños, médico, besadme | 1 | 0 | 0 | 0 | 1 | 1 | 35 | 2.9 % | 1.00 |
| C18 · fujisawa, kai, hit, kamakura | 1 | 0 | 1 | 0 | 2 | 2 | 30 | 6.7 % | 1.00 |
| C21 · imbécil, llama, pedófilo, zorra | 3 | 0 | 0 | 0 | 3 | 3 | 24 | 12.5 % | 1.00 |
| C23 · equipaje, tampón, bolsa, bolsillo | 0 | 1 | 0 | 0 | 1 | 1 | 23 | 4.3 % | 1.00 |
| C25 · paso, milla, corro, seguido | 0 | 0 | 1 | 0 | 1 | 1 | 21 | 4.8 % | 1.00 |
| C28 · entrega, sim, mes, pago | 1 | 0 | 0 | 0 | 1 | 1 | 17 | 5.9 % | 1.00 |
| C30 · lluvia, tormenta, sol, repentino | 1 | 0 | 0 | 0 | 1 | 1 | 15 | 6.7 % | 1.00 |
| Total | 104 | 25 | 71 | 25 | 225 | 144 | 2631 | 5.5 % | 1.56 |

Clusters sin ningún tuit calificado: sin texto útil (88), C0 · cristiano, iglesia, dios, judío (180), C6 · proyecto, desarrollador, vivienda, negocio (93), C12 · marido, carne, batidos, leche (45), C13 · tecnología, acción, ambicioso, fundador (39), C14 · sitio, hecho, usuario, envío (37), C16 · tarea, aplicación, app, foto (35), C17 · entrada, vuelo, club, inglaterra (33), C19 · extraño, correo, electrónico, terapia (27), C20 · hora, presidente, kompany, wednesday (26), C22 · voz, película, lotta, mandalorian (23), C24 · mujer, gay, militar, feminista (22), C26 · gracia, mentalmente, inolvidable, artista (20), C27 · publicación, hermano, post, hermoso (19), C29 · efecto, phat, indeed, yes (16).

## 2. Por indicador, apilado por tema

La misma matriz transpuesta: una barra por indicador, cuyos segmentos son los temas. El total de cada barra es el número de tuits que hablan de ese indicador.

| Indicador | ruido | C1 · especial, correcto, palabra, entrepierna | C2 · jugador, portero, fichaje, ince | C3 · yonna, streamer, chica, stream | C4 · méxico, viaje, ciudad, hora | C5 · partido, copa, fútbol, mundo | C7 · lindo, genial, increíble, favor | C8 · vegetarian, ensalada, queso, recipes | C9 · rotundo, mitch, traemos, verdaderamente | C10 · méxico, mexicano, gente, japón | C11 · estadio, york, autobús, impresionante | C15 · colega, cumpleaños, médico, besadme | C18 · fujisawa, kai, hit, kamakura | C21 · imbécil, llama, pedófilo, zorra | C23 · equipaje, tampón, bolsa, bolsillo | C25 · paso, milla, corro, seguido | C28 · entrega, sim, mes, pago | C30 · lluvia, tormenta, sol, repentino | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Atmósfera | 31 | 0 | 0 | 0 | 38 | 2 | 1 | 2 | 0 | 21 | 2 | 1 | 1 | 3 | 0 | 0 | 1 | 1 | 104 |
| Perspectiva política | 7 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 11 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 25 |
| Imagen cultural | 19 | 0 | 0 | 1 | 25 | 0 | 1 | 12 | 0 | 7 | 4 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 71 |
| Saliencia de violencia | 6 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 |

Combinaciones exactas de indicadores por tuit (cada tuit cuenta una sola vez):

| Combinación | Tuits | % |
|---|---:|---:|
| Atmósfera | 47 | 32.6 % |
| Atmósfera + Imagen cultural | 32 | 22.2 % |
| Imagen cultural | 29 | 20.1 % |
| Atmósfera + Perspectiva política + Saliencia de violencia | 11 | 7.6 % |
| Atmósfera + Imagen cultural + Saliencia de violencia | 4 | 2.8 % |
| Saliencia de violencia | 4 | 2.8 % |
| Perspectiva política | 4 | 2.8 % |
| Atmósfera + Perspectiva política | 3 | 2.1 % |
| Atmósfera + Saliencia de violencia | 3 | 2.1 % |
| Atmósfera + Perspectiva política + Imagen cultural | 2 | 1.4 % |
| Perspectiva política + Imagen cultural | 2 | 1.4 % |
| Atmósfera + Perspectiva política + Imagen cultural + Saliencia de violencia | 2 | 1.4 % |
| Perspectiva política + Saliencia de violencia | 1 | 0.7 % |

## 3. Por tema e indicador, apilado por nivel de valencia

Para cada indicador de valencia, los tuits del tema repartidos por nivel 1 a 5. La columna «neg / amb / pos» agrupa 1-2, 3 y 4-5. Saliencia de violencia es de presencia (solo nivel 1) y se lista al final sin valencia.

### Atmósfera

| Tema | 1 · muy negativo | 2 · negativo | 3 · ambivalente o mixto | 4 · positivo | 5 · muy positivo | Total | neg / amb / pos | Nivel medio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ruido | 4 | 10 | 2 | 8 | 7 | 31 | 14 / 2 / 15 | 3.13 |
| C4 · méxico, viaje, ciudad, hora | 0 | 3 | 0 | 18 | 17 | 38 | 3 / 0 / 35 | 4.29 |
| C5 · partido, copa, fútbol, mundo | 2 | 0 | 0 | 0 | 0 | 2 | 2 / 0 / 0 | 1.00 |
| C7 · lindo, genial, increíble, favor | 0 | 0 | 0 | 1 | 0 | 1 | 0 / 0 / 1 | 4.00 |
| C8 · vegetarian, ensalada, queso, recipes | 0 | 1 | 0 | 1 | 0 | 2 | 1 / 0 / 1 | 3.00 |
| C10 · méxico, mexicano, gente, japón | 7 | 8 | 1 | 3 | 2 | 21 | 15 / 1 / 5 | 2.29 |
| C11 · estadio, york, autobús, impresionante | 0 | 0 | 1 | 1 | 0 | 2 | 0 / 1 / 1 | 3.50 |
| C15 · colega, cumpleaños, médico, besadme | 0 | 0 | 0 | 0 | 1 | 1 | 0 / 0 / 1 | 5.00 |
| C18 · fujisawa, kai, hit, kamakura | 0 | 0 | 0 | 1 | 0 | 1 | 0 / 0 / 1 | 4.00 |
| C21 · imbécil, llama, pedófilo, zorra | 3 | 0 | 0 | 0 | 0 | 3 | 3 / 0 / 0 | 1.00 |
| C28 · entrega, sim, mes, pago | 0 | 0 | 0 | 1 | 0 | 1 | 0 / 0 / 1 | 4.00 |
| C30 · lluvia, tormenta, sol, repentino | 0 | 0 | 0 | 1 | 0 | 1 | 0 / 0 / 1 | 4.00 |
| Total | 16 | 22 | 4 | 35 | 27 | 104 | 38 / 4 / 62 | 3.34 |

### Perspectiva política

| Tema | 1 · muy negativo | 2 · negativo | 3 · ambivalente o mixto | 4 · positivo | 5 · muy positivo | Total | neg / amb / pos | Nivel medio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ruido | 0 | 5 | 0 | 2 | 0 | 7 | 5 / 0 / 2 | 2.57 |
| C1 · especial, correcto, palabra, entrepierna | 0 | 1 | 0 | 0 | 0 | 1 | 1 / 0 / 0 | 2.00 |
| C4 · méxico, viaje, ciudad, hora | 0 | 2 | 0 | 0 | 0 | 2 | 2 / 0 / 0 | 2.00 |
| C10 · méxico, mexicano, gente, japón | 9 | 2 | 0 | 0 | 0 | 11 | 11 / 0 / 0 | 1.18 |
| C11 · estadio, york, autobús, impresionante | 0 | 1 | 0 | 2 | 0 | 3 | 1 / 0 / 2 | 3.33 |
| C23 · equipaje, tampón, bolsa, bolsillo | 0 | 1 | 0 | 0 | 0 | 1 | 1 / 0 / 0 | 2.00 |
| Total | 9 | 12 | 0 | 4 | 0 | 25 | 21 / 0 / 4 | 1.96 |

### Imagen cultural

| Tema | 1 · muy negativo | 2 · negativo | 3 · ambivalente o mixto | 4 · positivo | 5 · muy positivo | Total | neg / amb / pos | Nivel medio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ruido | 1 | 2 | 7 | 7 | 2 | 19 | 3 / 7 / 9 | 3.37 |
| C3 · yonna, streamer, chica, stream | 0 | 0 | 0 | 1 | 0 | 1 | 0 / 0 / 1 | 4.00 |
| C4 · méxico, viaje, ciudad, hora | 0 | 1 | 3 | 15 | 6 | 25 | 1 / 3 / 21 | 4.04 |
| C7 · lindo, genial, increíble, favor | 0 | 0 | 0 | 1 | 0 | 1 | 0 / 0 / 1 | 4.00 |
| C8 · vegetarian, ensalada, queso, recipes | 0 | 1 | 6 | 5 | 0 | 12 | 1 / 6 / 5 | 3.33 |
| C10 · méxico, mexicano, gente, japón | 4 | 1 | 1 | 0 | 1 | 7 | 5 / 1 / 1 | 2.00 |
| C11 · estadio, york, autobús, impresionante | 0 | 0 | 2 | 2 | 0 | 4 | 0 / 2 / 2 | 3.50 |
| C18 · fujisawa, kai, hit, kamakura | 0 | 0 | 1 | 0 | 0 | 1 | 0 / 1 / 0 | 3.00 |
| C25 · paso, milla, corro, seguido | 0 | 0 | 0 | 1 | 0 | 1 | 0 / 0 / 1 | 4.00 |
| Total | 5 | 5 | 20 | 32 | 9 | 71 | 10 / 20 / 41 | 3.49 |

### Saliencia de violencia

| Tema | 1 · presente |
|---|---:|
| ruido | 6 |
| C2 · jugador, portero, fichaje, ince | 1 |
| C3 · yonna, streamer, chica, stream | 1 |
| C4 · méxico, viaje, ciudad, hora | 1 |
| C9 · rotundo, mitch, traemos, verdaderamente | 1 |
| C10 · méxico, mexicano, gente, japón | 15 |
| Total | 25 |

## Notas de lectura

- **Habla del indicador** = nivel mayor que 0 en ese criterio. Es la definición del notebook y de `pies_rubrica.py`; contar `aplicable = SI` daría más, porque incluye tuits marcados aplicables y puntuados en 0. BLOQUEADO es dato faltante y no cuenta.
- **Tema** es el cluster de HDBSCAN sobre el UMAP de los embeddings del texto original, con los cuatro términos más distintivos (c-TF-IDF sobre lemas de la traducción) como nombre. «ruido» es el cluster −1 (sin asignar) y «sin texto útil» el −2. Los clusters dependen de `HDBSCAN_MIN_CLUSTER` y `UMAP_VECINOS`; no son categorías fijas.
- La asignación de temas se lee de `resultados_enriquecidos.csv`, que produjo el notebook en Colab. Si se vuelve a correr el notebook con otros parámetros, hay que volver a correr este script.
- En la gráfica por tema los segmentos son indicadores y un tuit puede aportar a varios; en la gráfica por indicador cada tuit aporta a un solo segmento (su tema). Por eso las sumas coinciden por indicador pero no con los tuits distintos.
- El **nivel medio** es orientativo: con 2 o 3 tuits en un tema no describe nada. Las cuentas absolutas van siempre al lado.
