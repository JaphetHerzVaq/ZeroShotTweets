# -*- coding: utf-8 -*-
"""Mapa UMAP de los clusters del corpus y frecuencias por cluster.

Reproduce, fuera del notebook, la figura "Mapa del corpus · UMAP de los
embeddings del texto original" de la seccion 16 (rediseno_zeroshot_colab_v4)
y anade una dona con las frecuencias por cluster, la tabla de frecuencias y
un .md con las tablas.

Dos modos:

    python clusters_umap.py
        Usa la asignacion YA CALCULADA por el notebook (resultados_enriquecidos.csv:
        nlp__cluster, nlp__topico, nlp__umap_x, nlp__umap_y). Reproduce la
        figura punto por punto y no necesita GPU ni modelos.

    python clusters_umap.py --recalcular
        Rehace todo el pipeline desde tweets_calificados_anclada.csv, con los
        mismos parametros del notebook:

            texto original limpio -> embeddings multilingues (mpnet)
                -> UMAP 10 dim (agrupar) y 2 dim (dibujar)
                -> HDBSCAN (clusters y ruido = -1), renumerado por tamano
            traduccion -> spaCy (lemas NOUN/PROPN/ADJ) -> c-TF-IDF por cluster
                -> nombre del tema = 4 terminos mas distintivos

        Necesita sentence-transformers (+torch), umap-learn, hdbscan (o el
        HDBSCAN de scikit-learn como respaldo) y spaCy con es_core_news_lg.
        UMAP y HDBSCAN NO son bit a bit reproducibles entre maquinas y versiones:
        la particion sera parecida a la del notebook, no identica. La salida se
        guarda en salida/resultados_clusters.csv y la figura se dibuja de ahi;
        a partir de entonces el modo por defecto la prefiere sobre la del
        notebook (borra ese archivo para volver a la del notebook).

        Comprobado el 2026-09-24 en CPU (umap-learn 0.5.12, hdbscan 0.8.44):
        34 clusters y 33.1 % de ruido frente a 31 y 34.1 % en Colab; los
        temas grandes coinciden (cristiano/iglesia, mexico/viaje con 44
        calificados, mexico/mexicano/japon con 24, vegetarian/ensalada,
        proyecto/desarrollador, partido/copa...) con otra numeracion.
        Tarda unos 5 minutos en CPU.

Reglas (las mismas del notebook y de frecuencias_temas.py):

    * cluster -1 = ruido (HDBSCAN no lo asigno); -2 = sin texto util (tras
      quitar enlaces y menciones quedan menos de 3 letras; no entra a UMAP y
      por eso no aparece en el mapa).
    * "calificado" = nivel > 0 en al menos un indicador de la rubrica. En el
      mapa lleva rombo con borde negro.
    * los 15 clusters mas grandes tienen color propio (misma paleta que el
      notebook, en el mismo orden); del 16 en adelante van en gris claro como
      "otros clusters".

Salidas (en salida/ salvo el .md):

    mapa_umap_clusters.png        la figura del mapa
    dona_clusters.png             dona: corpus completo y calificados, por cluster
    frecuencias_clusters.csv      una fila por cluster (n, calificados, Mexico, ...)
    frecuencias_indicador_tema.csv        indicador x tema (un tuit cuenta en cada indicador)
    frecuencias_indicador_unico_tema.csv  igual, solo tuits con UN indicador (+ varios)
    barras_indicador_tema.png             barras apiladas por tema: 4 indicadores + ninguno
    barras_indicador_unico_tema.png       barras apiladas: un solo indicador + varios
    heatmaps_cruces_tema.png              indicador x indicador por tema (preponderancia)
    barras_indicador_idioma.png           barras apiladas por idioma: 4 indicadores + ninguno
    frecuencias_indicador_idioma.csv      indicador x idioma
    barras_indicador_unico_idioma.png     barras apiladas por idioma: un solo indicador + varios
    frecuencias_indicador_unico_idioma.csv  igual, solo tuits con UN indicador (+ varios)
    frecuencias_cruces_tema.csv           la tabla larga de esos cruces
    resultados_clusters.csv       solo con --recalcular: id, cluster, topico, umap
    tablas_frecuencias_clusters.md  las tablas legibles con comentarios
"""
import argparse
import os
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# rutas y columnas
# --------------------------------------------------------------------------
RUTA_CALIFICADOS = "tweets_calificados_anclada.csv"
RUTAS_ENRIQUECIDOS = [                        # se toma el primero que exista
    os.path.join("salida", "resultados_clusters.csv"),
    os.path.join("salida", "resultados_enriquecidos.csv"),
    os.path.join(os.path.expanduser("~"), "Downloads", "resultados_enriquecidos.csv"),
]
SALIDA_DIR = "salida"
RUTA_MD = "tablas_frecuencias_clusters.md"

COL_ID = "id"
COL_TEXTO = "text"
COL_TRADUCCION = "traducción"
COL_LANG = "lang"
COL_BASE = "base"
# Los cuatro indicadores de la rubrica, en el orden en que se dibujan.
# "habla del indicador" = nivel > 0 (igual que pies_rubrica.py y frecuencias_temas.py).
INDICADORES = [
    {"prefijo": "rubrica_1_atmosfera_de_mexic", "corto": "atmosfera", "etiqueta": "Atmósfera"},
    {"prefijo": "rubrica_3_perspectiva_politi", "corto": "perspectiva_politica", "etiqueta": "Perspectiva política"},
    {"prefijo": "rubrica_2_imagen_cultural_de", "corto": "imagen_cultural", "etiqueta": "Imagen cultural"},
    {"prefijo": "rubrica_4_saliencia_de_viole", "corto": "violencia", "etiqueta": "Saliencia de violencia"},
]

# --------------------------------------------------------------------------
# parametros del notebook (seccion 16)
# --------------------------------------------------------------------------
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
LOTE_EMBEDDINGS = 64
MODELO_SPACY = "es_core_news_lg"
LOTE_SPACY = 64
SEMILLA_NLP = 42
MIN_LETRAS_TEXTO_UTIL = 3
UMAP_VECINOS = 15
UMAP_DIM_CLUSTER = 10
UMAP_MIN_DIST = 0.0
HDBSCAN_MIN_CLUSTER = 15
HDBSCAN_MIN_SAMPLES = 5
TOP_TERMINOS = 10
POS_LEMAS = {"NOUN", "PROPN", "ADJ"}

# --------------------------------------------------------------------------
# paleta: la misma PAL del notebook, en el mismo orden (C0 -> PAL[0], ...)
# --------------------------------------------------------------------------
PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#4a3aa7", "#0d9488", "#b45309",
       "#7c3aed", "#be123c", "#0369a1", "#65a30d", "#c2410c", "#9333ea", "#0f766e"]
COLOR_RUIDO = "#c3c2b7"
COLOR_OTROS = "#dcdad2"
COLOR_SIN_TEXTO = "#ebe9e2"
COLOR_FONDO = "#fafafa"
COLOR_TINTA = "#1f1f1f"
COLOR_TINTA2 = "#4b4b4b"

# --- barras apiladas por indicador -------------------------------------------
# Un tema recibe color propio en las barras si suma al menos MIN_MENCIONES_COLOR
# menciones entre los cuatro indicadores (hasta MAX_TEMAS_COLOR temas); los
# demas se pliegan en "otros temas". Los clusters C0-C14 conservan el color del
# mapa (el color sigue al tema, no a su rango); los C15+ toman uno de PAL_EXTRA,
# que no se repite con la paleta del mapa. El ruido va en gris oscuro con trama
# para distinguirlo de "otros temas" (gris claro). Paleta validada con el
# comprobador de dataviz (pares adyacentes dE >= 8 en CVD, >= 15 en vision
# normal); el rosa y el verde lima quedan bajo 3:1 de contraste con el fondo,
# por eso todos los segmentos llevan la cifra escrita.
MIN_MENCIONES_COLOR = 3
MAX_TEMAS_COLOR = 8
PAL_EXTRA = ["#a16207", "#7f1d1d", "#155e75", "#4d7c0f", "#831843"]
COLOR_RUIDO_BARRA = "#8f8e83"
COLOR_OTROS_TEMAS = "#dcdad2"
NINGUNO = "Ningún indicador"      # quinta barra: tuits con nivel 0 (o faltante) en los cuatro
VARIOS = "Varios indicadores"     # segunda grafica: tuits con nivel > 0 en dos o mas

# --- barras apiladas por idioma ------------------------------------------------
# Idiomas con color propio (columna `lang` de Twitter), en el orden de apilado;
# un idioma sin tuits no genera serie. Los demas se pliegan en "otros idiomas". Paleta validada con el comprobador de dataviz (pares
# adyacentes dE >= 9 en CVD, >= 22 en vision normal); el verde y el ambar quedan
# bajo 3:1 de contraste con el fondo, por eso los segmentos llevan la cifra escrita.
IDIOMAS = [("en", "inglés", "#2a78d6"), ("ja", "japonés", "#be123c"), ("es", "español", "#1baf7a"),
           ("pt", "portugués", "#eda100"), ("fr", "francés", "#7c3aed"), ("it", "italiano", "#0d9488"),
           ("nl", "neerlandés", "#b45309"), ("de", "alemán", "#4a3aa7")]   # solo si hay tuits en ese idioma
COLOR_OTROS_IDIOMAS = "#dcdad2"
NOMBRE_LANG = {"pt": "portugués", "fr": "francés", "it": "italiano", "und": "sin determinar",
               "qme": "solo multimedia", "zxx": "sin contenido lingüístico", "ht": "criollo haitiano",
               "in": "indonesio", "tl": "tagalo", "art": "artificial", "qam": "solo menciones",
               "sv": "sueco", "fi": "finés", "eu": "vasco", "et": "estonio", "pl": "polaco",
               "no": "noruego", "qst": "muy corto", "qht": "solo hashtags"}

_URL = re.compile(r"https?://\S+|www\.\S+", re.I)
_MENCION = re.compile(r"(?<!\w)@\w+")
_LETRA = re.compile(r"[^\W\d_]", re.U)


# ==========================================================================
# 1. lectura
# ==========================================================================
def leer_calificados(ruta=RUTA_CALIFICADOS):
    df = pd.read_csv(ruta, encoding="utf-8-sig", low_memory=False, dtype={COL_ID: str})
    df[COL_ID] = df[COL_ID].astype(str).str.strip()
    for i in INDICADORES:
        df[i["prefijo"] + "_nivel"] = pd.to_numeric(df[i["prefijo"] + "_nivel"], errors="coerce")
        df["habla_" + i["corto"]] = df[i["prefijo"] + "_nivel"] > 0
    df["calificado"] = df[["habla_" + i["corto"] for i in INDICADORES]].any(axis=1)
    return df


def buscar_enriquecidos(ruta=None):
    candidatos = [ruta] if ruta else RUTAS_ENRIQUECIDOS
    for r in candidatos:
        if r and os.path.exists(r):
            return r
    sys.exit("No encuentro resultados_enriquecidos.csv (busque en {}). Pasa --enriquecidos RUTA "
             "o corre con --recalcular.".format(", ".join(candidatos)))


def leer_enriquecidos(ruta):
    cols = ["id", "nlp__cluster", "nlp__topico", "nlp__umap_x", "nlp__umap_y"]
    e = pd.read_csv(ruta, low_memory=False, dtype={"id": str})
    extra = [c for c in ("nlp__menciona_mexico",) if c in e.columns]
    e = e[cols + extra].copy()
    e["id"] = e["id"].astype(str).str.strip()
    e["nlp__cluster"] = pd.to_numeric(e["nlp__cluster"], errors="coerce")
    for c in ("nlp__umap_x", "nlp__umap_y"):
        e[c] = pd.to_numeric(e[c], errors="coerce")
    if "nlp__menciona_mexico" in e:
        e["nlp__menciona_mexico"] = e["nlp__menciona_mexico"].map(
            lambda v: str(v).strip().lower() in ("true", "1", "si", "sí", "yes"))
    return e.drop_duplicates("id")


# ==========================================================================
# 2. pipeline completo (solo con --recalcular)
# ==========================================================================
def limpiar(texto):
    """Enlaces fuera y menciones fuera: no dicen de que habla el tuit."""
    t = _URL.sub(" ", str(texto or ""))
    t = _MENCION.sub(" ", t)
    t = t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", t).strip()


def _version(paquete):
    import importlib.metadata as md
    try:
        return md.version(paquete)
    except md.PackageNotFoundError:
        return None


def recalcular(df):
    """Devuelve (DataFrame con las columnas nlp__*, ficha tecnica)."""
    import gc

    df = df.copy()
    df["texto_limpio"] = df[COL_TEXTO].map(limpiar)
    df["traduccion_limpia"] = df[COL_TRADUCCION].map(limpiar) if COL_TRADUCCION in df else ""
    df["texto_util"] = df["texto_limpio"].map(lambda t: len(_LETRA.findall(t)) >= MIN_LETRAS_TEXTO_UTIL)
    util = df[df.texto_util].reset_index(drop=True)
    print("texto util: {} de {} tuits ({} sin texto util, fuera del agrupamiento)".format(
        len(util), len(df), int((~df.texto_util).sum())))

    # --- embeddings del texto ORIGINAL ---------------------------------------
    import torch
    from sentence_transformers import SentenceTransformer
    disp = "cuda" if torch.cuda.is_available() else "cpu"
    print("embeddings: {} sobre {} textos ({})...".format(MODELO_EMBEDDINGS, len(util), disp))
    modelo = SentenceTransformer(MODELO_EMBEDDINGS, device=disp)
    emb = modelo.encode(util["texto_limpio"].tolist(), batch_size=LOTE_EMBEDDINGS,
                        show_progress_bar=True, normalize_embeddings=True, convert_to_numpy=True)
    del modelo
    gc.collect()

    # --- UMAP: 10 dim para agrupar, 2 para dibujar ----------------------------
    try:
        import umap
        reductor = "umap-learn " + str(_version("umap-learn"))
        r10 = umap.UMAP(n_neighbors=UMAP_VECINOS, n_components=UMAP_DIM_CLUSTER, min_dist=UMAP_MIN_DIST,
                        metric="cosine", random_state=SEMILLA_NLP).fit_transform(emb)
        r2 = umap.UMAP(n_neighbors=UMAP_VECINOS, n_components=2, min_dist=0.1,
                       metric="cosine", random_state=SEMILLA_NLP).fit_transform(emb)
    except ImportError:
        from sklearn.decomposition import PCA
        print("   AVISO: umap-learn no esta instalado; se usa PCA (clusters peores).")
        reductor = "PCA (respaldo: umap-learn no disponible)"
        r10 = PCA(n_components=UMAP_DIM_CLUSTER, random_state=SEMILLA_NLP).fit_transform(emb)
        r2 = PCA(n_components=2, random_state=SEMILLA_NLP).fit_transform(emb)

    # --- HDBSCAN ---------------------------------------------------------------
    try:
        import hdbscan
        agr = hdbscan.HDBSCAN(min_cluster_size=HDBSCAN_MIN_CLUSTER, min_samples=HDBSCAN_MIN_SAMPLES,
                              metric="euclidean", cluster_selection_method="eom").fit(r10)
        agrupador = "hdbscan " + str(_version("hdbscan"))
    except ImportError:
        from sklearn.cluster import HDBSCAN as SkHDBSCAN
        agr = SkHDBSCAN(min_cluster_size=HDBSCAN_MIN_CLUSTER, min_samples=HDBSCAN_MIN_SAMPLES).fit(r10)
        agrupador = "sklearn.cluster.HDBSCAN (respaldo) · scikit-learn " + str(_version("scikit-learn"))
    etq = np.asarray(agr.labels_)
    prob = np.asarray(getattr(agr, "probabilities_", np.ones(len(etq))))

    # renumerar por tamano: C0 es el mas grande; el ruido sigue en -1
    tam = pd.Series(etq[etq >= 0]).value_counts()
    mapa = {viejo: nuevo for nuevo, viejo in enumerate(tam.index)}
    mapa[-1] = -1
    util["nlp__cluster"] = [mapa[int(e)] for e in etq]
    util["prob_cluster"] = prob
    util["nlp__umap_x"] = r2[:, 0]
    util["nlp__umap_y"] = r2[:, 1]
    print("AGRUPAMIENTO: {} clusters · {} · {} · ruido {:.1%}".format(
        len(tam), reductor, agrupador, (etq == -1).mean()))

    # --- lemas de la TRADUCCION con spaCy y topicos c-TF-IDF ------------------
    import math
    import spacy
    if not spacy.util.is_package(MODELO_SPACY):
        sys.exit("Falta el modelo de spaCy {}: python -m spacy download {}".format(MODELO_SPACY, MODELO_SPACY))
    nlp = spacy.load(MODELO_SPACY, disable=["ner", "parser"])
    print("spaCy {} sobre {} traducciones...".format(MODELO_SPACY, len(util)))
    lemas = []
    for doc in nlp.pipe(util["traduccion_limpia"].tolist(), batch_size=LOTE_SPACY):
        lemas.append([t.lemma_.lower() for t in doc
                      if t.pos_ in POS_LEMAS and t.is_alpha and not t.is_stop and len(t.text) > 2])
    util["lemas"] = lemas

    conteos = {c: Counter(w for lst in g["lemas"] for w in lst) for c, g in util.groupby("nlp__cluster")}
    tot = Counter()
    for cnt in conteos.values():
        tot.update(cnt)
    A = np.mean([sum(c.values()) for c in conteos.values()]) if conteos else 1.0

    def ctfidf(cnt):
        n = sum(cnt.values()) or 1
        return sorted(((w, (f / n) * math.log(1 + A / tot[w])) for w, f in cnt.items()), key=lambda p: -p[1])

    topico = {}
    for c, cnt in conteos.items():
        terminos = [w for w, _ in ctfidf(cnt)[:TOP_TERMINOS]]
        topico[c] = ("ruido · " if c == -1 else "") + ", ".join(terminos[:4])
    util["nlp__topico"] = util["nlp__cluster"].map(topico)

    out = df[[COL_ID]].merge(util[[COL_ID, "nlp__cluster", "nlp__topico", "nlp__umap_x", "nlp__umap_y",
                                   "prob_cluster"]], on=COL_ID, how="left")
    out["nlp__cluster"] = out["nlp__cluster"].fillna(-2).astype(int)
    ficha = {"modelo_embeddings": MODELO_EMBEDDINGS, "dispositivo": disp, "reductor": reductor,
             "agrupador": agrupador, "semilla": SEMILLA_NLP, "umap_vecinos": UMAP_VECINOS,
             "umap_dim_cluster": UMAP_DIM_CLUSTER, "umap_min_dist": UMAP_MIN_DIST,
             "hdbscan_min_cluster": HDBSCAN_MIN_CLUSTER, "hdbscan_min_samples": HDBSCAN_MIN_SAMPLES,
             "spacy": MODELO_SPACY + " " + str(spacy.__version__)}
    return out, ficha


# ==========================================================================
# 3. tabla de frecuencias
# ==========================================================================
def nombre_tema(cluster, topico):
    c = int(cluster)
    if c == -2:
        return "sin texto útil"
    if c == -1:
        return "ruido"
    top = "" if pd.isna(topico) else str(topico)
    return "C{} · {}".format(c, top) if top else "C{}".format(c)


def unir(df, enr):
    d = df.merge(enr, on=COL_ID, how="left")
    d["cluster"] = d["nlp__cluster"].fillna(-2).astype(int)
    d["tema"] = [nombre_tema(c, t) for c, t in zip(d["cluster"], d["nlp__topico"])]
    n_clusters = int(d.loc[d.cluster >= 0, "cluster"].nunique())
    n_color = min(len(PAL), n_clusters)
    d["categoria_figura"] = np.select(
        [d.cluster == -2, d.cluster == -1, d.cluster < n_color],
        ["sin texto útil", "ruido", "color propio"], "otros clusters")
    return d, n_color


def tabla_frecuencias(d, n_color):
    n_total, n_cal = len(d), int(d.calificado.sum())
    filas = []
    for c, g in d.groupby("cluster", sort=True):
        fila = {
            "cluster": c, "tema": g["tema"].iloc[0],
            "en_la_figura": g["categoria_figura"].iloc[0],
            "color": (PAL[c] if 0 <= c < n_color else COLOR_RUIDO if c == -1
                      else COLOR_SIN_TEXTO if c == -2 else COLOR_OTROS),
            "n": len(g), "pct_corpus": len(g) / n_total,
            "calificados": int(g.calificado.sum()),
            "pct_calificados_del_cluster": g.calificado.mean(),
            "pct_de_los_calificados": g.calificado.sum() / n_cal if n_cal else 0.0,
        }
        if "nlp__menciona_mexico" in g:
            mx = g["nlp__menciona_mexico"].fillna(False).astype(bool)
            fila["menciona_mexico"] = int(mx.sum())
            fila["pct_menciona_mexico"] = float(mx.mean())
        if COL_LANG in g:
            fila["idiomas"] = " · ".join("{} {}".format(k, v) for k, v in g[COL_LANG].value_counts().head(3).items())
        if COL_BASE in g:
            fila["consulta_principal"] = str(g[COL_BASE].value_counts().index[0])
        filas.append(fila)
    tabla = pd.DataFrame(filas)
    # orden de lectura: clusters por tamano (C0...), luego ruido, luego sin texto
    orden = list(range(0, int(tabla.cluster.max()) + 1)) + [-1, -2]
    tabla["_o"] = tabla["cluster"].map({c: i for i, c in enumerate(orden)})
    return tabla.sort_values("_o").drop(columns="_o").reset_index(drop=True)


def tabla_categorias(d):
    """Las categorias que usa la leyenda del mapa y la dona."""
    orden = ["color propio", "otros clusters", "ruido", "sin texto útil"]
    n_total, n_cal = len(d), int(d.calificado.sum())
    filas = []
    for k in orden:
        g = d[d.categoria_figura == k]
        filas.append({"categoria": k, "clusters": int(g.loc[g.cluster >= 0, "cluster"].nunique()),
                      "n": len(g), "pct_corpus": len(g) / n_total,
                      "calificados": int(g.calificado.sum()),
                      "pct_de_los_calificados": g.calificado.sum() / n_cal if n_cal else 0.0})
    return pd.DataFrame(filas)


def tabla_indicador_tema(d):
    """Indicador x tema, para TODOS los temas (clusters, ruido y sin texto):
    cuantos tuits del tema hablan de cada indicador (nivel > 0) y cuantos no
    hablan de ninguno. Un tuit que habla de varios indicadores cuenta en cada
    uno, por eso 'menciones' puede superar 'tuits_calificados'. Ordenado por
    menciones, de mayor a menor; los temas sin calificados al final."""
    filas = []
    for c, g in d.groupby("cluster", sort=True):
        fila = {"cluster": c, "tema": g["tema"].iloc[0]}
        for i in INDICADORES:
            fila[i["etiqueta"]] = int(g["habla_" + i["corto"]].sum())
        fila[NINGUNO] = int((~g.calificado).sum())
        fila["menciones"] = sum(fila[i["etiqueta"]] for i in INDICADORES)
        fila["tuits_calificados"] = int(g.calificado.sum())
        fila["tuits"] = len(g)
        filas.append(fila)
    it = pd.DataFrame(filas)
    it["_ruido"] = (it.cluster < 0).astype(int)
    it = it.sort_values(["menciones", "_ruido", "cluster"], ascending=[False, True, True])
    return it.drop(columns="_ruido").reset_index(drop=True)


def tabla_indicador_unico(d, it):
    """Como tabla_indicador_tema, pero cada tuit calificado cuenta UNA sola vez:
    en la columna de su indicador si habla de exactamente uno, o en VARIOS si
    habla de dos o mas. Las cuatro columnas de indicador mas VARIOS suman los
    tuits calificados. Mismo orden de filas (y misma columna 'menciones') que
    `it`, para que la asignacion de colores sea la misma en las dos graficas."""
    habla = d[["habla_" + i["corto"] for i in INDICADORES]]
    n_ind = habla.sum(axis=1)
    filas = []
    for c, g in d.groupby("cluster", sort=True):
        fila = {"cluster": c}
        for i in INDICADORES:
            fila[i["etiqueta"]] = int((g["habla_" + i["corto"]] & (n_ind.loc[g.index] == 1)).sum())
        fila[VARIOS] = int((n_ind.loc[g.index] >= 2).sum())
        fila["un_solo_indicador"] = sum(fila[i["etiqueta"]] for i in INDICADORES)
        filas.append(fila)
    iu = it[["cluster", "tema", "menciones", "tuits_calificados", "tuits"]].merge(
        pd.DataFrame(filas), on="cluster", how="left")
    return iu


def cruces_por_serie(d, series):
    """Para cada serie (tema con color, otros temas, ruido...) una matriz 4x4:
    celda (i, j) = tuits de la serie que hablan del indicador i Y del j
    (nivel > 0 en ambos). UNIVERSO: solo los tuits calificados en DOS O MAS
    indicadores, que son los que de verdad cruzan; la diagonal es 'de esos,
    cuantos hablan de i'. Devuelve (matrices por serie, matriz total), en el
    orden de INDICADORES."""
    H = d[["habla_" + i["corto"] for i in INDICADORES]].to_numpy(dtype=int)
    varios = H.sum(axis=1) >= 2
    d, H = d[varios], H[varios]
    total = H.T @ H
    por_serie = {}
    for srs in series:
        m = d["cluster"].isin(srs["clusters"]).to_numpy()
        por_serie[srs["nombre"]] = H[m].T @ H[m]
    return por_serie, total


def tabla_cruces(por_serie, total):
    """Formato largo: una fila por (serie, indicador_x, indicador_y) con n,
    total del cruce y proporcion. Solo el triangulo superior (la matriz es
    simetrica), diagonal incluida."""
    etq = [i["etiqueta"] for i in INDICADORES]
    filas = []
    for nombre, M in por_serie.items():
        for i in range(len(etq)):
            for j in range(i, len(etq)):
                t = int(total[i, j])
                filas.append({"serie": nombre, "indicador_x": etq[i], "indicador_y": etq[j],
                              "n": int(M[i, j]), "total_cruce": t, "pct": (M[i, j] / t) if t else float("nan")})
    return pd.DataFrame(filas)


def tabla_indicador_idioma(d):
    """Indicador x idioma: cuantos tuits de cada idioma (`lang`) hablan de cada
    indicador (nivel > 0), cuantos no hablan de ninguno y el total. Un tuit que
    habla de varios indicadores cuenta en cada uno. Ordenado por tuits."""
    filas = []
    for lang, g in d.groupby(d[COL_LANG].fillna("und").astype(str), sort=False):
        fila = {"lang": lang}
        for i in INDICADORES:
            fila[i["etiqueta"]] = int(g["habla_" + i["corto"]].sum())
        fila[NINGUNO] = int((~g.calificado).sum())
        fila["menciones"] = sum(fila[i["etiqueta"]] for i in INDICADORES)
        fila["tuits_calificados"] = int(g.calificado.sum())
        fila["tuits"] = len(g)
        filas.append(fila)
    return pd.DataFrame(filas).sort_values(["tuits", "lang"], ascending=[False, True]).reset_index(drop=True)


def tabla_indicador_unico_idioma(d):
    """Como tabla_indicador_idioma, pero cada tuit calificado cuenta UNA sola
    vez: en la columna de su indicador si habla de exactamente uno, o en
    VARIOS si habla de dos o mas. Ordenado por tuits del idioma."""
    habla = d[["habla_" + i["corto"] for i in INDICADORES]]
    n_ind = habla.sum(axis=1)
    filas = []
    for lang, g in d.groupby(d[COL_LANG].fillna("und").astype(str), sort=False):
        fila = {"lang": lang}
        for i in INDICADORES:
            fila[i["etiqueta"]] = int((g["habla_" + i["corto"]] & (n_ind.loc[g.index] == 1)).sum())
        fila[VARIOS] = int((n_ind.loc[g.index] >= 2).sum())
        fila["un_solo_indicador"] = sum(fila[i["etiqueta"]] for i in INDICADORES)
        fila["tuits_calificados"] = int(g.calificado.sum())
        fila["tuits"] = len(g)
        filas.append(fila)
    return pd.DataFrame(filas).sort_values(["tuits", "lang"], ascending=[False, True]).reset_index(drop=True)


def series_idioma(ii, columnas=None):
    """Series para las barras por idioma: los de IDIOMAS con color propio y el
    resto plegado en 'otros idiomas'. Mismo formato que series_barras."""
    columnas = columnas or [i["etiqueta"] for i in INDICADORES] + [NINGUNO]
    series = []
    usados = []
    for codigo, nombre, color in IDIOMAS:
        sub = ii[ii.lang == codigo]
        if len(sub):
            usados.append(codigo)
            series.append({"nombre": "{} · {}".format(codigo, nombre), "color": color, "trama": None,
                           "clusters": [codigo], "valores": {k: int(sub[k].sum()) for k in columnas}})
    resto = ii[~ii.lang.isin(usados)]
    if len(resto):
        series.append({"nombre": "otros idiomas ({} códigos)".format(len(resto)), "color": COLOR_OTROS_IDIOMAS,
                       "trama": None, "clusters": resto.lang.tolist(),
                       "valores": {k: int(resto[k].sum()) for k in columnas}})
    return series


def series_barras(it, n_color, columnas=None):
    """Decide que temas llevan color propio en las barras y cuales se pliegan.
    Devuelve una lista de series (de abajo hacia arriba en la pila):
    {"nombre", "color", "trama", "clusters", "valores": {columna: n}}, con una
    entrada por columna (por defecto los indicadores y NINGUNO)."""
    columnas = columnas or [i["etiqueta"] for i in INDICADORES] + [NINGUNO]
    propios = it[(it.cluster >= 0) & (it.menciones >= MIN_MENCIONES_COLOR)].head(MAX_TEMAS_COLOR)
    plegados = it[(it.cluster >= 0) & ~it.index.isin(propios.index)]
    ruido = it[it.cluster == -1]
    sin_texto = it[it.cluster == -2]

    def valores(sub):
        return {k: int(sub[k].sum()) for k in columnas}

    series = []
    extra = iter(PAL_EXTRA)
    for idx, r in propios.iterrows():
        color = PAL[int(r.cluster)] if r.cluster < n_color else next(extra, COLOR_OTROS_TEMAS)
        series.append({"nombre": r.tema, "color": color, "trama": None, "clusters": [int(r.cluster)],
                       "valores": valores(propios.loc[[idx]])})
    if len(plegados):
        series.append({"nombre": "otros temas ({} clusters con menos de {} menciones)".format(
                           len(plegados), MIN_MENCIONES_COLOR),
                       "color": COLOR_OTROS_TEMAS, "trama": None, "clusters": plegados.cluster.tolist(),
                       "valores": valores(plegados)})
    if len(ruido):
        series.append({"nombre": "ruido (sin cluster)", "color": COLOR_RUIDO_BARRA, "trama": "////",
                       "clusters": [-1], "valores": valores(ruido)})
    if len(sin_texto):
        series.append({"nombre": "sin texto útil (fuera del agrupamiento)", "color": COLOR_SIN_TEXTO,
                       "trama": "....", "clusters": [-2], "valores": valores(sin_texto)})
    return series


# ==========================================================================
# 4. figuras
# ==========================================================================
def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans", "sans-serif"],
                         "figure.facecolor": COLOR_FONDO, "axes.facecolor": COLOR_FONDO,
                         "savefig.facecolor": COLOR_FONDO, "text.color": COLOR_TINTA})
    return plt


def color_de(cluster, n_color):
    c = int(cluster)
    if c == -1:
        return COLOR_RUIDO
    if 0 <= c < n_color:
        return PAL[c]
    return COLOR_OTROS


def figura_mapa(d, n_color, ruta):
    """El mapa del notebook: cada punto un tuit, color = cluster, rombo con
    borde negro = calificado. La leyenda va en el orden en que cada serie
    aparece por primera vez en el archivo (el mismo que produce ECharts)."""
    from matplotlib.lines import Line2D
    plt = _mpl()

    pts = d[d.cluster >= -1].copy()          # sin texto util no tiene coordenadas
    topico = dict(zip(pts.cluster, pts.tema))

    def clave(c):
        return "ruido" if c == -1 else ("C{}".format(c) if c < n_color else "otros clusters")

    pts["clave"] = pts["cluster"].map(clave)
    orden_series = list(dict.fromkeys(pts["clave"]))     # primera aparicion, como Object.entries

    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=200)
    fig.subplots_adjust(left=0.01, right=0.72, top=0.99, bottom=0.01)
    handles = []
    for k in orden_series:
        s = pts[(pts.clave == k) & ~pts.calificado]
        if k == "ruido":
            col, alfa, etiqueta = COLOR_RUIDO, 0.45, "ruido"
        elif k == "otros clusters":
            col, alfa, etiqueta = COLOR_OTROS, 0.75, "otros clusters"
        else:
            c = int(k[1:])
            col, alfa, etiqueta = PAL[c], 0.75, topico[c]
        ax.scatter(s.nlp__umap_x, s.nlp__umap_y, s=14, c=col, alpha=alfa, linewidths=0, zorder=2)
        handles.append(Line2D([], [], marker="o", linestyle="", markersize=13, markerfacecolor=col,
                              markeredgewidth=0, alpha=0.9, label=etiqueta))
    cal = pts[pts.calificado]
    ax.scatter(cal.nlp__umap_x, cal.nlp__umap_y, s=60, marker="D",
               c=[color_de(c, n_color) for c in cal.cluster], alpha=0.95,
               edgecolors="#0b0b0b", linewidths=0.9, zorder=3)
    handles.append(Line2D([], [], marker="D", linestyle="", markersize=11, markerfacecolor=PAL[0],
                          markeredgecolor="#0b0b0b", markeredgewidth=1.2, label="calificados (rúbrica)"))

    ax.set_axis_off()
    ax.margins(0.04)
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False,
              fontsize=11, labelspacing=1.55, handletextpad=0.9, labelcolor=COLOR_TINTA2, borderaxespad=0)
    fig.savefig(ruta)
    plt.close(fig)


def _dona(ax, valores, etiquetas, colores, titulo, centro):
    total = sum(valores)
    wedges, _ = ax.pie(valores, colors=colores, startangle=90, counterclock=False,
                       wedgeprops={"width": 0.38, "edgecolor": COLOR_FONDO, "linewidth": 1.2})
    # etiquetas fuera con linea; solo las porciones visibles (>= 1.5 %).
    # Se colocan en dos columnas (izquierda y derecha) y se separan en
    # vertical para que las porciones chicas consecutivas no se encimen.
    etiq = []
    for w, et, v in zip(wedges, etiquetas, valores):
        if v / total < 0.015:
            continue
        ang = np.deg2rad((w.theta1 + w.theta2) / 2)
        x, y = np.cos(ang), np.sin(ang)
        etiq.append({"x": x, "y": y, "yt": 1.2 * y, "lado": 1 if x >= 0 else -1,
                     "texto": "{}  {} ({:.1%})".format(et, v, v / total)})
    paso = 0.11
    for lado in (1, -1):
        col = sorted((e for e in etiq if e["lado"] == lado), key=lambda e: -e["yt"])
        for i in range(1, len(col)):                       # de arriba hacia abajo
            if col[i - 1]["yt"] - col[i]["yt"] < paso:
                col[i]["yt"] = col[i - 1]["yt"] - paso
        if col and col[-1]["yt"] < -1.3:                   # si se salio por abajo, recorrer
            desp = -1.3 - col[-1]["yt"]
            for e in col:
                e["yt"] += desp
    for e in etiq:
        ax.annotate(e["texto"], xy=(0.82 * e["x"], 0.82 * e["y"]), xytext=(1.3 * e["lado"], e["yt"]),
                    ha="left" if e["lado"] > 0 else "right", va="center", fontsize=8.5, color=COLOR_TINTA2,
                    arrowprops={"arrowstyle": "-", "color": "#9a9a92", "lw": 0.7,
                                "shrinkA": 0, "shrinkB": 2})
    ax.text(0, 0.06, centro[0], ha="center", va="center", fontsize=18, fontweight="bold", color=COLOR_TINTA)
    ax.text(0, -0.12, centro[1], ha="center", va="center", fontsize=9.5, color=COLOR_TINTA2)
    ax.set_title(titulo, fontsize=12, color=COLOR_TINTA, pad=14)
    ax.set_aspect("equal")
    ax.set_xlim(-2.45, 2.45)    # espacio para las etiquetas a ambos lados
    ax.set_ylim(-1.4, 1.4)


def figura_dona(tabla, n_color, ruta):
    """Dos donas con las mismas categorias del mapa: el corpus completo y los
    tuits calificados, repartidos por cluster."""
    plt = _mpl()
    t = tabla.copy()
    fig, axes = plt.subplots(1, 2, figsize=(17, 7.2), dpi=200)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.84, bottom=0.03, wspace=0.12)

    # --- dona 1: todo el corpus. Colores propios + otros + ruido + sin texto --
    propios = t[t.en_la_figura == "color propio"]
    otros = t[t.en_la_figura == "otros clusters"]
    ruido = t[t.cluster == -1]
    sin_texto = t[t.cluster == -2]
    valores = list(propios.n) + [int(otros.n.sum()), int(ruido.n.sum()), int(sin_texto.n.sum())]
    etiquetas = ["C{}".format(c) for c in propios.cluster] + [
        "otros (C{}–C{})".format(int(otros.cluster.min()), int(otros.cluster.max())) if len(otros) else "otros",
        "ruido", "sin texto útil"]
    colores = list(propios.color) + [COLOR_OTROS, COLOR_RUIDO, COLOR_SIN_TEXTO]
    _dona(axes[0], valores, etiquetas, colores, "Corpus completo · tuits por cluster",
          ("{:,}".format(int(t.n.sum())), "tuits"))

    # --- dona 2: solo calificados ----------------------------------------------
    cal = t[t.calificados > 0].sort_values("calificados", ascending=False)
    valores2 = [int(v) for v in cal.calificados]
    etiquetas2 = [("C{}".format(c) if c >= 0 else ("ruido" if c == -1 else "sin texto")) for c in cal.cluster]
    colores2 = list(cal.color)
    _dona(axes[1], valores2, etiquetas2, colores2, "Calificados (rúbrica) · por cluster",
          ("{:,}".format(int(cal.calificados.sum())), "calificados"))

    fig.text(0.5, 0.95, "Frecuencias por cluster del mapa UMAP", ha="center", fontsize=15,
             fontweight="bold", color=COLOR_TINTA)
    fig.text(0.5, 0.905, "Los {} clusters más grandes conservan el color del mapa; el resto se agrupa en «otros clusters». "
             "Las porciones menores al 1.5 % no llevan etiqueta.".format(n_color),
             ha="center", fontsize=9.5, color=COLOR_TINTA2)
    fig.savefig(ruta)
    plt.close(fig)


def _barras_apiladas(series, ruta, columnas, columna_aparte, titulo, subtitulo,
                     ylabel, etiqueta_total, ylabel_aparte=None,
                     titulo_leyenda="Tema (cluster del mapa UMAP)", nota=None):
    """Barras apiladas por tema. `columnas` van en el panel principal; si
    `columna_aparte` no es None, esa columna se dibuja en un segundo panel con
    escala propia (para una barra mucho mayor que las demas). Clave de color a
    la derecha, en el mismo orden vertical que la pila."""
    from matplotlib.patches import Patch
    plt = _mpl()

    if columna_aparte:
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(17, 8), dpi=200, gridspec_kw={"width_ratios": [4, 1.15]})
        fig.subplots_adjust(left=0.05, right=0.66, top=0.85, bottom=0.1, wspace=0.28)
        ax_leyenda, ancla = ax2, 1.08
    else:
        fig, ax = plt.subplots(figsize=(15, 8), dpi=200)
        fig.subplots_adjust(left=0.06, right=0.64, top=0.85, bottom=0.1)
        ax_leyenda, ancla = ax, 1.02

    def apilar(eje, cols, ancho, etq_total, pct=False):
        x = np.arange(len(cols))
        base = np.zeros(len(cols))
        totales = [sum(ss["valores"][c] for ss in series) for c in cols]
        for s in series:
            vals = np.array([s["valores"][c] for c in cols], dtype=float)
            eje.bar(x, vals, ancho, bottom=base, color=s["color"], hatch=s["trama"],
                    edgecolor=COLOR_FONDO, linewidth=1.5, zorder=2)     # 1.5 pt = separador entre segmentos
            for k, (v, b) in enumerate(zip(vals, base)):
                if v <= 0 or v / totales[k] < 0.025:                     # segmentos muy finos: sin cifra
                    continue
                claro = s["color"] in (COLOR_OTROS_TEMAS, COLOR_SIN_TEXTO)
                txt = "{:d} ({:.0%})".format(int(v), v / totales[k]) if pct else "{:d}".format(int(v))
                eje.text(x[k], b + v / 2, txt, ha="center", va="center", fontsize=9, fontweight="bold",
                         color=COLOR_TINTA if claro else "#ffffff", zorder=3,
                         bbox={"boxstyle": "round,pad=0.18", "fc": s["color"], "ec": "none"} if s["trama"] else None)
            base += vals
        for xi, tot in zip(x, base):
            eje.text(xi, tot + base.max() * 0.015, etq_total.format(int(tot)), ha="center", va="bottom",
                     fontsize=10, color=COLOR_TINTA, fontweight="bold")
        eje.set_xticks(x, cols, fontsize=11, color=COLOR_TINTA)
        eje.set_ylim(0, base.max() * 1.1)
        eje.yaxis.grid(True, color="#e4e2da", linewidth=0.8, zorder=0)
        eje.set_axisbelow(True)
        for lado in ("top", "right", "left"):
            eje.spines[lado].set_visible(False)
        eje.spines["bottom"].set_color("#c9c7bd")
        eje.tick_params(axis="y", colors=COLOR_TINTA2, labelsize=9, length=0)
        eje.tick_params(axis="x", length=0)

    apilar(ax, columnas, 0.58, etiqueta_total)
    ax.set_ylabel(ylabel, fontsize=10, color=COLOR_TINTA2)
    if columna_aparte:
        apilar(ax2, [columna_aparte], 0.58, "{:,d} tuits", pct=True)
        ax2.set_ylabel(ylabel_aparte or "", fontsize=10, color=COLOR_TINTA2)

    handles = [Patch(facecolor=s["color"], hatch=s["trama"], edgecolor=COLOR_FONDO, label=s["nombre"])
               for s in series]
    leyenda = ax_leyenda.legend(handles=handles[::-1], loc="upper left", bbox_to_anchor=(ancla, 1.0), frameon=False,
                                fontsize=10, labelspacing=1.1, handlelength=1.6, handleheight=1.3, borderaxespad=0,
                                labelcolor=COLOR_TINTA2, title=titulo_leyenda, title_fontsize=10,
                                alignment="left")
    leyenda.get_title().set_color(COLOR_TINTA)
    if nota:
        fig.text(0.695 if columna_aparte else 0.665, 0.40, nota, fontsize=8.5, color=COLOR_TINTA2,
                 va="top", wrap=True)

    fig.text(0.05, 0.95, titulo, fontsize=15, fontweight="bold", color=COLOR_TINTA)
    fig.text(0.05, 0.915, subtitulo, fontsize=9.5, color=COLOR_TINTA2)
    fig.savefig(ruta)
    plt.close(fig)


def figura_barras(it, n_color, ruta):
    """Grafica 1: los cuatro indicadores (un tuit cuenta en cada indicador del
    que habla) mas, en panel aparte, los tuits que no reflejan ninguno."""
    n_cal, n_tot = int(it.tuits_calificados.sum()), int(it.tuits.sum())
    series = series_barras(it, n_color, [i["etiqueta"] for i in INDICADORES] + [NINGUNO])
    _barras_apiladas(
        series, ruta, [i["etiqueta"] for i in INDICADORES], NINGUNO,
        "Temas de los que se habla, por indicador de la rúbrica",
        "{} tuits calificados (nivel > 0 en algún indicador) y {:,} sin ningún indicador, de {:,}. Un tuit que "
        "habla de varios indicadores cuenta en cada barra; los temas son los clusters del mapa UMAP."
        .format(n_cal, n_tot - n_cal, n_tot),
        "tuits que hablan del indicador (nivel > 0)", "{:d} menciones",
        ylabel_aparte="tuits sin ningún indicador · escala propia", nota=_nota_otros_temas(series))


def figura_barras_unico(iu, n_color, ruta):
    """Grafica 2: solo tuits calificados en UN SOLO indicador (cada tuit cuenta
    una vez), mas una quinta barra con los que hablan de varios. Las cinco
    barras suman los tuits calificados."""
    n_cal = int(iu.tuits_calificados.sum())
    n_uno = int(iu.un_solo_indicador.sum())
    series = series_barras(iu, n_color, [i["etiqueta"] for i in INDICADORES] + [VARIOS])
    _barras_apiladas(
        series, ruta, [i["etiqueta"] for i in INDICADORES] + [VARIOS], None,
        "Temas de los tuits calificados en un solo indicador",
        "{} de los {} tuits calificados hablan de exactamente un indicador; los otros {} hablan de dos o más "
        "(barra «{}»). Cada tuit cuenta una sola vez; los temas son los clusters del mapa UMAP."
        .format(n_uno, n_cal, n_cal - n_uno, VARIOS),
        "tuits calificados (cada uno cuenta una vez)", "{:d} tuits", nota=_nota_otros_temas(series))


def _nota_otros_temas(series):
    plegados = next((s for s in series if s["nombre"].startswith("otros temas")), None)
    if not plegados:
        return None
    return "otros temas: " + ", ".join("C{}".format(c) for c in sorted(plegados["clusters"]))


def figura_barras_idioma(ii, ruta):
    """Grafica 4: los cuatro indicadores (un tuit cuenta en cada indicador del
    que habla) mas, en panel aparte, los tuits sin ningun indicador, apilados
    por IDIOMA del tuit original."""
    series = series_idioma(ii)
    n_cal, n_tot = int(ii.tuits_calificados.sum()), int(ii.tuits.sum())
    otros = next((s for s in series if s["nombre"].startswith("otros idiomas")), None)
    nota = None
    if otros:
        nota = "otros idiomas: " + ", ".join(
            "{} ({})".format(c, NOMBRE_LANG.get(c, "?")) for c in otros["clusters"])
    _barras_apiladas(
        series, ruta, [i["etiqueta"] for i in INDICADORES], NINGUNO,
        "Idiomas de los tuits, por indicador de la rúbrica",
        "{} tuits calificados (nivel > 0 en algún indicador) y {:,} sin ningún indicador, de {:,}. Un tuit que "
        "habla de varios indicadores cuenta en cada barra; el idioma es el código `lang` del tuit original."
        .format(n_cal, n_tot - n_cal, n_tot),
        "tuits que hablan del indicador (nivel > 0)", "{:d} menciones",
        ylabel_aparte="tuits sin ningún indicador · escala propia",
        titulo_leyenda="Idioma del tuit original", nota=nota)


def _nota_otros_idiomas(series):
    otros = next((s for s in series if s["nombre"].startswith("otros idiomas")), None)
    if not otros:
        return None
    return "otros idiomas: " + ", ".join("{} ({})".format(c, NOMBRE_LANG.get(c, "?")) for c in otros["clusters"])


def figura_barras_unico_idioma(iui, ruta):
    """Grafica 5: solo tuits calificados en UN SOLO indicador (cada tuit cuenta
    una vez) mas la barra de varios, apilados por IDIOMA del tuit original."""
    columnas = [i["etiqueta"] for i in INDICADORES] + [VARIOS]
    series = series_idioma(iui, columnas)
    n_cal = int(iui.tuits_calificados.sum())
    n_uno = int(iui.un_solo_indicador.sum())
    _barras_apiladas(
        series, ruta, columnas, None,
        "Idiomas de los tuits calificados en un solo indicador",
        "{} de los {} tuits calificados hablan de exactamente un indicador; los otros {} hablan de dos o más "
        "(barra «{}»). Cada tuit cuenta una sola vez; el idioma es el código `lang` del tuit original."
        .format(n_uno, n_cal, n_cal - n_uno, VARIOS),
        "tuits calificados (cada uno cuenta una vez)", "{:d} tuits",
        titulo_leyenda="Idioma del tuit original", nota=_nota_otros_idiomas(series))


def figura_heatmaps(d, it, n_color, ruta):
    """Un heatmap 4x4 por tema (indicadores en x y en y). Celda (i, j) = tuits
    del tema que hablan de i y de j; el color es la PREPONDERANCIA del tema en
    ese cruce: su proporcion sobre todos los tuits del corpus que hablan de i
    y j. Un panel de referencia (gris) trae el total del cruce. Cada tema usa
    una rampa secuencial de su propio color (claro -> color del mapa)."""
    from matplotlib.colors import LinearSegmentedColormap, to_rgb
    plt = _mpl()
    series = [srs for srs in series_barras(it, n_color) if srs["clusters"] != [-2]]
    por_serie, total = cruces_por_serie(d, series)
    series = [srs for srs in series if por_serie[srs["nombre"]].sum() > 0]
    etq = [i["etiqueta"] for i in INDICADORES]
    cortas = ["Atmósfera", "Persp. política", "Imagen cultural", "Sal. violencia"]
    n_pan = len(series) + 1
    ncol = 4
    nfil = int(np.ceil(n_pan / ncol))

    fig, axes = plt.subplots(nfil, ncol, figsize=(4.4 * ncol, 4.1 * nfil + 1.1), dpi=200)
    axes = np.atleast_2d(axes)
    fig.subplots_adjust(left=0.05, right=0.985, top=0.85, bottom=0.08, wspace=0.42, hspace=0.5)

    def pintar(ax, M, cmap, vmax, titulo, color_titulo, fmt):
        ax.imshow(M, cmap=cmap, vmin=0, vmax=vmax, aspect="equal")
        for i in range(4):
            for j in range(4):
                v = M[i, j]
                oscuro = (v / vmax if vmax else 0) > 0.55
                ax.text(j, i, fmt(i, j), ha="center", va="center", fontsize=8.3,
                        color="#ffffff" if oscuro else COLOR_TINTA, fontweight="bold" if i == j else "normal")
        ax.set_xticks(range(4), cortas, fontsize=8, rotation=35, ha="right", color=COLOR_TINTA2)
        ax.set_yticks(range(4), cortas, fontsize=8, color=COLOR_TINTA2)
        ax.tick_params(length=0)
        for lado in ax.spines.values():
            lado.set_visible(False)
        ax.set_xticks(np.arange(-0.5, 4, 1), minor=True)          # rejilla de 1.5 pt entre celdas
        ax.set_yticks(np.arange(-0.5, 4, 1), minor=True)
        ax.grid(which="minor", color=COLOR_FONDO, linewidth=1.5)
        ax.tick_params(which="minor", length=0)
        ax.set_title(titulo, fontsize=9.5, color=color_titulo, loc="left", pad=8, fontweight="bold")

    # panel de referencia: el corpus completo, en gris, con el total del cruce
    ax0 = axes.flat[0]
    gris = LinearSegmentedColormap.from_list("gris", ["#f3f2ee", "#5f5e56"])
    pintar(ax0, total, gris, total.max(), "Todos los temas · tuits que hablan de ambos", COLOR_TINTA,
           lambda i, j: "{:d}".format(int(total[i, j])))

    for k, srs in enumerate(series, start=1):
        ax = axes.flat[k]
        M = por_serie[srs["nombre"]]
        with np.errstate(divide="ignore", invalid="ignore"):
            P = np.where(total > 0, M / np.maximum(total, 1), 0.0)
        base = to_rgb(srs["color"])
        claro = tuple(0.93 + 0.07 * c for c in base)                # tinte muy claro del mismo color
        cmap = LinearSegmentedColormap.from_list("t" + str(k), [claro, base])
        nombre = srs["nombre"]
        if nombre.startswith("otros temas"):
            nombre = "otros temas ({} clusters)".format(len(srs["clusters"]))
        titulo = nombre if len(nombre) <= 44 else nombre[:42] + "…"

        def fmt(i, j, M=M, P=P):
            if total[i, j] == 0:
                return "—"
            return "{:d}\n({:.0%})".format(int(M[i, j]), P[i, j])
        color_tit = srs["color"] if srs["trama"] is None and srs["color"] != COLOR_OTROS_TEMAS else COLOR_TINTA
        pintar(ax, P, cmap, 1.0, titulo, color_tit, fmt)

    for ax in list(axes.flat)[n_pan:]:
        ax.set_visible(False)

    n_varios = int((d[["habla_" + i["corto"] for i in INDICADORES]].sum(axis=1) >= 2).sum())
    fig.text(0.05, 0.955, "Preponderancia de cada tema en los cruces de indicadores", fontsize=15,
             fontweight="bold", color=COLOR_TINTA)
    fig.text(0.05, 0.925, "Universo: los {} tuits calificados en dos o más indicadores. Celda (fila, columna) = tuits "
             "del tema que hablan de los dos indicadores (nivel > 0 en ambos); la diagonal es «hablan de ese "
             "indicador». Entre paréntesis y en color: la proporción que el tema representa sobre todos los tuits "
             "de ese cruce (primer panel). Las matrices son simétricas.".format(n_varios),
             fontsize=9, color=COLOR_TINTA2, wrap=True)
    fig.savefig(ruta)
    plt.close(fig)


# ==========================================================================
# 5. markdown
# ==========================================================================
def _md_tabla(cabecera, filas, alineacion=None):
    alineacion = alineacion or ["---"] + ["---:"] * (len(cabecera) - 1)
    out = ["| " + " | ".join(cabecera) + " |", "|" + "|".join(alineacion) + "|"]
    out += ["| " + " | ".join(str(x) for x in f) + " |" for f in filas]
    return "\n".join(out)


def _pct(x):
    return "{:.1f} %".format(100 * x)


def _solo_terminos(tema, cluster):
    if cluster < 0:
        return "—"
    return tema.split(" · ", 1)[1] if " · " in tema else tema


def render_md(tabla, cats, it, iu, ii, iui, d, n_color, origen, ficha=None):
    n_total, n_cal = len(d), int(d.calificado.sum())
    n_cl = int((tabla.cluster >= 0).sum())
    n_ruido = int(tabla.loc[tabla.cluster == -1, "n"].sum())
    n_sin = int(tabla.loc[tabla.cluster == -2, "n"].sum())
    n_en_cl = n_total - n_ruido - n_sin
    hay_mx = "menciona_mexico" in tabla
    cal_en = tabla[(tabla.calificados > 0) & (tabla.cluster >= 0)]
    sin_cal = tabla[(tabla.calificados == 0) & (tabla.cluster >= 0)]
    md = []
    md.append("# Frecuencias por cluster del mapa UMAP\n")
    md.append("Fuente del corpus y de la rúbrica: `{}` ({:,} tuits). Fuente de los clusters: `{}` "
              "(columnas `nlp__cluster`, `nlp__topico`, `nlp__umap_x`, `nlp__umap_y`{}). "
              "Generado por `clusters_umap.py`, que también dibuja `salida/mapa_umap_clusters.png` y "
              "`salida/dona_clusters.png` y guarda la tabla en `salida/frecuencias_clusters.csv`.\n".format(
                  RUTA_CALIFICADOS, n_total, origen,
                  "; recalculado en esta máquina con `--recalcular`" if ficha else
                  ", la misma asignación del mapa de la sección 16 del notebook"))
    md.append("Cómo se obtuvo el agrupamiento: embeddings multilingües del **texto original** limpio "
              "(`{}`), UMAP a {} dimensiones (`n_neighbors={}`, `min_dist={}`, métrica coseno) y HDBSCAN "
              "(`min_cluster_size={}`, `min_samples={}`). Los clusters se renumeran por tamaño (C0 es el "
              "más grande). El nombre de cada tema son sus cuatro lemas más distintivos (c-TF-IDF sobre la "
              "traducción al español). El mapa usa un segundo UMAP a 2 dimensiones (`min_dist=0.1`) solo "
              "para dibujar.\n".format(MODELO_EMBEDDINGS, UMAP_DIM_CLUSTER, UMAP_VECINOS, UMAP_MIN_DIST,
                                       HDBSCAN_MIN_CLUSTER, HDBSCAN_MIN_SAMPLES))
    md.append("Resultado: **{} clusters** con {:,} tuits ({}), **ruido** {:,} ({}) y **sin texto útil** {} ({}). "
              "Calificados (nivel > 0 en algún indicador): {} ({} del corpus).\n".format(
                  n_cl, n_en_cl, _pct(n_en_cl / n_total), n_ruido, _pct(n_ruido / n_total),
                  n_sin, _pct(n_sin / n_total), n_cal, _pct(n_cal / n_total)))

    # ---- 1. categorias de la figura ------------------------------------------
    md.append("## 1. Lo que muestra la figura\n")
    md.append("El mapa da color propio a los {} clusters más grandes (C0–C{}); del C{} en adelante los "
              "puntos van en gris claro («otros clusters») y el ruido en gris más tenue. Los tuits sin "
              "texto útil no entran al UMAP, así que no están en el mapa. La dona usa las mismas "
              "categorías.\n".format(n_color, n_color - 1, n_color))
    md.append(_md_tabla(["Categoría", "Clusters", "Tuits", "% del corpus", "Calificados", "% de los calificados"],
                        [[r.categoria, r.clusters, r.n, _pct(r.pct_corpus), r.calificados, _pct(r.pct_de_los_calificados)]
                         for r in cats.itertuples()]
                        + [["Total", n_cl, n_total, "100.0 %", n_cal, "100.0 %"]]))
    md.append("")

    # ---- 2. tabla por cluster ------------------------------------------------------
    md.append("## 2. Frecuencias por cluster\n")
    md.append("Una fila por cluster, en el orden de la numeración (por tamaño). «% calificados» es la "
              "proporción del cluster que habla de algún indicador; «% de los calificados» reparte los "
              "{} calificados entre clusters.{}\n".format(
                  n_cal, " «Mencionan México» viene del diccionario del notebook (`nlp__menciona_mexico`)." if hay_mx else ""))
    cab = ["Cluster", "Tema (4 términos c-TF-IDF)", "En la figura", "Tuits", "% corpus", "Calificados",
           "% calificados", "% de los calificados"]
    if hay_mx:
        cab += ["Mencionan México", "% México"]
    if "idiomas" in tabla:
        cab += ["Idiomas (top 3)"]
    filas = []
    for r in tabla.itertuples():
        etiqueta = ("ruido" if r.cluster == -1 else "sin texto útil" if r.cluster == -2 else "C{}".format(r.cluster))
        f = [etiqueta, _solo_terminos(r.tema, r.cluster), r.en_la_figura, r.n, _pct(r.pct_corpus), r.calificados,
             _pct(r.pct_calificados_del_cluster), _pct(r.pct_de_los_calificados)]
        if hay_mx:
            f += [int(r.menciona_mexico), _pct(r.pct_menciona_mexico)]
        if "idiomas" in tabla:
            f += [r.idiomas]
        filas.append(f)
    tot = ["Total", "", "", n_total, "100.0 %", n_cal, _pct(n_cal / n_total), "100.0 %"]
    if hay_mx:
        tot += [int(tabla.menciona_mexico.sum()), _pct(tabla.menciona_mexico.sum() / n_total)]
    if "idiomas" in tabla:
        tot += [""]
    md.append(_md_tabla(cab, filas + [tot], ["---", "---", "---"] + ["---:"] * (len(cab) - 3)))
    md.append("")

    # ---- 3. indicador x tema (la grafica de barras apiladas) ----------------------
    md.append("## 3. Temas por indicador (barras apiladas)\n")
    series = series_barras(it, n_color)
    etq = [i["etiqueta"] for i in INDICADORES]
    cols = etq + [NINGUNO]
    tot_col = {e: int(it[e].sum()) for e in cols}
    n_propios = sum(1 for s in series if len(s["clusters"]) == 1 and s["clusters"][0] >= 0)
    md.append("Es la tabla de `salida/barras_indicador_tema.png`: una barra por indicador, apilada por tema, "
              "más una quinta barra (en un panel con escala propia) con los tuits que no calificaron en ningún "
              "indicador. Cada celda es el número de tuits del tema que hablan de ese indicador (nivel > 0); "
              "un tuit que habla de varios cuenta en cada columna, por eso «Menciones» puede superar "
              "«Tuits calificados». «{}» son los tuits con nivel 0 o faltante en los cuatro. Los temas con al "
              "menos {} menciones llevan color propio en la gráfica ({} temas); el resto se pliega en "
              "«otros temas».\n".format(NINGUNO, MIN_MENCIONES_COLOR, n_propios))
    filas = []
    for _, r in it.iterrows():
        etiqueta = "ruido" if r.cluster == -1 else "sin texto útil" if r.cluster == -2 else "C{}".format(r.cluster)
        en_fig = next((("color propio" if len(s["clusters"]) == 1 and s["clusters"][0] >= 0 else
                        "ruido" if s["clusters"] == [-1] else "sin texto útil" if s["clusters"] == [-2]
                        else "otros temas") for s in series if r.cluster in s["clusters"]), "")
        filas.append([etiqueta, _solo_terminos(r.tema, r.cluster), en_fig]
                     + [int(r[e]) for e in cols]
                     + [int(r.menciones), int(r.tuits_calificados), int(r.tuits)])
    filas.append(["Total", "", ""] + [tot_col[e] for e in cols]
                 + [sum(tot_col[e] for e in etq), int(it.tuits_calificados.sum()), int(it.tuits.sum())])
    md.append(_md_tabla(["Tema", "Términos", "En la gráfica"] + cols + ["Menciones", "Tuits calificados", "Tuits del tema"],
                        filas, ["---", "---", "---"] + ["---:"] * (len(cols) + 3)))
    md.append("")
    md.append("Series de la gráfica (de abajo hacia arriba en cada barra), con su color:\n")
    md.append(_md_tabla(["Serie", "Color", "Clusters"] + cols,
                        [[s["nombre"], s["color"],
                          ", ".join("C{}".format(c) if c >= 0 else ("ruido" if c == -1 else "sin texto") for c in s["clusters"])]
                         + [s["valores"][e] for e in cols] for s in series]
                        + [["Total", "", ""] + [tot_col[e] for e in cols]],
                        ["---", "---", "---"] + ["---:"] * len(cols)))
    md.append("")

    # ---- 3b. un solo indicador ----------------------------------------------------
    md.append("## 3b. Tuits calificados en un solo indicador\n")
    cols_u = etq + [VARIOS]
    series_u = series_barras(iu, n_color, cols_u)
    n_uno = int(iu.un_solo_indicador.sum())
    md.append("Es la tabla de `salida/barras_indicador_unico_tema.png`. Aquí cada tuit calificado cuenta **una "
              "sola vez**: en la columna de su indicador si habla exactamente de uno ({} tuits), o en «{}» si "
              "habla de dos o más ({} tuits). Las cinco columnas suman los {} calificados. Solo se listan los "
              "temas con algún calificado; los colores son los mismos de la gráfica anterior.\n".format(
                  n_uno, VARIOS, n_cal - n_uno, n_cal))
    filas = []
    for _, r in iu[iu.tuits_calificados > 0].iterrows():
        etiqueta = "ruido" if r.cluster == -1 else "sin texto útil" if r.cluster == -2 else "C{}".format(r.cluster)
        filas.append([etiqueta, _solo_terminos(r.tema, r.cluster)] + [int(r[e]) for e in cols_u]
                     + [int(r.un_solo_indicador), int(r.tuits_calificados)])
    filas.append(["Total", ""] + [int(iu[e].sum()) for e in cols_u] + [n_uno, n_cal])
    md.append(_md_tabla(["Tema", "Términos"] + cols_u + ["Un solo indicador", "Tuits calificados"], filas,
                        ["---", "---"] + ["---:"] * (len(cols_u) + 2)))
    md.append("")
    md.append("Series de la gráfica (de abajo hacia arriba en cada barra):\n")
    md.append(_md_tabla(["Serie", "Color"] + cols_u + ["Total"],
                        [[s["nombre"], s["color"]] + [s["valores"][e] for e in cols_u] + [sum(s["valores"].values())]
                         for s in series_u if sum(s["valores"].values()) > 0]
                        + [["Total", ""] + [int(iu[e].sum()) for e in cols_u] + [n_cal]],
                        ["---", "---"] + ["---:"] * (len(cols_u) + 1)))
    md.append("")

    # ---- 3c. cruces de indicadores ---------------------------------------------------
    md.append("## 3c. Cruces de indicadores por tema (heatmaps)\n")
    series_h = [srs for srs in series_barras(it, n_color) if srs["clusters"] != [-2]]
    por_serie, total_h = cruces_por_serie(d, series_h)
    series_h = [srs for srs in series_h if por_serie[srs["nombre"]].sum() > 0]
    n_varios = int((d[["habla_" + i["corto"] for i in INDICADORES]].sum(axis=1) >= 2).sum())
    md.append("Es la tabla de `salida/heatmaps_cruces_tema.png`. Universo: **los {} tuits calificados en dos o "
              "más indicadores** (la barra «{}» de la gráfica 3b). Cada fila es un cruce de dos indicadores, o un "
              "indicador consigo mismo (cuántos de esos {} hablan de él). «Total» son los tuits que hablan de "
              "ambos; en cada tema, cuántos de esos tuits pertenecen al tema y, entre paréntesis, su proporción "
              "sobre el total del cruce, que es lo que colorea el heatmap. Los cruces sin tuits se marcan con "
              "«—».\n".format(n_varios, VARIOS, n_varios))
    nombres_cortos = []
    for srs in series_h:
        n_ = srs["nombre"]
        nombres_cortos.append(n_.split(" · ")[0] if n_.startswith("C") else
                              ("otros temas" if n_.startswith("otros") else "ruido"))
    filas = []
    for i in range(len(etq)):
        for j in range(i, len(etq)):
            t = int(total_h[i, j])
            cruce = "{} (todos)".format(etq[i]) if i == j else "{} ∩ {}".format(etq[i], etq[j])
            fila = [cruce, t]
            for srs in series_h:
                n_ = int(por_serie[srs["nombre"]][i, j])
                fila.append("—" if t == 0 else "{} ({:.0%})".format(n_, n_ / t))
            filas.append(fila)
    md.append(_md_tabla(["Cruce", "Total"] + nombres_cortos, filas, ["---", "---:"] + ["---:"] * len(series_h)))
    md.append("")
    md.append("Clave: " + "; ".join("**{}** = {}".format(c, srs["nombre"]) for c, srs in zip(nombres_cortos, series_h)) + ".")
    md.append("")

    # ---- 3d. idiomas por indicador -------------------------------------------------------
    md.append("## 3d. Idiomas por indicador (barras apiladas)\n")
    series_i = series_idioma(ii)
    cols_i = etq + [NINGUNO]
    md.append("Es la tabla de `salida/barras_indicador_idioma.png`: las mismas cinco barras de la sección 3, "
              "pero apiladas por el idioma del tuit original (código `lang` de Twitter). Un tuit que habla de "
              "varios indicadores cuenta en cada columna. Los idiomas con color propio son {}; el resto se "
              "pliega en «otros idiomas».\n".format(
                  ", ".join("{} ({})".format(c, n) for c, n, _ in IDIOMAS)))
    filas = []
    for _, r in ii.iterrows():
        filas.append([r.lang, NOMBRE_LANG.get(r.lang, dict((c, n) for c, n, _ in IDIOMAS).get(r.lang, ""))]
                     + [int(r[e]) for e in cols_i] + [int(r.menciones), int(r.tuits_calificados), int(r.tuits)])
    filas.append(["Total", ""] + [int(ii[e].sum()) for e in cols_i]
                 + [int(ii.menciones.sum()), int(ii.tuits_calificados.sum()), int(ii.tuits.sum())])
    md.append(_md_tabla(["lang", "Idioma"] + cols_i + ["Menciones", "Tuits calificados", "Tuits"], filas,
                        ["---", "---"] + ["---:"] * (len(cols_i) + 3)))
    md.append("")
    md.append("Series de la gráfica (de abajo hacia arriba en cada barra):\n")
    md.append(_md_tabla(["Serie", "Color"] + cols_i + ["Códigos"],
                        [[s_["nombre"], s_["color"]] + [s_["valores"][e] for e in cols_i] + [", ".join(s_["clusters"])]
                         for s_ in series_i],
                        ["---", "---"] + ["---:"] * len(cols_i) + ["---"]))
    md.append("")

    # ---- 3e. un solo indicador, por idioma --------------------------------------------
    md.append("## 3e. Tuits calificados en un solo indicador, por idioma\n")
    cols_ui = etq + [VARIOS]
    series_ui = series_idioma(iui, cols_ui)
    n_uno_i = int(iui.un_solo_indicador.sum())
    md.append("Es la tabla de `salida/barras_indicador_unico_idioma.png`: la misma lógica de la sección 3b (cada "
              "tuit calificado cuenta **una sola vez**, en su indicador si habla exactamente de uno o en «{}» si "
              "habla de dos o más), apilada por idioma. Solo se listan los idiomas con algún calificado.\n"
              .format(VARIOS))
    nombres = dict((c, n) for c, n, _ in IDIOMAS)
    filas = []
    for _, r in iui[iui.tuits_calificados > 0].iterrows():
        filas.append([r.lang, NOMBRE_LANG.get(r.lang, nombres.get(r.lang, ""))]
                     + [int(r[e]) for e in cols_ui] + [int(r.un_solo_indicador), int(r.tuits_calificados)])
    filas.append(["Total", ""] + [int(iui[e].sum()) for e in cols_ui] + [n_uno_i, int(iui.tuits_calificados.sum())])
    md.append(_md_tabla(["lang", "Idioma"] + cols_ui + ["Un solo indicador", "Tuits calificados"], filas,
                        ["---", "---"] + ["---:"] * (len(cols_ui) + 2)))
    md.append("")
    md.append("Series de la gráfica (de abajo hacia arriba en cada barra):\n")
    md.append(_md_tabla(["Serie", "Color"] + cols_ui + ["Total", "Códigos"],
                        [[s_["nombre"], s_["color"]] + [s_["valores"][e] for e in cols_ui]
                         + [sum(s_["valores"].values()), ", ".join(s_["clusters"])]
                         for s_ in series_ui if sum(s_["valores"].values()) > 0],
                        ["---", "---"] + ["---:"] * (len(cols_ui) + 1) + ["---"]))
    md.append("")

    # ---- 4. comentarios -------------------------------------------------------------
    md.append("## 4. Lectura\n")
    top = tabla[tabla.cluster >= 0].head(5)
    md.append("- **El ruido es la categoría más grande** ({:,} tuits, {}): HDBSCAN no encontró para esos "
              "tuits una región densa a la que asignarlos. Es lo esperable con textos cortos y en varios "
              "idiomas; no es un tema y por eso el mapa lo pinta en gris tenue.".format(n_ruido, _pct(n_ruido / n_total)))
    md.append("- **Los clusters son chicos y muchos.** El mayor, C0 ({}), tiene {} tuits ({}); los cinco mayores "
              "suman {} ({}). Ningún tema domina el corpus.".format(
                  _solo_terminos(top.iloc[0].tema, 0), int(top.iloc[0].n), _pct(top.iloc[0].pct_corpus),
                  int(top.n.sum()), _pct(top.n.sum() / n_total)))
    conc = cal_en.sort_values("calificados", ascending=False).head(3)
    ruido_cal = int(tabla.loc[tabla.cluster == -1, "calificados"].sum())
    md.append("- **Los calificados se concentran en pocos clusters.** {} están en el ruido ({} de los "
              "calificados) y el resto sobre todo en {}. Son los temas donde el mapa muestra los rombos "
              "apiñados.".format(
                  ruido_cal, _pct(ruido_cal / n_cal) if n_cal else "0 %",
                  "; ".join("{} ({} calificados, {} de su cluster)".format(
                      r.tema, int(r.calificados), _pct(r.pct_calificados_del_cluster)) for r in conc.itertuples())))
    if len(sin_cal):
        md.append("- **{} clusters no tienen ningún calificado**: {}. Son la parte del corpus que la rúbrica no "
                  "toca.".format(len(sin_cal), ", ".join(r.tema for r in sin_cal.itertuples())))
    if hay_mx:
        mx = tabla[(tabla.cluster >= 0) & (tabla.n >= 15)].sort_values("pct_menciona_mexico", ascending=False).head(3)
        md.append("- **Dónde se habla de México.** Los clusters con más mención del diccionario son {}. "
                  "Un cluster con mucha mención de México y pocos calificados es candidato a «tema fuera de la "
                  "rúbrica».".format("; ".join("{} ({})".format(r.tema, _pct(r.pct_menciona_mexico)) for r in mx.itertuples())))
    md.append("- **Los nombres de los temas son orientativos.** Salen de cuatro lemas de la traducción automática; "
              "un cluster con textos en japonés o inglés mal traducidos puede recibir un nombre poco legible. "
              "Conviene leer los ejemplos del notebook antes de citarlos.")
    md.append("- **La partición depende de los parámetros** (`HDBSCAN_MIN_CLUSTER`, `UMAP_VECINOS`) y UMAP no es "
              "reproducible bit a bit entre máquinas. Con `--recalcular` se obtiene una partición parecida, no "
              "idéntica; las cifras de este archivo corresponden a `{}`.".format(origen))
    if ficha:
        md.append("")
        md.append("## Ficha técnica del recálculo\n")
        md.append(_md_tabla(["Parámetro", "Valor"], [[k, v] for k, v in ficha.items()], ["---", "---"]))
    md.append("")
    return "\n".join(md)


# ==========================================================================
# main
# ==========================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calificados", default=RUTA_CALIFICADOS)
    ap.add_argument("--enriquecidos", default=None, help="CSV con nlp__cluster/nlp__topico/nlp__umap_x/nlp__umap_y")
    ap.add_argument("--recalcular", action="store_true", help="rehacer embeddings + UMAP + HDBSCAN + tópicos")
    ap.add_argument("--salida", default=SALIDA_DIR)
    ap.add_argument("--md", default=RUTA_MD)
    args = ap.parse_args()
    os.makedirs(args.salida, exist_ok=True)

    df = leer_calificados(args.calificados)
    ficha = None
    if args.recalcular:
        enr, ficha = recalcular(df)
        origen = os.path.join(args.salida, "resultados_clusters.csv")
        enr.to_csv(origen, index=False, encoding="utf-8-sig")
        print("guardado", origen)
    else:
        origen = buscar_enriquecidos(args.enriquecidos)
        enr = leer_enriquecidos(origen)
        print("clusters tomados de", origen)

    d, n_color = unir(df, enr)
    tabla = tabla_frecuencias(d, n_color)
    cats = tabla_categorias(d)
    it = tabla_indicador_tema(d)
    iu = tabla_indicador_unico(d, it)
    ii = tabla_indicador_idioma(d)
    iui = tabla_indicador_unico_idioma(d)

    ruta_csv = os.path.join(args.salida, "frecuencias_clusters.csv")
    tabla.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
    it.to_csv(os.path.join(args.salida, "frecuencias_indicador_tema.csv"), index=False, encoding="utf-8-sig")
    iu.to_csv(os.path.join(args.salida, "frecuencias_indicador_unico_tema.csv"), index=False, encoding="utf-8-sig")
    ii.to_csv(os.path.join(args.salida, "frecuencias_indicador_idioma.csv"), index=False, encoding="utf-8-sig")
    iui.to_csv(os.path.join(args.salida, "frecuencias_indicador_unico_idioma.csv"), index=False, encoding="utf-8-sig")
    figura_mapa(d, n_color, os.path.join(args.salida, "mapa_umap_clusters.png"))
    figura_dona(tabla, n_color, os.path.join(args.salida, "dona_clusters.png"))
    figura_barras(it, n_color, os.path.join(args.salida, "barras_indicador_tema.png"))
    figura_barras_unico(iu, n_color, os.path.join(args.salida, "barras_indicador_unico_tema.png"))
    figura_barras_idioma(ii, os.path.join(args.salida, "barras_indicador_idioma.png"))
    figura_barras_unico_idioma(iui, os.path.join(args.salida, "barras_indicador_unico_idioma.png"))
    figura_heatmaps(d, it, n_color, os.path.join(args.salida, "heatmaps_cruces_tema.png"))
    _series_h = [srs for srs in series_barras(it, n_color) if srs["clusters"] != [-2]]
    _ps, _tot = cruces_por_serie(d, _series_h)
    tabla_cruces(_ps, _tot).to_csv(os.path.join(args.salida, "frecuencias_cruces_tema.csv"),
                                   index=False, encoding="utf-8-sig")
    with open(args.md, "w", encoding="utf-8") as f:
        f.write(render_md(tabla, cats, it, iu, ii, iui, d, n_color, origen, ficha))

    print("{} clusters · {} tuits · {} calificados · ruido {}".format(
        int((tabla.cluster >= 0).sum()), len(d), int(d.calificado.sum()),
        int(tabla.loc[tabla.cluster == -1, "n"].sum())))
    print(tabla[["cluster", "tema", "n", "calificados"]].head(18).to_string(index=False))
    print("escrito:", ruta_csv, "·", os.path.join(args.salida, "frecuencias_indicador_tema.csv"), "·",
          os.path.join(args.salida, "mapa_umap_clusters.png"), "·", os.path.join(args.salida, "dona_clusters.png"),
          "·", os.path.join(args.salida, "barras_indicador_tema.png"), "·",
          os.path.join(args.salida, "barras_indicador_unico_tema.png"), "·",
          os.path.join(args.salida, "heatmaps_cruces_tema.png"), "·",
          os.path.join(args.salida, "barras_indicador_idioma.png"), "·",
          os.path.join(args.salida, "barras_indicador_unico_idioma.png"), "·", args.md)


if __name__ == "__main__":
    main()
