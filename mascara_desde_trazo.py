# -*- coding: utf-8 -*-
"""Convierte un dibujo de trazo en una mascara para `nubes_corpus.py --mascara`.

`maskImage` de echarts-wordcloud rellena donde la imagen es OPACA. Un PNG de
trazo con fondo blanco es 100% opaco, asi que tal cual no enmascara nada:
rellenaria el rectangulo entero. Hay que producir la transparencia.

El problema es que el blanco de DENTRO de la figura y el de FUERA son el mismo
color, asi que no se pueden separar por umbral. Se separan por CONECTIVIDAD: el
blanco de fuera toca el borde de la imagen; el de dentro esta encerrado por el
trazo. Se inunda desde los bordes y lo que no se moja es el interior.

Resultado: palabras en los paneles interiores, costuras en blanco. El trazo no
se dibuja -- se lee en negativo, que es lo que lo hace legible como figura.

    python mascara_desde_trazo.py "image copy 2.png" mascara_balon.png
    python mascara_desde_trazo.py entrada.png salida.png --incluir-trazo
"""
import argparse
import sys
from collections import deque

from PIL import Image


def construir(ruta, salida, umbral=128, incluir_trazo=False, margen=0, escala=None):
    im = Image.open(ruta).convert("RGBA")
    if escala:
        im = im.resize((int(im.width * escala), int(im.height * escala)), Image.LANCZOS)
    w, h = im.size
    px = im.load()

    # Consciente del ALFA. Un PNG al que ya le quitaron el fondo trae el blanco
    # como transparente, y pasarlo a gris lo volveria negro -- es decir, trazo.
    # Transparente es claro, no oscuro.
    #
    # Esto importa para ALINEAR: la mascara y la imagen que se dibuja detras
    # tienen que salir del MISMO archivo. Con dos archivos de encuadre distinto,
    # las palabras siguen a uno y el dibujo al otro, y se salen de la figura.
    def es_oscuro(x, y):
        r, g, b, a = px[x, y]
        return a >= 128 and (r + g + b) / 3 < umbral

    oscuro = [[es_oscuro(x, y) for x in range(w)] for y in range(h)]

    # Inundacion desde los cuatro bordes sobre lo NO oscuro: eso es el fuera.
    fuera = [[False] * w for _ in range(h)]
    cola = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not oscuro[y][x] and not fuera[y][x]:
                fuera[y][x] = True
                cola.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not oscuro[y][x] and not fuera[y][x]:
                fuera[y][x] = True
                cola.append((x, y))
    while cola:
        x, y = cola.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not oscuro[ny][nx] and not fuera[ny][nx]:
                fuera[ny][nx] = True
                cola.append((nx, ny))

    # Rellenable: dentro de la figura. Con --incluir-trazo tambien el trazo,
    # y entonces la figura sale maciza y las costuras desaparecen.
    dentro = [[(not fuera[y][x]) and (incluir_trazo or not oscuro[y][x])
               for x in range(w)] for y in range(h)]

    # Margen: aleja las palabras del trazo, para que la costura se vea.
    for _ in range(margen):
        prev = [fila[:] for fila in dentro]
        for y in range(h):
            for x in range(w):
                if not prev[y][x]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < w and 0 <= ny < h) or not prev[ny][nx]:
                        dentro[y][x] = False
                        break

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    po = out.load()
    n = 0
    for y in range(h):
        for x in range(w):
            if dentro[y][x]:
                # NEGRO PURO, no "oscuro". Comprobado: con (17,17,17) la
                # biblioteca no rellena nada y la nube sale vacia sin avisar.
                # El area rellenable tiene que ser exactamente #000000.
                po[x, y] = (0, 0, 0, 255)
                n += 1
    out.save(salida)

    tot = w * h
    print("=" * 66)
    print("MASCARA · {}  ->  {}".format(ruta, salida))
    print("=" * 66)
    print("  tamano            {}x{}".format(w, h))
    print("  area RELLENABLE   {:>8} px  ({:.1%} del lienzo)".format(n, n / tot))
    print("  trazo             {}".format("incluido (figura maciza)" if incluir_trazo
                                          else "excluido (costuras en negativo)"))
    if margen:
        print("  margen            {} px alrededor del trazo".format(margen))
    print()
    print("  Las palabras solo caben en ese {:.0%}. Con demasiadas o con el".format(n / tot))
    print("  lienzo pequeno, wordcloud2 descarta las que no entran EN SILENCIO.")
    return n / tot


def negativo(ruta, salida, umbral=128, margen=0, escala=None):
    """Rellenable = TODO lo claro, sin distinguir dentro de fuera.

    La figura no se dibuja con palabras: se dibuja con su AUSENCIA. Las
    palabras ocupan el fondo y el trazo queda como hueco, asi que lo que se
    reconoce es el negativo. Sirve cuando la identidad de la figura esta en
    lineas internas, que una silueta normal no puede representar.
    """
    im = Image.open(ruta).convert("RGBA")
    if escala:
        im = im.resize((int(im.width * escala), int(im.height * escala)), Image.LANCZOS)
    w, h = im.size
    px = im.load()

    # Claro = transparente o de luminosidad alta. Las dos vias, porque el
    # archivo puede venir con el blanco ya en transparente o todavia en blanco.
    claro = [[(px[x, y][3] < 128) or (sum(px[x, y][:3]) / 3 >= umbral)
              for x in range(w)] for y in range(h)]

    for _ in range(margen):
        prev = [f[:] for f in claro]
        for y in range(h):
            for x in range(w):
                if not prev[y][x]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < w and 0 <= ny < h) or not prev[ny][nx]:
                        claro[y][x] = False
                        break

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    po = out.load()
    n = 0
    for y in range(h):
        for x in range(w):
            if claro[y][x]:
                po[x, y] = (0, 0, 0, 255)    # NEGRO PURO, ver construir()
                n += 1
    out.save(salida)
    print("=" * 66)
    print("MASCARA NEGATIVA · {}  ->  {}".format(ruta, salida))
    print("=" * 66)
    print("  tamano            {}x{}".format(w, h))
    print("  area RELLENABLE   {:>8} px  ({:.1%})   <- el fondo y los blancos".format(n, n / (w * h)))
    print("  la figura se lee por AUSENCIA de palabras")
    return n / (w * h)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--umbral", type=int, default=128)
    ap.add_argument("--incluir-trazo", action="store_true",
                    help="rellena tambien el trazo: figura maciza, sin costuras")
    ap.add_argument("--margen", type=int, default=0,
                    help="px de separacion entre las palabras y el trazo")
    ap.add_argument("--escala", type=float, default=None)
    ap.add_argument("--negativo", action="store_true",
                    help="rellena TODO lo claro, incluido el fondo: la figura "
                         "aparece como agujeros dentro de un bloque de palabras")
    args = ap.parse_args()
    if args.negativo:
        negativo(args.entrada, args.salida, args.umbral, args.margen, args.escala)
    else:
        construir(args.entrada, args.salida, args.umbral, args.incluir_trazo,
                  args.margen, args.escala)


if __name__ == "__main__":
    main()
