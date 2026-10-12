"""
Iconos pixel-art de la GUI de ROLL A RAT (estilo Press Start 2P).
Se dibujan a 16x16 y se agrandan con vecino mas cercano (en Roblox: ResampleMode = Pixelated).
  python make_ui_icons.py   -> ui_cheese.png, ui_sparkle.png al lado de este script
"""
import os

from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
SCALE = 16

PAL = {
    ".": (0, 0, 0, 0),
    "K": (40, 22, 6, 255),  # borde
    "L": (255, 240, 140, 255),  # cara de arriba (luz)
    "Y": (255, 204, 32, 255),  # frente
    "D": (236, 140, 18, 255),  # costado (sombra)
    "H": (196, 112, 8, 255),  # agujeros
    "W": (255, 255, 255, 255),
    "S": (255, 255, 255, 150),
}

CHEESE = """
................
................
............KK..
.........KKKLLK.
......KKKLLLLLK.
...KKKLLLLLLLLK.
.KKLLLLLLLLLLLDK
KYYYYYYYYYYYYDDK
KYYHHYYYYYYYYDDK
KYYHHYYYYYYYYDDK
KYYYYYYYYHHYYDDK
KYYYYYYYYHHYYDDK
KYHYYYYYYYYYYDDK
KYYYYYHHYYYYYDDK
KKKKKKKKKKKKKKKK
................
"""

SPARKLE = """
................
.......W........
.......W........
.......W........
......SWS.......
......WWW.......
.....SWWWS......
.WWWWWWWWWWWWW..
.....SWWWS......
......WWW.......
......SWS.......
.......W........
.......W........
.......W........
................
................
"""


def draw(name, art):
    rows = [r for r in art.strip("\n").split("\n")]
    img = Image.new("RGBA", (16, 16))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            img.putpixel((x, y), PAL[ch])
    img.resize((16 * SCALE, 16 * SCALE), Image.NEAREST).save(os.path.join(OUT, name + ".png"))


draw("ui_cheese", CHEESE)
draw("ui_sparkle", SPARKLE)
