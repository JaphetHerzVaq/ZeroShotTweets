# Frecuencias por cluster del mapa UMAP

Fuente del corpus y de la rúbrica: `tweets_calificados_anclada.csv` (2,631 tuits). Fuente de los clusters: `C:\Users\japhe\Downloads\resultados_enriquecidos.csv` (columnas `nlp__cluster`, `nlp__topico`, `nlp__umap_x`, `nlp__umap_y`, la misma asignación del mapa de la sección 16 del notebook). Generado por `clusters_umap.py`, que también dibuja `salida/mapa_umap_clusters.png` y `salida/dona_clusters.png` y guarda la tabla en `salida/frecuencias_clusters.csv`.

Cómo se obtuvo el agrupamiento: embeddings multilingües del **texto original** limpio (`sentence-transformers/paraphrase-multilingual-mpnet-base-v2`), UMAP a 10 dimensiones (`n_neighbors=15`, `min_dist=0.0`, métrica coseno) y HDBSCAN (`min_cluster_size=15`, `min_samples=5`). Los clusters se renumeran por tamaño (C0 es el más grande). El nombre de cada tema son sus cuatro lemas más distintivos (c-TF-IDF sobre la traducción al español). El mapa usa un segundo UMAP a 2 dimensiones (`min_dist=0.1`) solo para dibujar.

Resultado: **31 clusters** con 1,646 tuits (62.6 %), **ruido** 897 (34.1 %) y **sin texto útil** 88 (3.3 %). Calificados (nivel > 0 en algún indicador): 144 (5.5 % del corpus).

## 1. Lo que muestra la figura

El mapa da color propio a los 15 clusters más grandes (C0–C14); del C15 en adelante los puntos van en gris claro («otros clusters») y el ruido en gris más tenue. Los tuits sin texto útil no entran al UMAP, así que no están en el mapa. La dona usa las mismas categorías.

| Categoría | Clusters | Tuits | % del corpus | Calificados | % de los calificados |
|---|---:|---:|---:|---:|---:|
| color propio | 15 | 1260 | 47.9 % | 90 | 62.5 % |
| otros clusters | 16 | 386 | 14.7 % | 10 | 6.9 % |
| ruido | 0 | 897 | 34.1 % | 44 | 30.6 % |
| sin texto útil | 0 | 88 | 3.3 % | 0 | 0.0 % |
| Total | 31 | 2631 | 100.0 % | 144 | 100.0 % |

## 2. Frecuencias por cluster

Una fila por cluster, en el orden de la numeración (por tamaño). «% calificados» es la proporción del cluster que habla de algún indicador; «% de los calificados» reparte los 144 calificados entre clusters. «Mencionan México» viene del diccionario del notebook (`nlp__menciona_mexico`).

| Cluster | Tema (4 términos c-TF-IDF) | En la figura | Tuits | % corpus | Calificados | % calificados | % de los calificados | Mencionan México | % México | Idiomas (top 3) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 | cristiano, iglesia, dios, judío | color propio | 180 | 6.8 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 179 · es 1 |
| C1 | especial, correcto, palabra, entrepierna | color propio | 147 | 5.6 % | 1 | 0.7 % | 0.7 % | 0 | 0.0 % | en 103 · ja 37 · und 4 |
| C2 | jugador, portero, fichaje, ince | color propio | 135 | 5.1 % | 1 | 0.7 % | 0.7 % | 0 | 0.0 % | en 130 · ja 5 |
| C3 | yonna, streamer, chica, stream | color propio | 113 | 4.3 % | 2 | 1.8 % | 1.4 % | 1 | 0.9 % | en 107 · ja 4 · fr 2 |
| C4 | méxico, viaje, ciudad, hora | color propio | 99 | 3.8 % | 41 | 41.4 % | 28.5 % | 63 | 63.6 % | en 78 · ja 16 · es 3 |
| C5 | partido, copa, fútbol, mundo | color propio | 95 | 3.6 % | 2 | 2.1 % | 1.4 % | 6 | 6.3 % | en 80 · ja 15 |
| C6 | proyecto, desarrollador, vivienda, negocio | color propio | 93 | 3.5 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 93 |
| C7 | lindo, genial, increíble, favor | color propio | 75 | 2.9 % | 1 | 1.3 % | 0.7 % | 0 | 0.0 % | en 45 · ja 26 · it 1 |
| C8 | vegetarian, ensalada, queso, recipes | color propio | 60 | 2.3 % | 12 | 20.0 % | 8.3 % | 6 | 10.0 % | en 56 · ja 2 · es 1 |
| C9 | rotundo, mitch, traemos, verdaderamente | color propio | 49 | 1.9 % | 1 | 2.0 % | 0.7 % | 0 | 0.0 % | en 34 · ja 13 · es 1 |
| C10 | méxico, mexicano, gente, japón | color propio | 47 | 1.8 % | 23 | 48.9 % | 16.0 % | 26 | 55.3 % | en 36 · ja 11 |
| C11 | estadio, york, autobús, impresionante | color propio | 46 | 1.7 % | 6 | 13.0 % | 4.2 % | 6 | 13.0 % | en 25 · ja 21 |
| C12 | marido, carne, batidos, leche | color propio | 45 | 1.7 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 30 · ja 15 |
| C13 | tecnología, acción, ambicioso, fundador | color propio | 39 | 1.5 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 25 · ja 14 |
| C14 | sitio, hecho, usuario, envío | color propio | 37 | 1.4 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 37 |
| C15 | colega, cumpleaños, médico, besadme | otros clusters | 35 | 1.3 % | 1 | 2.9 % | 0.7 % | 0 | 0.0 % | en 24 · ja 4 · es 2 |
| C16 | tarea, aplicación, app, foto | otros clusters | 35 | 1.3 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 34 · ja 1 |
| C17 | entrada, vuelo, club, inglaterra | otros clusters | 33 | 1.3 % | 0 | 0.0 % | 0.0 % | 2 | 6.1 % | en 32 · ja 1 |
| C18 | fujisawa, kai, hit, kamakura | otros clusters | 30 | 1.1 % | 2 | 6.7 % | 1.4 % | 2 | 6.7 % | ja 21 · en 9 |
| C19 | extraño, correo, electrónico, terapia | otros clusters | 27 | 1.0 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 26 · ja 1 |
| C20 | hora, presidente, kompany, wednesday | otros clusters | 26 | 1.0 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 19 · ja 7 |
| C21 | imbécil, llama, pedófilo, zorra | otros clusters | 24 | 0.9 % | 3 | 12.5 % | 2.1 % | 0 | 0.0 % | en 24 |
| C22 | voz, película, lotta, mandalorian | otros clusters | 23 | 0.9 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 12 · ja 11 |
| C23 | equipaje, tampón, bolsa, bolsillo | otros clusters | 23 | 0.9 % | 1 | 4.3 % | 0.7 % | 2 | 8.7 % | ja 12 · en 11 |
| C24 | mujer, gay, militar, feminista | otros clusters | 22 | 0.8 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 22 |
| C25 | paso, milla, corro, seguido | otros clusters | 21 | 0.8 % | 1 | 4.8 % | 0.7 % | 1 | 4.8 % | en 17 · ja 4 |
| C26 | gracia, mentalmente, inolvidable, artista | otros clusters | 20 | 0.8 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 19 · ja 1 |
| C27 | publicación, hermano, post, hermoso | otros clusters | 19 | 0.7 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 19 |
| C28 | entrega, sim, mes, pago | otros clusters | 17 | 0.6 % | 1 | 5.9 % | 0.7 % | 0 | 0.0 % | en 14 · ja 3 |
| C29 | efecto, phat, indeed, yes | otros clusters | 16 | 0.6 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | en 13 · und 3 |
| C30 | lluvia, tormenta, sol, repentino | otros clusters | 15 | 0.6 % | 1 | 6.7 % | 0.7 % | 4 | 26.7 % | ja 9 · en 6 |
| ruido | — | ruido | 897 | 34.1 % | 44 | 4.9 % | 30.6 % | 56 | 6.2 % | en 700 · ja 175 · und 7 |
| sin texto útil | — | sin texto útil | 88 | 3.3 % | 0 | 0.0 % | 0.0 % | 0 | 0.0 % | qme 63 · zxx 8 · und 7 |
| Total |  |  | 2631 | 100.0 % | 144 | 5.5 % | 100.0 % | 175 | 6.7 % |  |

## 3. Temas por indicador (barras apiladas)

Es la tabla de `salida/barras_indicador_tema.png`: una barra por indicador, apilada por tema, más una quinta barra (en un panel con escala propia) con los tuits que no calificaron en ningún indicador. Cada celda es el número de tuits del tema que hablan de ese indicador (nivel > 0); un tuit que habla de varios cuenta en cada columna, por eso «Menciones» puede superar «Tuits calificados». «Ningún indicador» son los tuits con nivel 0 o faltante en los cuatro. Los temas con al menos 3 menciones llevan color propio en la gráfica (5 temas); el resto se pliega en «otros temas».

| Tema | Términos | En la gráfica | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Ningún indicador | Menciones | Tuits calificados | Tuits del tema |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C4 | méxico, viaje, ciudad, hora | color propio | 38 | 2 | 25 | 1 | 58 | 66 | 41 | 99 |
| ruido | — | ruido | 31 | 7 | 19 | 6 | 853 | 63 | 44 | 897 |
| C10 | méxico, mexicano, gente, japón | color propio | 21 | 11 | 7 | 15 | 24 | 54 | 23 | 47 |
| C8 | vegetarian, ensalada, queso, recipes | color propio | 2 | 0 | 12 | 0 | 48 | 14 | 12 | 60 |
| C11 | estadio, york, autobús, impresionante | color propio | 2 | 3 | 4 | 0 | 40 | 9 | 6 | 46 |
| C21 | imbécil, llama, pedófilo, zorra | color propio | 3 | 0 | 0 | 0 | 21 | 3 | 3 | 24 |
| C3 | yonna, streamer, chica, stream | otros temas | 0 | 0 | 1 | 1 | 111 | 2 | 2 | 113 |
| C5 | partido, copa, fútbol, mundo | otros temas | 2 | 0 | 0 | 0 | 93 | 2 | 2 | 95 |
| C7 | lindo, genial, increíble, favor | otros temas | 1 | 0 | 1 | 0 | 74 | 2 | 1 | 75 |
| C18 | fujisawa, kai, hit, kamakura | otros temas | 1 | 0 | 1 | 0 | 28 | 2 | 2 | 30 |
| C1 | especial, correcto, palabra, entrepierna | otros temas | 0 | 1 | 0 | 0 | 146 | 1 | 1 | 147 |
| C2 | jugador, portero, fichaje, ince | otros temas | 0 | 0 | 0 | 1 | 134 | 1 | 1 | 135 |
| C9 | rotundo, mitch, traemos, verdaderamente | otros temas | 0 | 0 | 0 | 1 | 48 | 1 | 1 | 49 |
| C15 | colega, cumpleaños, médico, besadme | otros temas | 1 | 0 | 0 | 0 | 34 | 1 | 1 | 35 |
| C23 | equipaje, tampón, bolsa, bolsillo | otros temas | 0 | 1 | 0 | 0 | 22 | 1 | 1 | 23 |
| C25 | paso, milla, corro, seguido | otros temas | 0 | 0 | 1 | 0 | 20 | 1 | 1 | 21 |
| C28 | entrega, sim, mes, pago | otros temas | 1 | 0 | 0 | 0 | 16 | 1 | 1 | 17 |
| C30 | lluvia, tormenta, sol, repentino | otros temas | 1 | 0 | 0 | 0 | 14 | 1 | 1 | 15 |
| C0 | cristiano, iglesia, dios, judío | otros temas | 0 | 0 | 0 | 0 | 180 | 0 | 0 | 180 |
| C6 | proyecto, desarrollador, vivienda, negocio | otros temas | 0 | 0 | 0 | 0 | 93 | 0 | 0 | 93 |
| C12 | marido, carne, batidos, leche | otros temas | 0 | 0 | 0 | 0 | 45 | 0 | 0 | 45 |
| C13 | tecnología, acción, ambicioso, fundador | otros temas | 0 | 0 | 0 | 0 | 39 | 0 | 0 | 39 |
| C14 | sitio, hecho, usuario, envío | otros temas | 0 | 0 | 0 | 0 | 37 | 0 | 0 | 37 |
| C16 | tarea, aplicación, app, foto | otros temas | 0 | 0 | 0 | 0 | 35 | 0 | 0 | 35 |
| C17 | entrada, vuelo, club, inglaterra | otros temas | 0 | 0 | 0 | 0 | 33 | 0 | 0 | 33 |
| C19 | extraño, correo, electrónico, terapia | otros temas | 0 | 0 | 0 | 0 | 27 | 0 | 0 | 27 |
| C20 | hora, presidente, kompany, wednesday | otros temas | 0 | 0 | 0 | 0 | 26 | 0 | 0 | 26 |
| C22 | voz, película, lotta, mandalorian | otros temas | 0 | 0 | 0 | 0 | 23 | 0 | 0 | 23 |
| C24 | mujer, gay, militar, feminista | otros temas | 0 | 0 | 0 | 0 | 22 | 0 | 0 | 22 |
| C26 | gracia, mentalmente, inolvidable, artista | otros temas | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 20 |
| C27 | publicación, hermano, post, hermoso | otros temas | 0 | 0 | 0 | 0 | 19 | 0 | 0 | 19 |
| C29 | efecto, phat, indeed, yes | otros temas | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 16 |
| sin texto útil | — | sin texto útil | 0 | 0 | 0 | 0 | 88 | 0 | 0 | 88 |
| Total |  |  | 104 | 25 | 71 | 25 | 2487 | 225 | 144 | 2631 |

Series de la gráfica (de abajo hacia arriba en cada barra), con su color:

| Serie | Color | Clusters | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Ningún indicador |
|---|---|---|---:|---:|---:|---:|---:|
| C4 · méxico, viaje, ciudad, hora | #e87ba4 | C4 | 38 | 2 | 25 | 1 | 58 |
| C10 · méxico, mexicano, gente, japón | #0369a1 | C10 | 21 | 11 | 7 | 15 | 24 |
| C8 · vegetarian, ensalada, queso, recipes | #7c3aed | C8 | 2 | 0 | 12 | 0 | 48 |
| C11 · estadio, york, autobús, impresionante | #65a30d | C11 | 2 | 3 | 4 | 0 | 40 |
| C21 · imbécil, llama, pedófilo, zorra | #a16207 | C21 | 3 | 0 | 0 | 0 | 21 |
| otros temas (26 clusters con menos de 3 menciones) | #dcdad2 | C3, C5, C7, C18, C1, C2, C9, C15, C23, C25, C28, C30, C0, C6, C12, C13, C14, C16, C17, C19, C20, C22, C24, C26, C27, C29 | 7 | 2 | 4 | 3 | 1355 |
| ruido (sin cluster) | #8f8e83 | ruido | 31 | 7 | 19 | 6 | 853 |
| sin texto útil (fuera del agrupamiento) | #ebe9e2 | sin texto | 0 | 0 | 0 | 0 | 88 |
| Total |  |  | 104 | 25 | 71 | 25 | 2487 |

## 3b. Tuits calificados en un solo indicador

Es la tabla de `salida/barras_indicador_unico_tema.png`. Aquí cada tuit calificado cuenta **una sola vez**: en la columna de su indicador si habla exactamente de uno (84 tuits), o en «Varios indicadores» si habla de dos o más (60 tuits). Las cinco columnas suman los 144 calificados. Solo se listan los temas con algún calificado; los colores son los mismos de la gráfica anterior.

| Tema | Términos | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Varios indicadores | Un solo indicador | Tuits calificados |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| C4 | méxico, viaje, ciudad, hora | 15 | 0 | 3 | 0 | 23 | 18 | 41 |
| ruido | — | 18 | 1 | 10 | 1 | 14 | 30 | 44 |
| C10 | méxico, mexicano, gente, japón | 5 | 0 | 1 | 0 | 17 | 6 | 23 |
| C8 | vegetarian, ensalada, queso, recipes | 0 | 0 | 10 | 0 | 2 | 10 | 12 |
| C11 | estadio, york, autobús, impresionante | 0 | 1 | 2 | 0 | 3 | 3 | 6 |
| C21 | imbécil, llama, pedófilo, zorra | 3 | 0 | 0 | 0 | 0 | 3 | 3 |
| C3 | yonna, streamer, chica, stream | 0 | 0 | 1 | 1 | 0 | 2 | 2 |
| C5 | partido, copa, fútbol, mundo | 2 | 0 | 0 | 0 | 0 | 2 | 2 |
| C7 | lindo, genial, increíble, favor | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| C18 | fujisawa, kai, hit, kamakura | 1 | 0 | 1 | 0 | 0 | 2 | 2 |
| C1 | especial, correcto, palabra, entrepierna | 0 | 1 | 0 | 0 | 0 | 1 | 1 |
| C2 | jugador, portero, fichaje, ince | 0 | 0 | 0 | 1 | 0 | 1 | 1 |
| C9 | rotundo, mitch, traemos, verdaderamente | 0 | 0 | 0 | 1 | 0 | 1 | 1 |
| C15 | colega, cumpleaños, médico, besadme | 1 | 0 | 0 | 0 | 0 | 1 | 1 |
| C23 | equipaje, tampón, bolsa, bolsillo | 0 | 1 | 0 | 0 | 0 | 1 | 1 |
| C25 | paso, milla, corro, seguido | 0 | 0 | 1 | 0 | 0 | 1 | 1 |
| C28 | entrega, sim, mes, pago | 1 | 0 | 0 | 0 | 0 | 1 | 1 |
| C30 | lluvia, tormenta, sol, repentino | 1 | 0 | 0 | 0 | 0 | 1 | 1 |
| Total |  | 47 | 4 | 29 | 4 | 60 | 84 | 144 |

Series de la gráfica (de abajo hacia arriba en cada barra):

| Serie | Color | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Varios indicadores | Total |
|---|---|---:|---:|---:|---:|---:|---:|
| C4 · méxico, viaje, ciudad, hora | #e87ba4 | 15 | 0 | 3 | 0 | 23 | 41 |
| C10 · méxico, mexicano, gente, japón | #0369a1 | 5 | 0 | 1 | 0 | 17 | 23 |
| C8 · vegetarian, ensalada, queso, recipes | #7c3aed | 0 | 0 | 10 | 0 | 2 | 12 |
| C11 · estadio, york, autobús, impresionante | #65a30d | 0 | 1 | 2 | 0 | 3 | 6 |
| C21 · imbécil, llama, pedófilo, zorra | #a16207 | 3 | 0 | 0 | 0 | 0 | 3 |
| otros temas (26 clusters con menos de 3 menciones) | #dcdad2 | 6 | 2 | 3 | 3 | 1 | 15 |
| ruido (sin cluster) | #8f8e83 | 18 | 1 | 10 | 1 | 14 | 44 |
| Total |  | 47 | 4 | 29 | 4 | 60 | 144 |

## 3c. Cruces de indicadores por tema (heatmaps)

Es la tabla de `salida/heatmaps_cruces_tema.png`. Universo: **los 60 tuits calificados en dos o más indicadores** (la barra «Varios indicadores» de la gráfica 3b). Cada fila es un cruce de dos indicadores, o un indicador consigo mismo (cuántos de esos 60 hablan de él). «Total» son los tuits que hablan de ambos; en cada tema, cuántos de esos tuits pertenecen al tema y, entre paréntesis, su proporción sobre el total del cruce, que es lo que colorea el heatmap. Los cruces sin tuits se marcan con «—».

| Cruce | Total | C4 | C10 | C8 | C11 | otros temas | ruido |
|---|---:|---:|---:|---:|---:|---:|---:|
| Atmósfera (todos) | 57 | 23 (40%) | 16 (28%) | 2 (4%) | 2 (4%) | 1 (2%) | 13 (23%) |
| Atmósfera ∩ Perspectiva política | 18 | 2 (11%) | 10 (56%) | 0 (0%) | 1 (6%) | 0 (0%) | 5 (28%) |
| Atmósfera ∩ Imagen cultural | 40 | 22 (55%) | 6 (15%) | 2 (5%) | 1 (2%) | 1 (2%) | 8 (20%) |
| Atmósfera ∩ Saliencia de violencia | 20 | 1 (5%) | 14 (70%) | 0 (0%) | 0 (0%) | 0 (0%) | 5 (25%) |
| Perspectiva política (todos) | 21 | 2 (10%) | 11 (52%) | 0 (0%) | 2 (10%) | 0 (0%) | 6 (29%) |
| Perspectiva política ∩ Imagen cultural | 6 | 1 (17%) | 2 (33%) | 0 (0%) | 1 (17%) | 0 (0%) | 2 (33%) |
| Perspectiva política ∩ Saliencia de violencia | 14 | 0 (0%) | 11 (79%) | 0 (0%) | 0 (0%) | 0 (0%) | 3 (21%) |
| Imagen cultural (todos) | 42 | 22 (52%) | 6 (14%) | 2 (5%) | 2 (5%) | 1 (2%) | 9 (21%) |
| Imagen cultural ∩ Saliencia de violencia | 6 | 1 (17%) | 4 (67%) | 0 (0%) | 0 (0%) | 0 (0%) | 1 (17%) |
| Saliencia de violencia (todos) | 21 | 1 (5%) | 15 (71%) | 0 (0%) | 0 (0%) | 0 (0%) | 5 (24%) |

Clave: **C4** = C4 · méxico, viaje, ciudad, hora; **C10** = C10 · méxico, mexicano, gente, japón; **C8** = C8 · vegetarian, ensalada, queso, recipes; **C11** = C11 · estadio, york, autobús, impresionante; **otros temas** = otros temas (26 clusters con menos de 3 menciones); **ruido** = ruido (sin cluster).

## 3d. Idiomas por indicador (barras apiladas)

Es la tabla de `salida/barras_indicador_idioma.png`: las mismas cinco barras de la sección 3, pero apiladas por el idioma del tuit original (código `lang` de Twitter). Un tuit que habla de varios indicadores cuenta en cada columna. Los idiomas con color propio son en (inglés), ja (japonés), es (español), pt (portugués), fr (francés), it (italiano), nl (neerlandés), de (alemán); el resto se pliega en «otros idiomas».

| lang | Idioma | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Ningún indicador | Menciones | Tuits calificados | Tuits |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| en | inglés | 70 | 15 | 45 | 17 | 1966 | 147 | 93 | 2059 |
| ja | japonés | 29 | 10 | 23 | 8 | 387 | 70 | 45 | 432 |
| qme | solo multimedia | 0 | 0 | 0 | 0 | 64 | 0 | 0 | 64 |
| und | sin determinar | 1 | 0 | 1 | 0 | 21 | 2 | 1 | 22 |
| es | español | 3 | 0 | 2 | 0 | 8 | 5 | 4 | 12 |
| zxx | sin contenido lingüístico | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 8 |
| ht | criollo haitiano | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 5 |
| art | artificial | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 4 |
| in | indonesio | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 4 |
| tl | tagalo | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 4 |
| fr | francés | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 3 |
| pt | portugués | 1 | 0 | 0 | 0 | 2 | 1 | 1 | 3 |
| qam | solo menciones | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 |
| et | estonio | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| eu | vasco | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| fi | finés | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| it | italiano | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| no | noruego | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| pl | polaco | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| qht | solo hashtags | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| qst | muy corto | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| sv | sueco | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| Total |  | 104 | 25 | 71 | 25 | 2487 | 225 | 144 | 2631 |

Series de la gráfica (de abajo hacia arriba en cada barra):

| Serie | Color | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Ningún indicador | Códigos |
|---|---|---:|---:|---:|---:|---:|---|
| en · inglés | #2a78d6 | 70 | 15 | 45 | 17 | 1966 | en |
| ja · japonés | #be123c | 29 | 10 | 23 | 8 | 387 | ja |
| es · español | #1baf7a | 3 | 0 | 2 | 0 | 8 | es |
| pt · portugués | #eda100 | 1 | 0 | 0 | 0 | 2 | pt |
| fr · francés | #7c3aed | 0 | 0 | 0 | 0 | 3 | fr |
| it · italiano | #0d9488 | 0 | 0 | 0 | 0 | 1 | it |
| otros idiomas (16 códigos) | #dcdad2 | 1 | 0 | 1 | 0 | 120 | qme, und, zxx, ht, art, in, tl, qam, et, eu, fi, no, pl, qht, qst, sv |

## 3e. Tuits calificados en un solo indicador, por idioma

Es la tabla de `salida/barras_indicador_unico_idioma.png`: la misma lógica de la sección 3b (cada tuit calificado cuenta **una sola vez**, en su indicador si habla exactamente de uno o en «Varios indicadores» si habla de dos o más), apilada por idioma. Solo se listan los idiomas con algún calificado.

| lang | Idioma | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Varios indicadores | Un solo indicador | Tuits calificados |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| en | inglés | 32 | 2 | 16 | 2 | 41 | 52 | 93 |
| ja | japonés | 12 | 2 | 12 | 2 | 17 | 28 | 45 |
| und | sin determinar | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| es | español | 2 | 0 | 1 | 0 | 1 | 3 | 4 |
| pt | portugués | 1 | 0 | 0 | 0 | 0 | 1 | 1 |
| Total |  | 47 | 4 | 29 | 4 | 60 | 84 | 144 |

Series de la gráfica (de abajo hacia arriba en cada barra):

| Serie | Color | Atmósfera | Perspectiva política | Imagen cultural | Saliencia de violencia | Varios indicadores | Total | Códigos |
|---|---|---:|---:|---:|---:|---:|---:|---|
| en · inglés | #2a78d6 | 32 | 2 | 16 | 2 | 41 | 93 | en |
| ja · japonés | #be123c | 12 | 2 | 12 | 2 | 17 | 45 | ja |
| es · español | #1baf7a | 2 | 0 | 1 | 0 | 1 | 4 | es |
| pt · portugués | #eda100 | 1 | 0 | 0 | 0 | 0 | 1 | pt |
| otros idiomas (16 códigos) | #dcdad2 | 0 | 0 | 0 | 0 | 1 | 1 | qme, und, zxx, ht, art, in, tl, qam, et, eu, fi, no, pl, qht, qst, sv |

## 4. Lectura

- **El ruido es la categoría más grande** (897 tuits, 34.1 %): HDBSCAN no encontró para esos tuits una región densa a la que asignarlos. Es lo esperable con textos cortos y en varios idiomas; no es un tema y por eso el mapa lo pinta en gris tenue.
- **Los clusters son chicos y muchos.** El mayor, C0 (cristiano, iglesia, dios, judío), tiene 180 tuits (6.8 %); los cinco mayores suman 674 (25.6 %). Ningún tema domina el corpus.
- **Los calificados se concentran en pocos clusters.** 44 están en el ruido (30.6 % de los calificados) y el resto sobre todo en C4 · méxico, viaje, ciudad, hora (41 calificados, 41.4 % de su cluster); C10 · méxico, mexicano, gente, japón (23 calificados, 48.9 % de su cluster); C8 · vegetarian, ensalada, queso, recipes (12 calificados, 20.0 % de su cluster). Son los temas donde el mapa muestra los rombos apiñados.
- **14 clusters no tienen ningún calificado**: C0 · cristiano, iglesia, dios, judío, C6 · proyecto, desarrollador, vivienda, negocio, C12 · marido, carne, batidos, leche, C13 · tecnología, acción, ambicioso, fundador, C14 · sitio, hecho, usuario, envío, C16 · tarea, aplicación, app, foto, C17 · entrada, vuelo, club, inglaterra, C19 · extraño, correo, electrónico, terapia, C20 · hora, presidente, kompany, wednesday, C22 · voz, película, lotta, mandalorian, C24 · mujer, gay, militar, feminista, C26 · gracia, mentalmente, inolvidable, artista, C27 · publicación, hermano, post, hermoso, C29 · efecto, phat, indeed, yes. Son la parte del corpus que la rúbrica no toca.
- **Dónde se habla de México.** Los clusters con más mención del diccionario son C4 · méxico, viaje, ciudad, hora (63.6 %); C10 · méxico, mexicano, gente, japón (55.3 %); C30 · lluvia, tormenta, sol, repentino (26.7 %). Un cluster con mucha mención de México y pocos calificados es candidato a «tema fuera de la rúbrica».
- **Los nombres de los temas son orientativos.** Salen de cuatro lemas de la traducción automática; un cluster con textos en japonés o inglés mal traducidos puede recibir un nombre poco legible. Conviene leer los ejemplos del notebook antes de citarlos.
- **La partición depende de los parámetros** (`HDBSCAN_MIN_CLUSTER`, `UMAP_VECINOS`) y UMAP no es reproducible bit a bit entre máquinas. Con `--recalcular` se obtiene una partición parecida, no idéntica; las cifras de este archivo corresponden a `C:\Users\japhe\Downloads\resultados_enriquecidos.csv`.
