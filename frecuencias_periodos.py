# -*- coding: utf-8 -*-
"""Frecuencias periodo x nivel por criterio: las cifras de las barras apiladas
"por periodo" de graficas_calificaciones_anclada.html.

Esa grafica la arma evaluadorTweets en el navegador (plantilla_graficas.html,
panel g-periodos) a partir del agregado de viz.py, y ningun script la escribe a
disco. Este la reproduce en Python sobre `tweets_calificados_anclada.csv`, con
las MISMAS reglas que viz.py + config.toml:

  * la fecha `created_at` viene en UTC y se corta por dia en
    America/Mexico_City antes de asignar el periodo;
  * los periodos son intervalos [desde, hasta) -- el 11 de junio ya es DURANTE;
  * solo se apilan las calificaciones de VALENCIA: estado OK y nivel distinto
    del de ausencia. Con `niveles_ausencia = "auto"` el nivel 0 es ausencia en
    los cuatro criterios (su descriptor niega que el tuit toque la dimension),
    asi que en saliencia de violencia la barra solo lleva el nivel 1;
  * NO_APLICABLE, nivel 0 y BLOQUEADO quedan fuera de la barra y se reportan
    aparte por periodo, para que el recorte sea visible.

    python frecuencias_periodos.py
    python frecuencias_periodos.py --entrada otro.csv --salida otro.md
"""
import argparse
import os

import pandas as pd

RUTA_ENTRADA = "tweets_calificados_anclada.csv"
RUTA_SALIDA = "tablas_frecuencias_periodos.md"
ZONA = "America/Mexico_City"

# Copia literal de [[periodos]] en evaluadorTweets/config.toml.
PERIODOS = [
    {"nombre": "PREVIO A MUNDIAL",              "desde": "2026-05-31", "hasta": "2026-06-11"},
    {"nombre": "DURANTE MUNDIAL EN MEXICO",     "desde": "2026-06-11", "hasta": "2026-07-06"},
    {"nombre": "DESPUES DE PARTIDOS EN MEXICO", "desde": "2026-07-06", "hasta": None},
]

# Mismo orden que los paneles de la pagina (rubrica 1, 2, 3, 4).
CRITERIOS = [
    {"prefijo": "rubrica_1_atmosfera_de_mexic", "etiqueta": "Atmósfera",
     "nombre": "ATMÓSFERA DE MÉXICO: DIMENSIÓN SIMPÁTICA / EMOCIONAL", "niveles": [1, 2, 3, 4, 5]},
    {"prefijo": "rubrica_2_imagen_cultural_de", "etiqueta": "Imagen cultural",
     "nombre": "IMAGEN CULTURAL DE MÉXICO: DIMENSIÓN ESTÉTICA", "niveles": [1, 2, 3, 4, 5]},
    {"prefijo": "rubrica_3_perspectiva_politi", "etiqueta": "Perspectiva política",
     "nombre": "PERSPECTIVA POLÍTICA DE MÉXICO: DIMENSIÓN FUNCIONAL", "niveles": [1, 2, 3, 4, 5]},
    {"prefijo": "rubrica_4_saliencia_de_viole", "etiqueta": "Saliencia de violencia",
     "nombre": "SALIENCIA DE VIOLENCIA EN MÉXICO", "niveles": [1]},
]

ETIQUETA_NIVEL = {1: "1 · muy negativo", 2: "2 · negativo", 3: "3 · ambivalente o mixto",
                  4: "4 · positivo", 5: "5 · muy positivo"}
ETIQUETA_PRESENCIA = {1: "1 · presente"}


def leer(ruta):
    df = pd.read_csv(ruta, low_memory=False)
    for c in df.columns:
        if c.endswith("_nivel"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        if c.endswith("_aplicable"):
            df[c] = df[c].astype("string").str.strip().str.upper()
    return df


def fecha_local(created_at):
    """UTC -> dia local, como _a_utc + _a_hora_local de viz.py."""
    utc = None
    for extra in ({"format": "mixed"}, {"format": "ISO8601"}, {}):
        try:
            utc = pd.to_datetime(created_at, errors="coerce", utc=True, **extra)
            break
        except (ValueError, TypeError):
            continue
    if utc is None:
        utc = pd.to_datetime(created_at, errors="coerce", utc=True)
    return utc.dt.tz_convert(ZONA).dt.normalize().dt.tz_localize(None)


def asignar_periodo(fecha):
    periodo = pd.Series(pd.NA, index=fecha.index, dtype="object")
    for p in PERIODOS:
        dentro = fecha >= pd.Timestamp(p["desde"])
        if p["hasta"]:
            dentro &= fecha < pd.Timestamp(p["hasta"])
        periodo = periodo.mask(dentro & periodo.isna(), p["nombre"])
    return periodo


def contar(df):
    """Una tabla por criterio: filas = periodo, columnas = nivel + fuera de barra."""
    df = df.copy()
    df["periodo"] = asignar_periodo(fecha_local(df["created_at"]))
    nombres = [p["nombre"] for p in PERIODOS]
    fuera = df["periodo"].isna()

    tablas = {}
    for c in CRITERIOS:
        niv, apl = df[c["prefijo"] + "_nivel"], df[c["prefijo"] + "_aplicable"]
        filas = []
        for nombre in nombres + ["(fuera de periodo)"]:
            m = fuera if nombre == "(fuera de periodo)" else (df["periodo"] == nombre)
            fila = {"periodo": nombre}
            for n in c["niveles"]:
                fila[n] = int((m & (niv == n)).sum())
            fila["valencia"] = sum(fila[n] for n in c["niveles"])
            fila["nivel_0"] = int((m & (niv == 0)).sum())
            fila["no_aplicable"] = int((m & (apl == "NO") & niv.isna()).sum())
            fila["bloqueado"] = int((m & (apl == "BLOQUEADO")).sum())
            fila["tuits"] = int(m.sum())
            filas.append(fila)
        tablas[c["prefijo"]] = pd.DataFrame(filas).set_index("periodo")
    return tablas, int(fuera.sum())


def corto(nombre):
    """'PREVIO A MUNDIAL' -> 'PREVIO', igual que el eje de la grafica."""
    return nombre.split(" ")[0]


def pct(n, t):
    return f"{100 * n / t:.1f} %" if t else "—"


def render_md(tablas, n_total, n_fuera, origen):
    L = []
    L.append("# Frecuencias por periodo y nivel (barras apiladas por periodo)\n")
    L.append(f"Fuente: `{origen}` ({n_total:,} tuits). Generado por `frecuencias_periodos.py`.")
    L.append("Reproduce el panel «por periodo» de `graficas_calificaciones_anclada.html`, "
             "que evaluadorTweets dibuja en el navegador y no guarda en ninguna tabla.\n")
    L.append("Periodos (intervalos cerrados por la izquierda y abiertos por la derecha, "
             f"día cortado en {ZONA}):\n")
    L.append("| Periodo | Desde | Hasta |")
    L.append("|---|---|---|")
    for p in PERIODOS:
        L.append(f"| {p['nombre']} | {p['desde']} | {p['hasta'] or 'abierto'} |")
    L.append("")
    if n_fuera:
        L.append(f"Hay {n_fuera:,} tuits fuera de todo periodo; se listan en una fila aparte "
                 "y no entran en las barras.\n")

    for c in CRITERIOS:
        t = tablas[c["prefijo"]]
        etq = ETIQUETA_PRESENCIA if c["niveles"] == [1] else ETIQUETA_NIVEL
        L.append(f"## {c['etiqueta']} ({c['nombre']})\n")
        L.append("Frecuencias absolutas. La barra de la gráfica es la suma de las columnas de nivel; "
                 "la etiqueta del eje es «PERIODO (valencia)».\n")
        L.append("| Periodo | " + " | ".join(etq[n] for n in c["niveles"]) +
                 " | Valencia (barra) | Nivel 0 | No aplicable | Bloqueado | Tuits del periodo |")
        L.append("|---|" + "---:|" * (len(c["niveles"]) + 5))
        for nombre, r in t.iterrows():
            if nombre == "(fuera de periodo)" and r["tuits"] == 0:
                continue
            et = nombre if nombre.startswith("(") else f"{corto(nombre)} ({r['valencia']})"
            L.append(f"| {et} | " + " | ".join(str(r[n]) for n in c["niveles"]) +
                     f" | {r['valencia']} | {r['nivel_0']} | {r['no_aplicable']:,} | "
                     f"{r['bloqueado']} | {r['tuits']:,} |")
        tot = t.sum()
        L.append("| Total | " + " | ".join(str(tot[n]) for n in c["niveles"]) +
                 f" | {tot['valencia']} | {tot['nivel_0']} | {tot['no_aplicable']:,} | "
                 f"{tot['bloqueado']} | {tot['tuits']:,} |")
        L.append("")
        if len(c["niveles"]) > 1:
            L.append("Proporciones dentro de la barra (modo «proporción» de la página):\n")
            L.append("| Periodo | " + " | ".join(etq[n] for n in c["niveles"]) + " |")
            L.append("|---|" + "---:|" * len(c["niveles"]))
            for nombre, r in t.iterrows():
                if nombre == "(fuera de periodo)" and r["tuits"] == 0:
                    continue
                et = nombre if nombre.startswith("(") else f"{corto(nombre)} ({r['valencia']})"
                L.append(f"| {et} | " + " | ".join(pct(r[n], r["valencia"]) for n in c["niveles"]) + " |")
            L.append("")

    L.append("## Notas de lectura\n")
    L.append("- **Valencia** es lo único apilado: calificaciones con estado OK y nivel distinto del de "
             "ausencia. Es la regla `niveles_ausencia = \"auto\"` de `config.toml`, que marca como "
             "ausencia el nivel cuyo descriptor niega que el tuit toque la dimensión; en los cuatro "
             "criterios ese nivel es el 0.")
    L.append("- **Saliencia de violencia** es binaria (0/1) y mide presencia, no valencia. Con la regla "
             "anterior su barra solo lleva el nivel 1, y los 0 (que aquí sí son un hallazgo) quedan en "
             "la columna «Nivel 0». El propio `config.toml` advierte que esa regla es la inversa de lo "
             "que este criterio necesita.")
    L.append("- **No aplicable** es `aplicable = NO` sin nivel; **bloqueado** es respuesta bloqueada por "
             "el proveedor. Ninguno de los dos entra en la barra ni en el denominador de las proporciones.")
    L.append("- **Tuits del periodo** es el total de tuits del corpus con fecha en ese periodo, sin "
             "importar el criterio; por eso es la misma cifra en las cuatro tablas.")
    L.append("- La fecha se convierte de UTC a hora de la Ciudad de México antes de cortar el día, igual "
             "que en viz.py: un tuit de las 23:00 UTC del 10 de junio cae el 10 de junio local y es PREVIO.")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entrada", default=RUTA_ENTRADA)
    ap.add_argument("--salida", default=RUTA_SALIDA)
    args = ap.parse_args()

    df = leer(args.entrada)
    tablas, n_fuera = contar(df)
    md = render_md(tablas, len(df), n_fuera, os.path.basename(args.entrada))
    with open(args.salida, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print(f"[escrito] {args.salida}")


if __name__ == "__main__":
    main()
