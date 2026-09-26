"""
Genera dos wordclouds del grupo 'calificado' a partir de frecuencias_lemas.csv:
  1. PNG estático en alta resolución (librería `wordcloud`)
  2. HTML interactivo con Apache ECharts + echarts-wordcloud

Uso:
    pip install pandas wordcloud
    python generar_wordcloud.py frecuencias_lemas.csv
"""
import sys
import json
import pandas as pd
from pathlib import Path

CSV = sys.argv[1] if len(sys.argv) > 1 else "frecuencias_lemas.csv"
GRUPO = "calificado"        # ojo: en el CSV es singular
TOP_N = 250                 # términos para la versión ECharts

# ---------- Cargar y filtrar ----------
df = pd.read_csv(CSV, encoding="utf-8-sig")   # utf-8-sig por el BOM del archivo
sub = df[df["grupo"] == GRUPO]
print(f"{len(sub)} términos en el grupo '{GRUPO}'")

# ---------- 1. PNG en alta resolución ----------
from wordcloud import WordCloud

freqs = dict(zip(sub["termino"], sub["ocurrencias"]))
wc = WordCloud(
    width=4000, height=2500,
    background_color="white",
    colormap="viridis",
    max_words=250,
    prefer_horizontal=0.9,
    relative_scaling=0.5,
    random_state=42,
    collocations=False,
).generate_from_frequencies(freqs)
wc.to_file("wordcloud_calificado.png")
print("→ wordcloud_calificado.png")

# ---------- 2. Datos para ECharts ----------
top = sub.sort_values("ocurrencias", ascending=False).head(TOP_N)
data = [{"name": t, "value": int(v)} for t, v in zip(top["termino"], top["ocurrencias"])]

plantilla = Path("wordcloud_echarts.html").read_text(encoding="utf-8")
# La plantilla ya trae los datos embebidos; para regenerarla con datos nuevos,
# sustituye la línea `const DATA = [...]` por:
nueva = plantilla
import re
nueva = re.sub(r"const DATA = \[.*?\];", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";", nueva, flags=re.S)
Path("wordcloud_echarts.html").write_text(nueva, encoding="utf-8")
print("→ wordcloud_echarts.html")
