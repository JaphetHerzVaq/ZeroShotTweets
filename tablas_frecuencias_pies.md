# Tablas de frecuencias de las gráficas de pastel

Fuente: `tweets_calificados_anclada.csv` (2,631 tuits de 69 turistas).
Cálculo: las mismas funciones `leer`, `contar_criterio` y `construir` de `pies_rubrica.py`, sin modificaciones.
Corresponden a la gráfica `universo_corpus.png` (la dona de cobertura) y a las donas por criterio `pie_atmosfera.png`, `pie_perspectiva_politica.png` y `pie_imagen_cultural.png`.

En los cuatro criterios las cuentas cuadran: rebanadas + ausencia + bloqueados = 2,631.

## 1. Universo del corpus (cobertura)

Modo de cuatro indicadores: atmósfera, perspectiva política, imagen cultural y saliencia de violencia.

| Categoría | Tuits | % |
|---|---:|---:|
| Con calificación en atmósfera, perspectiva política, imagen cultural o violencia | 144 | 5.5 % |
| Sin calificación en ninguno de esos indicadores | 2,487 | 94.5 % |
| Total | 2,631 | 100 % |

- De los 144 calificados, 4 tuits solo mencionan violencia y no puntúan en ningún criterio de valencia.
- Con la opción de tres indicadores (`--indicadores tres`, solo los de valencia) el corte sería 140 (5.3 %) contra 2,491.
- Los 2,631 tuits provienen de 69 turistas; los 144 calificados, de 47.

## 2. Atmósfera de México (dimensión simpática / emocional)

| Nivel | Tuits | % del pastel | % del corpus |
|---|---:|---:|---:|
| 1 · muy negativo | 16 | 15.4 % | 0.6 % |
| 2 · negativo | 22 | 21.2 % | 0.8 % |
| 3 · ambivalente o mixto | 4 | 3.8 % | 0.2 % |
| 4 · positivo | 35 | 33.7 % | 1.3 % |
| 5 · muy positivo | 27 | 26.0 % | 1.0 % |
| Total en el pastel (nivel > 0) | 104 | 100 % | 4.0 % |

Fuera del pastel: 2,527 en ausencia (3 con nivel 0, el resto no aplicable), 0 bloqueados.

## 3. Perspectiva política de México (dimensión funcional)

| Nivel | Tuits | % del pastel | % del corpus |
|---|---:|---:|---:|
| 1 · muy negativo | 9 | 36.0 % | 0.3 % |
| 2 · negativo | 12 | 48.0 % | 0.5 % |
| 3 · ambivalente o mixto | 0 | 0.0 % | 0.0 % |
| 4 · positivo | 4 | 16.0 % | 0.2 % |
| 5 · muy positivo | 0 | 0.0 % | 0.0 % |
| Total en el pastel (nivel > 0) | 25 | 100 % | 1.0 % |

Fuera del pastel: 2,599 en ausencia (0 con nivel 0), 7 bloqueados por el proveedor.

## 4. Imagen cultural de México (dimensión estética)

| Nivel | Tuits | % del pastel | % del corpus |
|---|---:|---:|---:|
| 1 · muy negativo | 5 | 7.0 % | 0.2 % |
| 2 · negativo | 5 | 7.0 % | 0.2 % |
| 3 · ambivalente o mixto | 20 | 28.2 % | 0.8 % |
| 4 · positivo | 32 | 45.1 % | 1.2 % |
| 5 · muy positivo | 9 | 12.7 % | 0.3 % |
| Total en el pastel (nivel > 0) | 71 | 100 % | 2.7 % |

Fuera del pastel: 2,552 en ausencia (0 con nivel 0), 8 bloqueados.

## 5. Saliencia de violencia (escala de presencia, sin pastel)

Este criterio mide presencia, no valencia: un tuit que menciona violencia no es un tuit negativo. Por eso no tiene dona de niveles, aunque sí entra en el corte de cobertura.

| Nivel | Tuits |
|---|---:|
| 1 | 25 |
| 2 a 5 | 0 |
| Total con presencia (nivel > 0) | 25 |

Fuera: 2,604 en ausencia (79 con nivel 0), 2 bloqueados.

## Notas de lectura

Las reglas vienen del propio script y del notebook (celda 6); reimplementarlas de otra forma haría que estas tablas contaran distinto que el resto del trabajo.

- **Calificado** significa nivel mayor que 0 en algún criterio. Contar `aplicable = SI` daría 175, porque incluye tuits que el motor marcó aplicables y luego puntuó en 0.
- **Ausencia** junta el nivel 0 con `aplicable = NO`: el script los trata como la misma clase.
- **Bloqueado** (`aplicable = BLOQUEADO`) es dato faltante por el proveedor y nunca cuenta como ausencia.
- **% del pastel** se calcula sobre los tuits con nivel > 0 de ese criterio; **% del corpus**, sobre los 2,631.
- Los turistas se cuentan por `author_username`, no por `author_id`, porque la hoja de cálculo convirtió parte de los id a notación científica y contar por id inflaría el número de personas.
- Todas las rebanadas de las gráficas llevan la frecuencia además del porcentaje: con 4 tuits en un nivel y 35 en otro, el porcentaje solo miente sobre cuánta evidencia hay detrás.
