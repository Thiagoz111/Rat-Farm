"""
Iconos del TRADE y de la MOCHILA (ROLL A RAT, 2026-10-12).
  pass_trade      32x32 pixel-art: dos flechas que se cruzan (verde arriba ->, naranja abajo <-) con bisel, brillo
                  y borde negro como todos los iconos (make_pass_icons.finish). Cartel de la Trade Plaza + ventana Trade.
  topbar_backpack 256x256 liso (NO pixel): mochila blanca de linea como los iconos de la barra de Roblox
                  (el boton de la mochila que va al lado del menu de Roblox). Se usa con ResampleMode Default.
  python make_trade_icons.py   -> outlined/pass_trade.png (x16) + outlined/topbar_backpack.png
"""
import os

import numpy as np
from PIL import Image, ImageDraw

import make_pass_icons as MP

N, SCALE = MP.N, MP.SCALE
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outlined")

GREEN = ((22, 120, 40), (60, 196, 70), (140, 240, 110), (230, 255, 200))
ORANGE = ((170, 70, 10), (250, 140, 30), (255, 196, 80), (255, 240, 190))


def arrow(y0, y1, x_tail, x_neck, x_tip, head_pad, right):
    """flecha horizontal: barra de y0..y1 y punta triangular; right = apunta a la derecha"""
    if right:
        bar = MP.poly([(x_tail, y0), (x_neck, y0), (x_neck, y1), (x_tail, y1)])
        head = MP.poly([(x_neck, y0 - head_pad), (x_tip, (y0 + y1) / 2), (x_neck, y1 + head_pad)])
    else:
        bar = MP.poly([(x_neck, y0), (x_tail, y0), (x_tail, y1), (x_neck, y1)])
        head = MP.poly([(x_neck, y0 - head_pad), (x_tip, (y0 + y1) / 2), (x_neck, y1 + head_pad)])
    return bar | head


def ring_outline(img):
    """borde negro SOLO por afuera (finish() tambien pinta el borde de adentro y se come las puntas finas)"""
    solid = img[..., 3] > 0
    ring = np.zeros_like(solid)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            ring |= MP.shift(solid, dx, dy)
    out = img.copy()
    out[ring & ~solid] = (10, 10, 12, 255)
    return out


def trade():
    img = np.zeros((N, N, 4), np.uint8)
    top = arrow(5, 12, 2, 18, 30, 4, True)
    bot = arrow(19, 26, 30, 14, 2, 4, False)
    MP.bevel(img, top, GREEN)
    MP.seam(img, bot, (40, 20, 6))
    MP.bevel(img, bot, ORANGE)
    v = ring_outline(img)
    MP.sparkle(v, 28, 28, big=True, color=(255, 246, 170))
    MP.sparkle(v, 3, 2)
    return v


def topbar_backpack(size=256):
    """mochila blanca de linea (estilo iconos de la barra de Roblox): cuerpo redondeado, manija, bolsillo"""
    im = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = size * 4 / 256
    w = int(20 * s)
    white = (255, 255, 255, 255)
    d.rounded_rectangle([60 * s, 70 * s, 196 * s, 222 * s], radius=int(40 * s), outline=white, width=w)
    d.arc([96 * s, 30 * s, 160 * s, 100 * s], 180, 360, fill=white, width=w)  # manija
    d.rounded_rectangle([92 * s, 146 * s, 164 * s, 194 * s], radius=int(14 * s), outline=white, width=int(w * 0.85))  # bolsillo
    d.line([60 * s, 122 * s, 196 * s, 122 * s], fill=white, width=int(w * 0.8))  # tapa
    return im.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    t = Image.fromarray(trade(), "RGBA").resize((N * SCALE, N * SCALE), Image.NEAREST)
    t.save(os.path.join(OUT, "pass_trade.png"))
    topbar_backpack().save(os.path.join(OUT, "topbar_backpack.png"))
    # hoja de prueba (sobre gris oscuro, como el boton)
    sheet = Image.new("RGBA", (600, 300), (40, 42, 50, 255))
    sheet.alpha_composite(t.resize((256, 256), Image.NEAREST), (20, 22))
    sheet.alpha_composite(topbar_backpack(), (320, 22))
    sheet.save(os.path.join(HERE, "preview_trade_icons.png"))
    print("ok")
