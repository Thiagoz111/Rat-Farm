"""
Borde NEGRO para los iconos pixel-art de la GUI (como la referencia C:/VIDEOS/2026-10-10 21-46-04.mp4): el contorno
del dibujo pasa a negro y se agrega un anillo negro mas por fuera (2 px de arte). Lee los PNG exportados x16, trabaja
en la resolucion del arte (16/24/32 px) y guarda en vfx/outlined/ con el mismo nombre y escala.
  python make_outline.py                 -> outlined/*.png
  python make_outline.py preview RUTA    -> ademas una hoja de prueba
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outlined")
SCALE = 16
BLACK = (10, 10, 12, 255)
NAMES = [
    "ui3d_cart", "ui3d_book", "ui3d_upgrade", "ui3d_backpack", "ui3d_gift", "ui3d_moneybag", "ui3d_house", "ui3d_stall",
    "ui_cheese", "px5_clover",
] + sorted(f[:-4] for f in os.listdir(HERE) if f.startswith("px4_") and f.endswith(".png"))


def shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = m[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
    return out


def outline(img):
    art = img.width // SCALE
    a = np.array(img.resize((art, art), Image.NEAREST).convert("RGBA"))
    solid = a[..., 3] > 127
    a[~solid] = 0
    # contorno del dibujo: opaco con algun vecino (4) transparente
    edge = np.zeros_like(solid)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        edge |= solid & ~shift(solid, dx, dy)
    # anillo de afuera: transparente con algun vecino (8) opaco
    ring = np.zeros_like(solid)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            ring |= shift(solid, dx, dy)
    ring &= ~solid
    a[edge] = BLACK
    a[ring] = BLACK
    return Image.fromarray(a, "RGBA").resize((art * SCALE, art * SCALE), Image.NEAREST), art


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    done = []
    for n in NAMES:
        src = os.path.join(HERE, n + ".png")
        if not os.path.exists(src):
            print("FALTA", n)
            continue
        im, art = outline(Image.open(src))
        im.save(os.path.join(OUT, n + ".png"))
        done.append((n, im))
    print(len(done), "iconos ->", OUT)
    if len(sys.argv) > 2 and sys.argv[1] == "preview":
        cell = 96
        cols = 10
        rows = (len(done) + cols - 1) // cols
        sheet = Image.new("RGBA", (cols * cell, rows * cell), (70, 150, 80, 255))
        for i, (n, im) in enumerate(done):
            sheet.alpha_composite(im.resize((cell - 8, cell - 8), Image.NEAREST), ((i % cols) * cell + 4, (i // cols) * cell + 4))
        sheet.save(sys.argv[2])
