# -*- coding: utf-8 -*-
"""Frecuencias de lemas y de entidades del corpus, fuera de Colab.

NO reimplementa nada. Ejecuta los bloques del propio notebook -- la regla de
codificacion de la rubrica, la polaridad, `limpiar()`, el diccionario MEXICO,
`POS_LEMAS` y el pipeline de spaCy -- y sobre eso cuenta. Si el notebook
cambia, este script cambia con el; no hay una segunda copia que mantener.

Salta los bloques que necesitan GPU (embeddings, UMAP, HDBSCAN) y los topicos
por cluster, que dependen de ellos. Los lemas y las entidades son CPU pura.

    python frecuencias_corpus.py
    python frecuencias_corpus.py --notebook rediseno_zeroshot_colab_v4.ipynb \
                                --entrada tweets_calificados_anclada.csv \
                                --salida salida --min 1

Requisitos que el notebook instala en Colab y aqui hay que tener:
    pip install spacy pandas
    python -m spacy download es_core_news_lg          (~560 MB, CPU)
"""
import argparse
import io
import json
import os
import sys
from collections import Counter, defaultdict

# Bloques del notebook que hacen falta, EN ORDEN. Se localizan por su marcador
# `# === BLOQUE: nombre ===`, nunca por indice: reordenar el notebook no debe
# romper esto en silencio, y si un bloque falta el script se detiene.
BLOQUES = [
    "configuracion-entrada",      # rutas, periodos, zona horaria, CRITERIOS_RUBRICA
    "rubrica-y-polaridad",        # RUBRICA, RUBRICA_TUIT, polaridad, asercion
    "configuracion-nlp",          # MODELO_SPACY, MEXICO, POS_LEMAS, umbrales
    "preparacion-texto",          # limpiar(), NLP_TUIT, texto_util
    "spacy-lemas-entidades",      # spaCy + EntityRuler -> lemas, entidades
    "vocabulario-grafos-nubes",   # log_odds: el estimador, que aqui se REUTILIZA
]
# Se ejecuta tambien el bloque de vocabulario, no por sus figuras sino por
# `log_odds`. Reimplementar el estimador aqui seria la segunda fuente de verdad
# que este script existe para evitar.

MARCA = "# === BLOQUE: {} ==="


def cargar_bloques(ruta_nb):
    with io.open(ruta_nb, encoding="utf-8") as fh:
        nb = json.load(fh)
    encontrados = {}
    for celda in nb["cells"]:
        if celda.get("cell_type") != "code":
            continue
        fuente = "".join(celda["source"])
        primera = fuente.split("\n", 1)[0].strip()
        for nombre in BLOQUES:
            if primera == MARCA.format(nombre):
                if nombre in encontrados:
                    raise SystemExit(
                        "El bloque '{}' aparece dos veces en {}. Los marcadores "
                        "deben ser unicos.".format(nombre, ruta_nb))
                encontrados[nombre] = fuente
    faltan = [b for b in BLOQUES if b not in encontrados]
    if faltan:
        raise SystemExit(
            "No encuentro estos bloques en {}: {}.\n"
            "Cada celda que este script necesita empieza por una linea\n"
            "    {}\n"
            "Si reorganizaste el notebook, repon el marcador o actualiza BLOQUES."
            .format(ruta_nb, ", ".join(faltan), MARCA.format("nombre")))
    return encontrados


def ejecutar(bloques, ruta_entrada):
    g = {"__name__": "__main__"}
    for nombre in BLOQUES:
        if nombre == "preparacion-texto":
            # La ruta del notebook apunta a /content; aqui mandamos la local.
            g["RUTA_ENTRADA"] = ruta_entrada
        try:
            exec(compile(bloques[nombre], "<{}>".format(nombre), "exec"), g)
        except ImportError as exc:
            if "spacy" in str(exc).lower():
                raise SystemExit(
                    "Falta spaCy. Es CPU, no necesita GPU:\n"
                    "    pip install spacy\n"
                    "    python -m spacy download es_core_news_lg")
            raise
        if nombre == "configuracion-entrada":
            g["RUTA_ENTRADA"] = ruta_entrada
    if g.get("NLP_TUIT") is None:
        raise SystemExit("El notebook no construyo NLP_TUIT: revisa la entrada.")
    return g


def cortes(g):
    """Los grupos sobre los que contar.

    Cada corte trae (corte, grupo, subconjunto, universo, descripcion).

    `universo` es el conjunto contra el que ese grupo se contrasta -- el
    "resto" del uno-contra-resto -- o None cuando el corte no admite
    contraste. Un corte con universo es disjunto por construccion: sus grupos
    parten ese universo. Los criterios NO lo son (un tuit puede tocar varios),
    asi que no llevan universo y sus cuentas no suman el corpus.
    """
    t = g["NLP_TUIT"]
    rub = g["RUBRICA_TUIT"].set_index("id")
    # `universo` None puede significar DOS cosas distintas y la pagina las
    # confundia: que el grupo es todo lo que hay (nada contra que contrastar) o
    # que su corte se solapa (contrastar no seria valido). Se declaran aparte.
    grupos = [("total", "corpus", t, None, "todos los tuits del corpus")]

    for valor in ("calificado", "no_calificado"):
        grupos.append(("grupo", valor, t[t.grupo == valor], t,
                       "grupo de la rubrica: algun criterio con nivel > 0"))

    # Prior de la polaridad: los tuits CON polaridad. Los `sin_polaridad` no
    # tienen valencia, asi que tampoco pueden ser el resto de una valencia;
    # se cuentan, pero sin contraste.
    con_pol = t[t.polaridad.isin(("positivo", "negativo", "ambivalente"))]
    for valor in ("positivo", "negativo", "ambivalente"):
        grupos.append(("polaridad", valor, con_pol[con_pol.polaridad == valor], con_pol,
                       "polaridad del tuit, derivada de los criterios de valencia"))
    grupos.append(("polaridad", "sin_polaridad", t[t.polaridad == "sin_polaridad"], None,
                   "calificado solo por un criterio de presencia: no tiene valencia"))

    for c in g["CRITERIOS"]:
        presente = rub["presente_" + c["corto"]]
        sub = t[t["id"].map(presente).fillna(False).astype(bool).values]
        grupos.append(("criterio", c["corto"], sub, None,
                       "{} con nivel > 0 (escala {})".format(c["etiqueta"], c["escala"])))

        # Cruce criterio x valencia. La valencia sale del nivel DE ESTE
        # criterio, no de la polaridad global del tuit: dentro de un criterio
        # el nivel ya es la valencia, y no hace falta la regla de polos
        # primero. Estos si son disjuntos, y su universo es el criterio.
        if c["escala"] != "valencia":
            continue
        nivel = t["id"].map(rub["nivel_" + c["corto"]])
        tramos = (("negativo", g["NIVELES_NEGATIVOS"]),
                  ("ambivalente", (g["NIVEL_AMBIVALENTE"],)),
                  ("positivo", g["NIVELES_POSITIVOS"]))
        for etiqueta, niveles in tramos:
            celda = t[nivel.isin(niveles).values]
            grupos.append(("criterio_valencia", "{}__{}".format(c["corto"], etiqueta), celda, sub,
                           "{} en nivel {} (dentro de su criterio)".format(
                               c["etiqueta"], "-".join(str(int(n)) for n in niveles))))
    return grupos


def _pares(sub, columna, es_entidad):
    """(clave, categoria) por elemento, para entidades y para lemas.

    En entidades la categoria viene emparejada en el propio elemento; en lemas
    viaja en una columna paralela con la etiqueta gramatical.
    """
    if es_entidad:
        for fila in sub[columna]:
            yield [(k, c) for k, c in fila]
        return
    tiene_pos = "lemas_pos" in sub.columns
    pos_col = sub["lemas_pos"] if tiene_pos else [None] * len(sub)
    for fila, pos in zip(sub[columna], pos_col):
        yield list(zip(fila, pos)) if tiene_pos else [(k, "") for k in fila]


def contar(sub, columna, es_entidad):
    """(ocurrencias, tuits, categoria) por termino.

    Se dan LAS DOS cuentas a proposito. El notebook cuenta lemas por ocurrencia
    y entidades por tuit, y esa asimetria es invisible si solo se publica una
    columna. Aqui cada fila trae las dos y quien lea elige.

    La categoria de un termino es la MAS FRECUENTE de las que se le vieron: un
    lema puede aparecer como sustantivo en un tuit y como nombre propio en
    otro, y elegir la primera que salga haria que el color dependiera del orden
    de lectura del corpus.
    """
    ocurr, docs = Counter(), Counter()
    cats = defaultdict(Counter)
    for elementos in _pares(sub, columna, es_entidad):
        vistos = set()
        for clave, cat in elementos:
            ocurr[clave] += 1
            if cat:
                cats[clave][cat] += 1
            vistos.add(clave)
        for clave in vistos:
            docs[clave] += 1
    categoria = {k: c.most_common(1)[0][0] for k, c in cats.items()}
    return ocurr, docs, categoria


def tabla(g, columna, es_entidad, minimo):
    """Una fila por (corte, grupo, termino).

    `z` es la puntuacion de log-odds con prior informativo de ese termino en
    ese grupo contra el resto de su universo, calculada con el MISMO estimador
    que usan las figuras del notebook. Queda vacia cuando el corte no admite
    contraste, y entonces la unica lectura posible es la frecuencia.
    """
    import pandas as pd
    log_odds = g["log_odds"]
    filas = []
    for corte, grupo, sub, universo, _desc in cortes(g):
        ocurr, docs, cat = contar(sub, columna, es_entidad)

        z_de = {}
        if universo is not None and len(sub) and len(universo) > len(sub):
            resto = universo.drop(sub.index)
            oc_resto, _, _ = contar(resto, columna, es_entidad)
            # top enorme: aqui queremos la tabla entera, no el recorte de una
            # figura. El umbral de entrada sigue siendo el del notebook.
            r = log_odds(ocurr, oc_resto, "grupo", "resto",
                         minimo=g["MIN_FRECUENCIA_NUBE"], top=10 ** 9)
            z_de = {f["termino"]: (f["z"], f["n_resto"]) for f in r["grupo"]}

        for termino, n in ocurr.items():
            if n < minimo:
                continue
            z, n_resto = z_de.get(termino, (None, None))
            fila = {"corte": corte, "grupo": grupo, "termino": termino,
                    "ocurrencias": int(n), "tuits": int(docs[termino]),
                    "n_tuits_grupo": int(len(sub)),
                    "z": z, "ocurrencias_resto": n_resto}
            fila["categoria"] = cat.get(termino, "")
            filas.append(fila)
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    # Orden estable: el mismo archivo byte a byte en cada corrida.
    return df.sort_values(["corte", "grupo", "ocurrencias", "termino"],
                          ascending=[True, True, False, True]).reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--notebook", default="rediseno_zeroshot_colab_v4.ipynb")
    ap.add_argument("--entrada", default="tweets_calificados_anclada.csv")
    ap.add_argument("--salida", default="salida")
    ap.add_argument("--min", type=int, default=1,
                    help="frecuencia minima de ocurrencias para entrar (1 = todo)")
    args = ap.parse_args()

    for ruta in (args.notebook, args.entrada):
        if not os.path.exists(ruta):
            raise SystemExit("No existe {}".format(ruta))
    os.makedirs(args.salida, exist_ok=True)

    print("=" * 74)
    print("FRECUENCIAS DEL CORPUS · lemas y entidades, sin GPU")
    print("=" * 74)
    print("  notebook : {}".format(args.notebook))
    print("  entrada  : {}".format(args.entrada))
    print()

    bloques = cargar_bloques(args.notebook)
    print("  bloques localizados: {}".format(", ".join(BLOQUES)))
    print()
    g = ejecutar(bloques, args.entrada)

    import pandas as pd
    lemas = tabla(g, "lemas", False, args.min)
    entidades = tabla(g, "entidades", True, args.min)

    # Los criterios son el unico corte cuyos grupos se solapan; el resto sin
    # universo simplemente no tiene contra que contrastarse.
    SE_SOLAPAN = {"criterio"}

    def contraste(corte, universo):
        if universo is not None:
            return "z"
        return "se_solapa" if corte in SE_SOLAPAN else "sin_contraste"

    grupos = pd.DataFrame([
        {"corte": c, "grupo": n, "n_tuits": len(s),
         "contraste": contraste(c, u),
         "disjunto": "si" if c not in SE_SOLAPAN else "no",
         "n_tuits_universo": len(u) if u is not None else "",
         "descripcion": desc}
        for c, n, s, u, desc in cortes(g)])

    salidas = [("frecuencias_lemas.csv", lemas),
               ("frecuencias_entidades.csv", entidades),
               ("frecuencias_grupos.csv", grupos)]
    print()
    print("=" * 74)
    for nombre, df in salidas:
        ruta = os.path.join(args.salida, nombre)
        df.to_csv(ruta, index=False, encoding="utf-8-sig")
        print("  {:<28} {:>7} filas   {}".format(nombre, len(df), ruta))

    print()
    print("  GRUPOS")
    for _, f in grupos.iterrows():
        print("     {:<18} {:<26} {:>6} tuits   {}".format(
            f["corte"], f["grupo"], f["n_tuits"],
            "" if f["disjunto"] == "si" else "(se solapa; sin z)"))
    print()
    print("  Los lemas se cuentan por OCURRENCIA y por TUIT; las dos columnas van")
    print("  en cada fila. Las figuras del notebook usan ocurrencias para lemas y")
    print("  tuits para entidades: si comparas contra ellas, elige la columna que")
    print("  corresponde.")
    print("=" * 74)


if __name__ == "__main__":
    main()
