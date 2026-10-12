"""
Trebol de 4 hojas pixel-art 32x32 (ROLL A RAT: icono del gamepass 2x Luck, como el trebol de la referencia).
Dibujado en 2D: 4 hojas de corazon en diagonal + tallo, borde oscuro, luz arriba a la izquierda, sombra abajo a la
derecha, vena en cada hoja, separacion entre hojas y brillos blancos.
  python make_clover.py                  -> px5_clover.png (x16 = 512 px) al lado de este script
  python make_clover.py preview RUTA.png -> ademas una hoja de prueba ampliada
En Roblox: ResampleMode Pixelated + UIKit.SnapPixels (atributo Art = 32).
"""
import os
import sys

import numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
N, SCALE = 32, 16

OUTLINE = (14, 54, 22)
SEAM = (24, 96, 36)  # (entre hojas y vena)
SHADOW = (34, 140, 48)
BASE = (62, 190, 70)
LIGHT = (118, 228, 92)
HILITE = (206, 255, 168)
STEM, STEM_DK = (70, 160, 56), (36, 110, 40)

C = np.array((15.5, 13.5))  # centro del trebol
ys, xs = np.mgrid[0:N, 0:N]
P = np.stack([xs + 0.5, ys + 0.5], -1)  # centro de cada pixel


def disk(c, r):
    return ((P - np.array(c)) ** 2).sum(-1) <= r * r


# 4 hojas de corazon: dos lobulos afuera (la muesca mira hacia afuera) + una gota hacia el centro
leaf_id = np.full((N, N), -1)
dirs = []
for k, a in enumerate((225, 315, 45, 135)):  # arriba-izq, arriba-der, abajo-der, abajo-izq (y crece hacia abajo)
    t = np.radians(a)
    d = np.array((np.cos(t), np.sin(t)))
    n = np.array((-d[1], d[0]))
    v = P - C
    along, side = v @ d, v @ n
    wedge = (along > 0.3) & (np.abs(side) <= along * 0.72 + 0.4) & (along < 8.2) # (punta hacia el centro)
    m = disk(C + d * 7.6 + n * 2.6, 3.25) | disk(C + d * 7.6 - n * 2.6, 3.25) | wedge
    leaf_id[m & (leaf_id < 0)] = k
    dirs.append((d, n))
leaf = leaf_id >= 0

# tallo: de abajo del centro curvandose hacia abajo a la derecha
stem = np.zeros((N, N), bool)
for s in np.linspace(0, 1, 60):
    x = C[0] + 1.0 + s * 8.0 + np.sin(s * 2.2) * 1.5
    y = C[1] + 5.0 + s * 11.5
    stem |= disk((x, y), 1.25)
stem &= ~leaf

shape = leaf | stem
img = np.zeros((N, N, 4), np.uint8)


def put(mask, col):
    img[mask] = (*col, 255)


def inside(x, y):
    return 0 <= x < N and 0 <= y < N


# relleno de las hojas con luz arriba-izquierda
for y in range(N):
    for x in range(N):
        if not leaf[y, x]:
            continue
        k = leaf_id[y, x]
        ul = not (inside(x - 1, y - 1) and leaf_id[y - 1, x - 1] == k)
        ul2 = not (inside(x - 2, y - 2) and leaf_id[y - 2, x - 2] == k)
        dr = not (inside(x + 1, y + 1) and leaf_id[y + 1, x + 1] == k)
        dr2 = not (inside(x + 2, y + 2) and leaf_id[y + 2, x + 2] == k)
        col = BASE
        if dr:
            col = SHADOW
        elif ul:
            col = HILITE if k == 0 else LIGHT
        elif ul2:
            col = LIGHT
        elif dr2:
            col = (48, 164, 58)
        img[y, x] = (*col, 255)

# vena de cada hoja (del centro hacia la muesca) y costura entre hojas
for y in range(N):
    for x in range(N):
        k = leaf_id[y, x]
        if k < 0:
            continue
        d, n = dirs[k]
        v = P[y, x] - C
        along, side = v @ d, v @ n
        if 1.5 < along < 8.5 and abs(side) < 0.55:
            img[y, x] = (*SEAM, 255)
        for dx, dy in ((1, 0), (0, 1)):
            xx, yy = x + dx, y + dy
            if inside(xx, yy) and leaf_id[yy, xx] >= 0 and leaf_id[yy, xx] != k:
                img[y, x] = (*SEAM, 255)

# tallo (claro arriba-izquierda)
for y in range(N):
    for x in range(N):
        if stem[y, x]:
            edge = not (inside(x + 1, y) and stem[y, x + 1])
            img[y, x] = (*(STEM_DK if edge else STEM), 255)

# centro y brillos
cx, cy = int(C[0]), int(C[1])
for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
    img[cy + dy, cx + dx] = (*SEAM, 255)
for x, y in ((8, 6), (9, 5), (7, 8), (19, 5), (20, 6)):
    if leaf[y, x]:
        img[y, x] = (255, 255, 255, 255)

# borde oscuro (8 vecinos) alrededor de todo
out = np.zeros((N, N), bool)
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        sh = np.zeros_like(shape)
        sy0, sy1 = max(0, dy), N + min(0, dy)
        sx0, sx1 = max(0, dx), N + min(0, dx)
        sh[sy0:sy1, sx0:sx1] = shape[sy0 - dy:sy1 - dy, sx0 - dx:sx1 - dx]
        out |= sh
out &= ~shape
put(out, OUTLINE)

big = Image.fromarray(img, "RGBA").resize((N * SCALE, N * SCALE), Image.NEAREST)
path = os.path.join(OUT, "px5_clover.png")
big.save(path)
print("saved", path)

if len(sys.argv) > 2 and sys.argv[1] == "preview":
    sheet = Image.new("RGBA", (N * 12 + 40, N * 12 + 40), (60, 140, 70, 255))
    sheet.alpha_composite(Image.fromarray(img, "RGBA").resize((N * 12, N * 12), Image.NEAREST), (20, 20))
    sheet.save(sys.argv[2])
    print("preview", sys.argv[2])
