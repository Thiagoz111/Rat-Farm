"""
Billete de dinero pixel-art 24x24 (ROLL A RAT: va al lado de la plata del HUD, de lo que gana cada rata, precios...).
Un billete en diagonal (pendiente 2:1) y ondulado: margen claro (luz arriba), marco oscuro, medallon redondo claro
con el $ derecho, puntitos en las esquinas, borde negro del billete + anillo negro de afuera (2 px como los otros).
El usuario lo eligio entre 4 variantes (diagonal, abanico, pila, ondulado) -> ondulado.
(v1 = 16x16 plano, v2 = fajo con faja dorada: reemplazados.)
  python make_money.py                  -> px7_bill.png (x16 = 384 px)
  python make_money.py preview RUTA.png -> ademas una hoja de prueba (grande + tamanos reales)
En Roblox: ResampleMode Pixelated + UIKit.SnapPixels (atributo Art = 24).
"""
import os
import sys

import numpy as np
from PIL import Image

N, SCALE = 24, 16
OUT = os.path.dirname(os.path.abspath(__file__))
K = (10, 10, 12)
COL = {
    "H": (214, 255, 170), "L": (148, 230, 106), "G": (92, 198, 76), "G2": (74, 174, 64),
    "F": (32, 106, 46), "O": (226, 252, 192), "O2": (186, 236, 152), "S": (24, 90, 40),
}


def shift(m, dx, dy):
    out = np.zeros_like(m)
    out[max(0, dy):N + min(0, dy), max(0, dx):N + min(0, dx)] = m[max(0, -dy):N + min(0, -dy), max(0, -dx):N + min(0, -dx)]
    return out


def bill(cx, cy, ang, hl, hw, wave):
    """billete rotado (ang en rad, y hacia abajo) y ondulado; muestrea el centro de cada pixel -> (mask, rgb)"""
    ys, xs = np.mgrid[0:N, 0:N]
    px, py = xs + 0.5 - cx, ys + 0.5 - cy
    c, s = np.cos(ang), np.sin(ang)
    u = px * c + py * s
    v = -px * s + py * c
    v = v - wave * np.sin(u / hl * np.pi)
    inside = (np.abs(u) <= hl) & (np.abs(v) <= hw)
    au, av = np.abs(u), np.abs(v)
    lab = np.full((N, N), "G", object)
    lab[v > hw * 0.45] = "G2"
    margin = (au > hl - 1.2) | (av > hw - 1.2)
    lab[(au > hl - 2.2) | (av > hw - 2.2)] = "F"
    lab[margin & (v < 0)] = "H"
    lab[margin & (v >= 0)] = "L"
    r = np.hypot(u, v)
    lab[(r < 4.6) & ~margin] = "F"
    lab[r < 3.6] = "O"
    lab[(r < 3.6) & (u + v > 3.2)] = "O2"
    for su in (-1, 1):
        for sv in (-1, 1):
            lab[np.hypot(u - su * (hl - 4.2), v - sv * (hw - 3.4)) < 0.75] = "O"
    rgb = np.zeros((N, N, 3), np.uint8)
    for k, col in COL.items():
        rgb[lab == k] = col
    edge = np.zeros_like(inside)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        edge |= inside & ~shift(inside, dx, dy)
    rgb[edge] = K
    return inside, rgb


DOLLAR = [
    "..#..",
    ".####",
    "#....",
    ".###.",
    "....#",
    "####.",
    "..#..",
]

m, rgb = bill(12, 12, -np.arctan(0.5), 11.6, 6.0, wave=1.0)
img = np.zeros((N, N, 4), np.uint8)
img[m, :3] = rgb[m]
img[m, 3] = 255
for j, row in enumerate(DOLLAR):  # $ derecho en el medallon
    for i, ch in enumerate(row):
        if ch == "#":
            img[9 + j, 10 + i] = (*COL["S"], 255)
solid = img[..., 3] > 0
ring = np.zeros_like(solid)
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        ring |= shift(solid, dx, dy)
img[ring & ~solid] = (*K, 255)

art = Image.fromarray(img, "RGBA")
path = os.path.join(OUT, "px7_bill.png")
art.resize((N * SCALE, N * SCALE), Image.NEAREST).save(path)
print("saved", path)

if len(sys.argv) > 2 and sys.argv[1] == "preview":
    Z = 14
    sheet = Image.new("RGBA", (N * Z + 260, N * Z + 40), (34, 38, 46, 255))
    sheet.alpha_composite(art.resize((N * Z, N * Z), Image.NEAREST), (20, 20))
    y = 20
    for k in (1, 2, 3):  # tamanos reales en pantalla
        sheet.alpha_composite(art.resize((N * k, N * k), Image.NEAREST), (N * Z + 40, y))
        y += N * k + 16
    sheet.save(sys.argv[2])
