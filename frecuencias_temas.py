# -*- coding: utf-8 -*-
"""Frecuencias de los tuits de turistas que SI hablan de alguno de los cuatro
indicadores de la rubrica, cruzadas con el tema (cluster) del mapa UMAP.

Sirven para tres graficas de barras apiladas:

    1. por TEMA        una barra por cluster, apilada por indicador
    2. por INDICADOR   una barra por indicador, apilada por tema
    3. con SENTIMIENTO por tema e indicador, apilada por nivel de valencia 1-5

Entradas:

    tweets_calificados_anclada.csv   la rubrica: <criterio>_nivel / _aplicable
    resultados_enriquecidos.csv      la salida del notebook (seccion 16):
                                     nlp__cluster y nlp__topico por tuit. Es la
                                     misma asignacion que dibuja el mapa
                                     "Mapa del corpus - UMAP" de figuras_v3.html;
                                     no se recalcula aqui porque exige GPU.

Reglas, las mismas de pies_rubrica.py y del notebook:

    * "habla del indicador" = nivel > 0 en ese criterio. `aplicable = SI` con
      nivel 0 NO cuenta. BLOQUEADO es dato faltante.
    * un tuit puede hablar de varios indicadores: en las tablas por indicador
      cuenta en cada uno, y por eso la suma de una barra apilada por tema puede
      superar el numero de tuits distintos del tema. Se da tambien la cuenta
      de tuits distintos y la combinacion exacta de indicadores.
    * el cluster -1 es "ruido" (HDBSCAN no lo asigno) y el -2 "sin texto util".
      Los temas se nombran como en la leyenda del mapa: "C7 - lindo, genial,
      increible, favor".

Salidas (en salida/):

    frecuencias_temas_largo.csv   tema x indicador x nivel x n: la tabla unica
                                  de la que salen las tres graficas
    frecuencias_temas_resumen.csv una fila por tema, con totales
    tablas_frecuencias_temas.md   las tablas legibles

    python frecuencias_temas.py
    python frecuencias_temas.py --enriquecidos salida/resultados_enriquecidos.csv
"""
import argparse
import os

import pandas as pd

RUTA_CALIFICADOS = "tweets_calificados_anclada.csv"
RUTAS_ENRIQUECIDOS = [                      # se toma el primero que exista
    os.path.join("salida", "resultados_enriquecidos.csv"),
    os.path.join(os.path.expanduser("~"), "Downloads", "resultados_enriquecidos.csv"),
]
SALIDA_DIR = "salida"
RUTA_MD = "tablas_frecuencias_temas.md"

INDICADORES = [
    {"prefijo": "rubrica_1_atmosfera_de_mexic", "corto": "atmosfera",
     "etiqueta": "Atmósfera", "tipo": "valencia"},
    {"prefijo": "rubrica_3_perspectiva_politi", "corto": "perspectiva_politica",
     "etiqueta": "Perspectiva política", "tipo": "valencia"},
    {"prefijo": "rubrica_2_imagen_cultural_de", "corto": "imagen_cultural",
     "etiqueta": "Imagen cultural", "tipo": "valencia"},
    {"prefijo": "rubrica_4_saliencia_de_viole", "corto": "violencia",
     "etiqueta": "Saliencia de violencia", "tipo": "presencia"},
]
NIVELES_VALENCIA = {1: "1 · muy negativo", 2: "2 · negativo", 3: "3 · ambivalente o mixto",
                    4: "4 · positivo", 5: "5 · muy positivo"}
NIVELES_PRESENCIA = {1: "1 · presente"}


def leer_calificados(ruta):
    df = pd.read_csv(ruta, low_memory=False, dtype={"id": str})
    df["id"] = df["id"].astype(str).str.strip()
    for c in df.columns:
        if c.endswith("_nivel"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        if c.endswith("_aplicable"):
            df[c] = df[c].astype("string").str.strip().str.upper()
    return df


def leer_enriquecidos(ruta):
    e = pd.read_csv(ruta, low_memory=False, dtype={"id": str},
                    usecols=["id", "nlp__cluster", "nlp__topico"])
    e["id"] = e["id"].astype(str).str.strip()
    e["nlp__cluster"] = pd.to_numeric(e["nlp__cluster"], errors="coerce")
    return e.drop_duplicates("id")


def nombre_tema(cluster, topico):
    if pd.isna(cluster):
        return "sin cluster (no está en resultados_enriquecidos)"
    c = int(cluster)
    if c == -2:
        return "sin texto útil"
    if c == -1:
        return "ruido"
    top = "" if pd.isna(topico) else str(topico)
    return f"C{c} · {top}" if top else f"C{c}"


def construir(df, enr):
    """Devuelve (largo, resumen, combos, n_total, n_calificados)."""
    cols_nivel = [i["prefijo"] + "_nivel" for i in INDICADORES]
    df = df.merge(enr, on="id", how="left")
    df["tema"] = [nombre_tema(c, t) for c, t in zip(df["nlp__cluster"], df["nlp__topico"])]
    df["cluster"] = df["nlp__cluster"].fillna(-3).astype(int)   # -3 = sin cluster

    habla = (df[cols_nivel] > 0)
    habla.columns = [i["corto"] for i in INDICADORES]
    df["calificado"] = habla.any(axis=1)
    cal = df[df["calificado"]].copy()
    habla_cal = habla[df["calificado"]]

    # ---- tabla larga: tema x indicador x nivel ------------------------------
    filas = []
    for i in INDICADORES:
        niv = cal[i["prefijo"] + "_nivel"]
        sub = cal[niv > 0]
        g = sub.groupby(["cluster", "tema", niv[niv > 0].astype(int).rename("nivel")]).size()
        for (c, t, n), k in g.items():
            filas.append({"cluster": c, "tema": t, "indicador": i["corto"],
                          "indicador_etiqueta": i["etiqueta"], "nivel": n, "n": int(k)})
    largo = (pd.DataFrame(filas)
             .sort_values(["cluster", "indicador", "nivel"])
             .reset_index(drop=True))

    # ---- resumen por tema ----------------------------------------------------
    corpus_por_tema = df.groupby(["cluster", "tema"]).size().rename("tuits_corpus")
    cal_por_tema = cal.groupby(["cluster", "tema"]).size().rename("tuits_calificados")
    res = pd.concat([corpus_por_tema, cal_por_tema], axis=1).fillna(0).astype(int)
    for i in INDICADORES:
        res[i["corto"]] = (habla_cal[i["corto"]]
                           .groupby([cal["cluster"], cal["tema"]]).sum()
                           .reindex(res.index).fillna(0).astype(int))
    res["prop_calificados"] = (res["tuits_calificados"] / res["tuits_corpus"]).round(3)
    # cuantos indicadores toca cada tuit calificado, promediado por tema
    res["indicadores_por_tuit"] = (habla_cal.sum(axis=1)
                                   .groupby([cal["cluster"], cal["tema"]]).mean()
                                   .reindex(res.index).round(2))
    resumen = res.reset_index().sort_values("cluster").reset_index(drop=True)

    # ---- combinacion exacta de indicadores por tuit -------------------------
    combo = habla_cal.apply(
        lambda r: " + ".join(i["etiqueta"] for i in INDICADORES if r[i["corto"]]), axis=1)
    combos = (combo.value_counts().rename_axis("combinacion").reset_index(name="tuits")
              .sort_values("tuits", ascending=False).reset_index(drop=True))
    combos_tema = (pd.crosstab([cal["cluster"], cal["tema"]], combo)
                   .reset_index().sort_values("cluster"))

    return largo, resumen, combos, combos_tema, len(df), int(df["calificado"].sum())


# ---------------------------------------------------------------------------
#  Markdown
# ---------------------------------------------------------------------------

def _tabla(cabecera, filas, alineacion=None):
    ali = alineacion or ["---"] + ["---:"] * (len(cabecera) - 1)
    out = ["| " + " | ".join(str(c) for c in cabecera) + " |",
           "|" + "|".join(ali) + "|"]
    for f in filas:
        out.append("| " + " | ".join(str(x) for x in f) + " |")
    return "\n".join(out)


def _pct(n, t):
    return f"{100 * n / t:.1f} %" if t else "—"


def render_md(largo, resumen, combos, combos_tema, n_total, n_cal, ruta_enr):
    con_cal = resumen[resumen["tuits_calificados"] > 0]
    sin_cal = resumen[resumen["tuits_calificados"] == 0]
    etiquetas = {i["corto"]: i["etiqueta"] for i in INDICADORES}
    L = []
    L.append("# Frecuencias por tema e indicador (tuits que sí hablan de la rúbrica)\n")
    L.append(f"Fuente de la rúbrica: `{RUTA_CALIFICADOS}` ({n_total:,} tuits). "
             f"Fuente de los temas: `{os.path.basename(ruta_enr)}` (columnas `nlp__cluster` y "
             "`nlp__topico`, la misma asignación del mapa UMAP de la sección 16 del notebook). "
             "Generado por `frecuencias_temas.py`.\n")
    L.append(f"Universo: los {n_cal} tuits con nivel mayor que 0 en al menos un indicador "
             f"({_pct(n_cal, n_total)} del corpus). Aparecen en {len(con_cal)} temas; "
             f"los otros {len(sin_cal)} clusters no tienen ningún tuit calificado.\n")

    # ---- 1. por tema ---------------------------------------------------------
    L.append("## 1. Por tema, apilado por indicador\n")
    L.append("Cada celda es el número de tuits calificados del tema que hablan de ese indicador. "
             "Un tuit puede hablar de varios, así que la suma de la barra puede superar la columna "
             "«Tuits calificados» (distintos). «Indicadores por tuit» es ese cociente.\n")
    cab = ["Tema"] + [etiquetas[i["corto"]] for i in INDICADORES] + \
          ["Suma (barra)", "Tuits calificados", "Tuits del tema", "% calificados", "Indicadores por tuit"]
    filas = []
    for _, r in con_cal.iterrows():
        vals = [r[i["corto"]] for i in INDICADORES]
        filas.append([r["tema"]] + vals + [sum(vals), r["tuits_calificados"], r["tuits_corpus"],
                                           _pct(r["tuits_calificados"], r["tuits_corpus"]),
                                           f"{r['indicadores_por_tuit']:.2f}"])
    tot = [int(con_cal[i["corto"]].sum()) for i in INDICADORES]
    filas.append(["Total"] + tot + [sum(tot), int(con_cal["tuits_calificados"].sum()),
                                    int(resumen["tuits_corpus"].sum()),
                                    _pct(n_cal, n_total),
                                    f"{sum(tot) / n_cal:.2f}"])
    L.append(_tabla(cab, filas))
    L.append("")
    L.append("Clusters sin ningún tuit calificado: " +
             ", ".join(f"{r['tema']} ({r['tuits_corpus']})" for _, r in sin_cal.iterrows()) + ".\n")

    # ---- 2. por indicador ----------------------------------------------------
    L.append("## 2. Por indicador, apilado por tema\n")
    L.append("La misma matriz transpuesta: una barra por indicador, cuyos segmentos son los temas. "
             "El total de cada barra es el número de tuits que hablan de ese indicador.\n")
    cab = ["Indicador"] + list(con_cal["tema"]) + ["Total"]
    filas = []
    for i in INDICADORES:
        vals = [int(v) for v in con_cal[i["corto"]]]
        filas.append([i["etiqueta"]] + vals + [sum(vals)])
    L.append(_tabla(cab, filas))
    L.append("")
    L.append("Combinaciones exactas de indicadores por tuit (cada tuit cuenta una sola vez):\n")
    L.append(_tabla(["Combinación", "Tuits", "%"],
                    [[r["combinacion"], r["tuits"], _pct(r["tuits"], n_cal)] for _, r in combos.iterrows()]))
    L.append("")

    # ---- 3. sentimiento ------------------------------------------------------
    L.append("## 3. Por tema e indicador, apilado por nivel de valencia\n")
    L.append("Para cada indicador de valencia, los tuits del tema repartidos por nivel 1 a 5. "
             "La columna «neg / amb / pos» agrupa 1-2, 3 y 4-5. Saliencia de violencia es de presencia "
             "(solo nivel 1) y se lista al final sin valencia.\n")
    for i in INDICADORES:
        sub = largo[largo["indicador"] == i["corto"]]
        if sub.empty:
            continue
        niveles = NIVELES_PRESENCIA if i["tipo"] == "presencia" else NIVELES_VALENCIA
        piv = (sub.pivot_table(index=["cluster", "tema"], columns="nivel", values="n",
                               aggfunc="sum", fill_value=0)
               .reindex(columns=list(niveles), fill_value=0)
               .reset_index().sort_values("cluster"))
        L.append(f"### {i['etiqueta']}\n")
        if i["tipo"] == "valencia":
            cab = ["Tema"] + list(niveles.values()) + ["Total", "neg / amb / pos", "Nivel medio"]
            filas = []
            for _, r in piv.iterrows():
                v = [int(r[n]) for n in niveles]
                t = sum(v)
                neg, amb, pos = v[0] + v[1], v[2], v[3] + v[4]
                medio = sum(n * k for n, k in zip(niveles, v)) / t if t else 0
                filas.append([r["tema"]] + v + [t, f"{neg} / {amb} / {pos}", f"{medio:.2f}"])
            tv = [int(piv[n].sum()) for n in niveles]
            tt = sum(tv)
            filas.append(["Total"] + tv + [tt, f"{tv[0] + tv[1]} / {tv[2]} / {tv[3] + tv[4]}",
                                          f"{sum(n * k for n, k in zip(niveles, tv)) / tt:.2f}"])
        else:
            cab = ["Tema", "1 · presente"]
            filas = [[r["tema"], int(r[1])] for _, r in piv.iterrows()]
            filas.append(["Total", int(piv[1].sum())])
        L.append(_tabla(cab, filas))
        L.append("")

    # ---- notas ---------------------------------------------------------------
    L.append("## Notas de lectura\n")
    L.append("- **Habla del indicador** = nivel mayor que 0 en ese criterio. Es la definición del notebook y "
             "de `pies_rubrica.py`; contar `aplicable = SI` daría más, porque incluye tuits marcados "
             "aplicables y puntuados en 0. BLOQUEADO es dato faltante y no cuenta.")
    L.append("- **Tema** es el cluster de HDBSCAN sobre el UMAP de los embeddings del texto original, con "
             "los cuatro términos más distintivos (c-TF-IDF sobre lemas de la traducción) como nombre. "
             "«ruido» es el cluster −1 (sin asignar) y «sin texto útil» el −2. Los clusters dependen de "
             "`HDBSCAN_MIN_CLUSTER` y `UMAP_VECINOS`; no son categorías fijas.")
    L.append("- La asignación de temas se lee de `resultados_enriquecidos.csv`, que produjo el notebook en "
             "Colab. Si se vuelve a correr el notebook con otros parámetros, hay que volver a correr este "
             "script.")
    L.append("- En la gráfica por tema los segmentos son indicadores y un tuit puede aportar a varios; en la "
             "gráfica por indicador cada tuit aporta a un solo segmento (su tema). Por eso las sumas "
             "coinciden por indicador pero no con los tuits distintos.")
    L.append("- El **nivel medio** es orientativo: con 2 o 3 tuits en un tema no describe nada. Las cuentas "
             "absolutas van siempre al lado.")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calificados", default=RUTA_CALIFICADOS)
    ap.add_argument("--enriquecidos", default=None,
                    help="CSV con nlp__cluster y nlp__topico (por omisión: salida/ y luego Downloads)")
    ap.add_argument("--salida-dir", default=SALIDA_DIR)
    ap.add_argument("--md", default=RUTA_MD)
    args = ap.parse_args()

    ruta_enr = args.enriquecidos or next((r for r in RUTAS_ENRIQUECIDOS if os.path.exists(r)), None)
    if not ruta_enr or not os.path.exists(ruta_enr):
        raise SystemExit("No encuentro resultados_enriquecidos.csv; pásalo con --enriquecidos.")

    df = leer_calificados(args.calificados)
    enr = leer_enriquecidos(ruta_enr)
    largo, resumen, combos, combos_tema, n_total, n_cal = construir(df, enr)

    os.makedirs(args.salida_dir, exist_ok=True)
    r_largo = os.path.join(args.salida_dir, "frecuencias_temas_largo.csv")
    r_res = os.path.join(args.salida_dir, "frecuencias_temas_resumen.csv")
    r_combo = os.path.join(args.salida_dir, "frecuencias_temas_combinaciones.csv")
    largo.to_csv(r_largo, index=False, encoding="utf-8-sig")
    resumen.to_csv(r_res, index=False, encoding="utf-8-sig")
    combos_tema.to_csv(r_combo, index=False, encoding="utf-8-sig")

    md = render_md(largo, resumen, combos, combos_tema, n_total, n_cal, ruta_enr)
    with open(args.md, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    for r in (r_largo, r_res, r_combo, args.md):
        print(f"[escrito] {r}")


if __name__ == "__main__":
    main()
