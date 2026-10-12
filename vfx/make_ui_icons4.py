"""
Pixel-art 32x32 de RANKING / TRAITS / ITEMS / UPGRADES / TORRE (ROLL A RAT).
Usa el mismo render que make_ui_icons3d.py (formas 3D SDF -> pixel-art con tonos, brillo y borde) para los objetos,
y dibuja a mano (2D) los emblemas de los rangos (letras gordas con degrade, bisel, extrusion y destellos).
  python make_ui_icons4.py                  -> px4_*.png (x16 = 512 px) al lado de este script
  python make_ui_icons4.py preview RUTA.png -> ademas una hoja de prueba
En Roblox: ResampleMode Pixelated + UIKit.SnapPixels (atributo Art = 32).
"""
import os
import sys

import numpy as np
from PIL import Image

import make_ui_icons3d as B
from make_ui_icons3d import Scene, box, cyl, local, length, prism, pal, rx, ry, rz, sphere, torus, wedge

OUT = os.path.dirname(os.path.abspath(__file__))
N, SCALE = 32, 16

B.MATS.update({
    "coin": pal((150, 86, 10), (226, 160, 24), (255, 212, 60), (255, 248, 190), gloss=0.9),
    "coindk": pal((112, 60, 6), (176, 112, 14), (214, 150, 30), (240, 196, 90), gloss=0.4),
    "silver": pal((90, 96, 116), (170, 178, 198), (222, 228, 240), (255, 255, 255), gloss=0.9),
    "gem": pal((60, 14, 110), (140, 52, 226), (196, 126, 255), (242, 214, 255), gloss=1.0),
    "gemdk": pal((44, 10, 84), (100, 34, 170), (140, 70, 214), (190, 140, 250), gloss=0.8),
    "ruby": pal((110, 8, 30), (210, 24, 56), (255, 90, 110), (255, 210, 220), gloss=1.0),
    "sapph": pal((14, 40, 120), (30, 100, 220), (90, 170, 255), (220, 240, 255), gloss=1.0),
    "liqgold": pal((168, 104, 6), (246, 184, 22), (255, 226, 70), (255, 252, 190), gloss=0.7),
    "liqgreen": pal((14, 110, 40), (40, 196, 70), (120, 246, 100), (226, 255, 200), gloss=0.7),
    "cork": pal((96, 56, 26), (164, 104, 54), (204, 146, 86), (232, 186, 128)),
    "leaf": pal((20, 110, 36), (46, 176, 58), (110, 226, 84), (210, 255, 170), gloss=0.5),
    "steel": pal((70, 78, 98), (158, 168, 190), (214, 222, 238), (255, 255, 255), gloss=1.0),
    "dkpurple": pal((34, 14, 54), (70, 32, 108), (104, 56, 150), (150, 100, 200)),
    "flame": pal((176, 46, 10), (246, 110, 20), (255, 182, 40), (255, 244, 160), gloss=0.4),
    "flamered": pal((130, 16, 16), (214, 40, 30), (250, 90, 40), (255, 170, 90), gloss=0.3),
    "iron": pal((40, 44, 54), (92, 98, 114), (146, 152, 170), (220, 226, 240), gloss=0.9),
    "plate": pal((110, 14, 20), (200, 34, 40), (240, 84, 80), (255, 170, 160), gloss=0.7),
    "feather": pal((150, 156, 180), (226, 230, 246), (250, 252, 255), (255, 255, 255), gloss=0.3),
    "moon": pal((176, 132, 30), (238, 204, 84), (255, 236, 140), (255, 255, 220), gloss=0.5),
    "cap": pal((120, 12, 22), (214, 34, 44), (250, 84, 84), (255, 180, 170), gloss=0.6),
    "stem": pal((172, 146, 112), (236, 218, 184), (252, 242, 222), (255, 255, 255)),
    "shoe": pal((120, 14, 26), (214, 36, 50), (252, 86, 92), (255, 190, 190), gloss=0.6),
    "sole": pal((150, 150, 160), (226, 226, 232), (250, 250, 252), (255, 255, 255)),
    "can": pal((70, 80, 92), (138, 150, 164), (190, 200, 212), (240, 246, 255), gloss=0.8),
    "crystal": pal((70, 30, 140), (130, 80, 230), (180, 150, 255), (240, 230, 255), gloss=1.0),
    "tower": pal((176, 100, 8), (240, 172, 22), (255, 214, 64), (255, 246, 170), gloss=0.3),
    "towerdk": pal((140, 72, 6), (196, 120, 14), (222, 152, 30), (240, 186, 70)),
    "flag": pal((120, 14, 30), (216, 36, 56), (250, 90, 100), (255, 180, 180), gloss=0.3),
    "pink": pal((150, 40, 100), (236, 90, 170), (255, 150, 210), (255, 220, 240), gloss=0.5),
    "skin": pal((176, 92, 92), (236, 140, 140), (255, 182, 176), (255, 225, 220), gloss=0.2),
    "fur": pal((60, 60, 66), (120, 120, 124), (164, 164, 168), (206, 206, 210), gloss=0.2),
})
B.NAMES[:] = list(B.MATS)
B.MID.clear()
B.MID.update({n: i for i, n in enumerate(B.NAMES)})
MID, MATS = B.MID, B.MATS


def octa(p, s):
    return (np.abs(p).sum(-1) - s) * 0.57735


def ellip(p, r):
    r = np.array(r, float)
    k0 = length(p / r)
    k1 = length(p / (r * r))
    return k0 * (k0 - 1) / (k1 + 1e-9)


def cone(p, h, r1, r2):  # tronco de cono vertical: radio r1 abajo (y=-h) y r2 arriba (y=+h)
    q = np.stack([np.sqrt(p[:, 0] ** 2 + p[:, 2] ** 2), p[:, 1]], -1)
    k = (r2 - r1) / (2 * h)
    rr = r1 + (q[:, 1] + h) * k
    d1 = (q[:, 0] - rr) / np.sqrt(1 + k * k)
    return np.maximum(d1, np.abs(q[:, 1]) - h)


def capsule(p, a, b, r):
    a, b = np.array(a, float), np.array(b, float)
    pa, ba = p - a, b - a
    h = np.clip((pa @ ba) / (ba @ ba), 0, 1)
    return length(pa - h[:, None] * ba) - r


# ---------------------------------------------------------------- items
def coin_face(s, q, mat="coin"):
    """moneda parada mirando a +z (q ya en espacio de la moneda)"""
    cq = q @ rx(np.pi / 2).T  # eje de la moneda = z
    s.add(cyl(cq, 0.16, 0.86) - 0.05, mat)
    s.cut(cyl(local(cq, (0, 0.2, 0)), 0.06, 0.68))  # cara hundida
    s.cut(cyl(local(cq, (0, -0.2, 0)), 0.06, 0.68))


def roll_token(p):
    s = Scene(p)
    q = local(p, (0, 0, 0), ry(-0.35) @ rz(0.12))
    coin_face(s, q)
    # carita de rata en relieve (cabeza + orejas + hocico)
    s.add(ellip(local(q, (0, -0.1, 0.12)), (0.36, 0.3, 0.14)), "coindk")
    for sx in (-1, 1):
        s.add(ellip(local(q, (sx * 0.3, 0.26, 0.1)), (0.17, 0.17, 0.08)), "coindk")
        s.add(ellip(local(q, (sx * 0.3, 0.26, 0.15)), (0.09, 0.09, 0.06)), "pink")
    s.add(ellip(local(q, (0, -0.3, 0.24)), (0.1, 0.08, 0.06)), "pink")  # nariz
    return s


def trait_token(p):
    s = Scene(p)
    q = local(p, (0, 0.02, 0), ry(0.6))
    gq = q * np.array([1.0, 0.72, 1.0])
    s.add(octa(gq, 0.78) * 0.9, np.where(q[:, 1] > 0, MID["gem"], MID["gemdk"]))
    rq = local(p, (0, 0.0, 0), rx(0.5) @ rz(-0.25))
    s.add(torus(rq, 0.86, 0.07), "coin")
    return s


def flask(p, liquid, level=0.2):
    s = Scene(p)
    q = local(p, (0, -0.22, 0))
    body = sphere(q, 0.62)
    s.add(body, np.where(q[:, 1] < level, MID[liquid], MID["glass"]))
    s.add(cyl(local(p, (0, 0.5, 0)), 0.22, 0.2) - 0.02, "glass")
    s.add(torus(local(p, (0, 0.72, 0)), 0.2, 0.06), "glass")
    s.add(cyl(local(p, (0, 0.86, 0)), 0.14, 0.17) - 0.03, "cork")
    for (x, y, r) in ((-0.25, 0.1, 0.07), (0.18, 0.2, 0.05), (0.05, 0.32, 0.04)):  # burbujas
        s.add(sphere(local(p, (x, y - 0.22 + 0.0, 0.52)), r), "white")
    return s


def cash_potion(p):
    return flask(p, "liqgold")


def luck_potion(p):
    return flask(p, "liqgreen")


# ---------------------------------------------------------------- traits
def clover(s, q, scale=1.0, mat="leaf"):
    for a in range(4):
        ang = a * np.pi / 2 + np.pi / 4
        c = (np.cos(ang) * 0.3 * scale, np.sin(ang) * 0.3 * scale, 0)
        lq = local(q, c, rz(ang))
        s.add(ellip(lq, (0.34 * scale, 0.26 * scale, 0.1 * scale)), mat)
    s.add(sphere(q, 0.1 * scale), mat)
    s.add(capsule(q, (0, -0.05, 0), (0.18 * scale, -0.62 * scale, 0), 0.05 * scale), "leaf")


def coin_stack(s, c, n, r=0.26):
    """pila de n monedas acostadas (se ve la cara de arriba)"""
    for k in range(n):
        s.add(cyl(local(s.p, (c[0], c[1] + k * 0.11, c[2])), 0.045, r) - 0.012, "coin" if k % 2 == 0 else "coindk")


def fortune(n):
    def scene(p):
        s = Scene(p)
        q = local(p, (-0.18, 0.2, -0.1), ry(-0.3) @ rx(-0.2))
        clover(s, q, 1.0, "gold" if n == 3 else "leaf")
        stacks = {1: [(0.42, 3)], 2: [(0.2, 2), (0.62, 4)], 3: [(-0.1, 2), (0.34, 4), (0.76, 3)]}[n]
        for i, (x, h) in enumerate(stacks):
            coin_stack(s, (x, -0.7, 0.42 - i * 0.12), h)
        return s
    return scene


def heart_shape(q):
    q2 = q * np.array([1.0, 1.0, 1.0])
    x = np.abs(q2[:, 0])
    a = sphere(np.stack([x - 0.32, q2[:, 1] - 0.18, q2[:, 2]], -1), 0.42)
    b = box(local(q2, (0, -0.2, 0), rz(np.pi / 4)), (0.42, 0.42, 0.26), 0.12)
    d = np.minimum(a, b)
    return np.maximum(d, np.abs(q2[:, 2]) - 0.3)


def health(p):
    s = Scene(p)
    q = local(p, (0, 0, 0), ry(-0.42))
    s.add(heart_shape(q) - 0.03, "red")
    s.add(box(local(q, (0, 0.06, 0.3)), (0.12, 0.34, 0.06), 0.02), "white")
    s.add(box(local(q, (0, 0.06, 0.3)), (0.34, 0.12, 0.06), 0.02), "white")
    return s


def heart(p):
    s = Scene(p)
    s.add(heart_shape(local(p, (0, 0, 0), ry(-0.4))) - 0.03, "red")
    return s


def dagger(s, q):
    # hoja: prisma afilado
    bq = local(q, (0, 0.28, 0))
    blade = np.maximum(box(bq, (0.16, 0.62, 0.05)), (np.abs(bq[:, 0]) * 1.0 + (bq[:, 1] - 0.62) * 0.26))
    s.add(blade, np.where(bq[:, 0] > 0, MID["steel"], MID["silver"]))
    s.add(box(local(q, (0, -0.38, 0)), (0.36, 0.06, 0.08), 0.03), "dkpurple")  # guarda
    s.add(cyl(local(q, (0, -0.62, 0)), 0.2, 0.07), "dkpurple")  # mango
    s.add(sphere(local(q, (0, -0.86, 0)), 0.1), "ruby")


def assassin(p):
    s = Scene(p)
    dagger(s, local(p, (0, 0, 0), rz(-0.75) @ ry(0.3)))
    return s


def sword(p):
    s = Scene(p)
    q = local(p, (0, 0, 0), rz(-0.75) @ ry(0.3))
    bq = local(q, (0, 0.2, 0))
    blade = np.maximum(box(bq, (0.13, 0.74, 0.05)), (np.abs(bq[:, 0]) + (bq[:, 1] - 0.74) * 0.4))
    s.add(blade, np.where(bq[:, 0] > 0, MID["steel"], MID["silver"]))
    s.add(box(local(q, (0, -0.56, 0)), (0.34, 0.07, 0.08), 0.03), "gold")
    s.add(cyl(local(q, (0, -0.76, 0)), 0.16, 0.06), "wood")
    s.add(sphere(local(q, (0, -0.95, 0)), 0.09), "gold")
    return s


def king(p):
    s = Scene(p)
    q = local(p, (0, -0.1, 0), ry(0.3) @ rx(0.15))
    ring = np.maximum(cyl(q, 0.26, 0.74), -cyl(q, 0.6, 0.56))
    s.add(ring, "gold")
    for a in range(5):
        ang = a / 5 * 2 * np.pi + 0.3
        c = (np.cos(ang) * 0.66, 0.2, np.sin(ang) * 0.66)
        sq = local(q, c, ry(np.pi / 2 - ang))
        spike = prism(sq, 0.7, 0.62, 0.08)
        s.add(spike, "gold")
        s.add(sphere(local(q, (np.cos(ang) * 0.66, 0.86, np.sin(ang) * 0.66)), 0.11), "gold")
    for a, m in ((0.2, "ruby"), (1.4, "sapph"), (-1.0, "sapph"), (2.6, "ruby"), (-2.2, "ruby")):
        s.add(sphere(local(q, (np.cos(a) * 0.71, 0.0, np.sin(a) * 0.71)), 0.11), m)
    return s


def phoenix(p):
    s = Scene(p)
    q = local(p, (0, -0.05, 0), ry(0.0))
    s.add(ellip(local(q, (0, -0.05, 0)), (0.26, 0.36, 0.22)), "flame")
    s.add(sphere(local(q, (0, 0.38, 0.06)), 0.19), "flame")
    s.add(prism(local(q, (0, 0.34, 0.24), rx(np.pi / 2)), 0.14, 0.18, 0.05), "gold")  # pico
    s.add(sphere(local(q, (0.08, 0.44, 0.2)), 0.04), "white")
    for sx in (-1, 1):  # alas en V, con plumas de fuego
        wq = local(q, (sx * 0.42, 0.18, -0.05), rz(sx * -0.75))
        s.add(ellip(wq, (0.44, 0.17, 0.08)), np.where(np.abs(wq[:, 0]) > 0.22, MID["flamered"], MID["flame"]))
        for k in range(3):
            fq = local(q, (sx * (0.55 + k * 0.12), 0.48 + k * 0.1 - k * k * 0.04, -0.05), rz(sx * (-0.3 - k * 0.35)))
            s.add(ellip(fq, (0.08, 0.2, 0.06)), "flamered")
    for k, (x, y) in enumerate(((0, -0.5), (-0.16, -0.6), (0.16, -0.6))):  # cola
        tq = local(q, (x, y, -0.05), rz(x * 2))
        s.add(cone(tq, 0.24, 0.12, 0.0), "flamered" if k else "flame")
    s.add(prism(local(q, (0, 0.52, 0.0)), 0.16, 0.2, 0.04), "flamered")  # cresta
    return s


def mega(p):  # hongo que te hace crecer
    s = Scene(p)
    q = local(p, (0, 0, 0), ry(0.3) @ rx(0.2))
    capq = local(q, (0, 0.12, 0))
    cap = np.maximum(ellip(capq, (0.86, 0.62, 0.86)), -capq[:, 1] - 0.02)
    dots = np.zeros(len(p), bool)
    for (x, y, z, r) in ((0, 0.6, 0.1, 0.2), (0.55, 0.3, 0.35, 0.17), (-0.5, 0.32, 0.4, 0.17), (0.1, 0.36, 0.72, 0.15), (-0.2, 0.3, -0.7, 0.18)):
        dots |= length(capq - np.array([x, y, z])) < r
    s.add(cap, np.where(dots, MID["white"], MID["cap"]))
    s.add(cyl(local(q, (0, -0.3, 0)), 0.34, 0.36) - 0.06, "stem")
    for sx in (-1, 1):
        s.add(ellip(local(q, (sx * 0.13, -0.22, 0.38)), (0.05, 0.1, 0.04)), "strap")
    return s


def angelic(p):
    s = Scene(p)
    for sx in (-1, 1):
        wq = local(p, (sx * 0.46, 0.0, 0), rz(-sx * 0.55))
        band = np.floor((wq[:, 1] + 1) * 5) % 2 == 0
        s.add(ellip(wq, (0.26, 0.6, 0.1)), np.where(band, MID["white"], MID["feather"]))
        for k in range(4):
            fq = local(p, (sx * (0.3 + k * 0.17), -0.44 + k * 0.08, 0.02), rz(-sx * (0.2 + k * 0.25)))
            s.add(ellip(fq, (0.08, 0.26, 0.07)), "feather")
    hq = local(p, (0, 0.62, 0), rx(0.5))
    s.add(torus(hq, 0.34, 0.08), "gold")
    s.add(sphere(local(p, (0, -0.2, 0.12)), 0.18), "gold")
    return s


def zzz(p):
    s = Scene(p)
    q = local(p, (-0.3, -0.18, 0), ry(-0.3))
    moon = np.maximum(sphere(q, 0.62), -sphere(local(q, (0.34, 0.24, 0.1)), 0.52))
    s.add(sphere(local(p, (0.62, 0.62, 0)), 0.02), "moon")  # (encuadre: deja lugar arriba a la derecha)
    s.add(moon, "moon")
    return s


# ---------------------------------------------------------------- upgrades
def up_cash(p):
    s = Scene(p)
    cq = local(p, (-0.08, -0.12, 0.08), ry(-0.75))
    ch = wedge(cq, (0.64, 0.46, 0.38))
    spots = np.sin(cq[:, 0] * 10 + 1) * np.sin(cq[:, 1] * 10 + 2) * np.sin(cq[:, 2] * 10) > 0.14
    s.add(ch, np.where(spots, MID["hole"], MID["cheese"]))
    coin_stack(s, (0.55, -0.62, 0.5), 3, 0.24)
    coin_stack(s, (0.2, -0.62, 0.72), 2, 0.24)
    return s


def up_luck(p):  # herradura
    s = Scene(p)
    q = local(p, (0, 0.04, 0), ry(-0.3) @ rx(np.pi / 2))
    shoe = np.maximum(torus(q, 0.56, 0.17), -(q[:, 2] + 0.32))
    s.add(shoe, "gold")
    for sx in (-1, 1):
        s.add(box(local(q, (sx * 0.56, 0, -0.42)), (0.2, 0.15, 0.12), 0.05), "gold")
    for a in (-1.0, -0.5, 0.0, 0.5, 1.0, 1.6, -1.6):
        ang = a + np.pi / 2
        s.add(sphere(local(q, (np.cos(ang) * 0.56, 0.14, np.sin(ang) * 0.56)), 0.05), "steel")
    return s


def up_open(p):  # tacho con la tapa saltando
    s = Scene(p)
    q = local(p, (0, -0.2, 0), ry(0.4))
    bands = (np.floor((q[:, 1] + 1) * 5) % 2 == 0)
    s.add(cone(q, 0.56, 0.5, 0.6) - 0.02, np.where(bands, MID["can"], MID["silver"]))
    lq = local(q, (0.18, 0.86, 0), rz(-0.5))
    s.add(cyl(lq, 0.06, 0.68) - 0.02, "can")
    s.add(box(local(lq, (0, 0.12, 0)), (0.16, 0.06, 0.06), 0.03), "iron")
    return s


def up_throw(p):  # queso volando con lineas de velocidad
    s = Scene(p)
    cq = local(p, (0.22, 0.05, 0.1), ry(-0.4) @ rz(0.3))
    ch = wedge(cq, (0.52, 0.36, 0.3))
    spots = np.sin(cq[:, 0] * 11 + 1) * np.sin(cq[:, 1] * 11 + 2) * np.sin(cq[:, 2] * 11) > 0.14
    s.add(ch, np.where(spots, MID["hole"], MID["cheese"]))
    for k, (y, w) in enumerate(((0.36, 0.3), (0.0, 0.42), (-0.36, 0.26))):
        s.add(box(local(p, (-0.62 + (0.42 - w), y, 0)), (w, 0.07, 0.07), 0.03), "white")
    return s


def up_train(p):  # mancuerna
    s = Scene(p)
    q = local(p, (0, 0, 0), rz(0.45) @ ry(0.5))
    s.add(cyl(local(q, (0, 0, 0), rz(np.pi / 2)), 0.78, 0.08), "iron")
    for sx in (-1, 1):
        for k, (r, w) in enumerate(((0.46, 0.1), (0.36, 0.08))):
            s.add(cyl(local(q, (sx * (0.44 + k * 0.2), 0, 0), rz(np.pi / 2)), w, r) - 0.02, "plate")
    return s


def up_speed(p):  # zapatilla de perfil (punta a la derecha)
    s = Scene(p)
    q = local(p, (0, 0, 0), ry(np.pi / 2 + 0.42) @ rx(0.0))
    q = q @ rz(0.12).T
    s.add(box(local(q, (0, -0.4, 0.06)), (0.3, 0.09, 0.9), 0.07), "sole")  # suela (largo en z)
    s.add(ellip(local(q, (0, -0.22, 0.42)), (0.29, 0.22, 0.42)), "shoe")  # punta
    s.add(box(local(q, (0, -0.02, -0.4)), (0.28, 0.36, 0.34), 0.14), "shoe")  # talon alto
    s.add(box(local(q, (0, -0.1, 0.0)), (0.28, 0.24, 0.36), 0.12), "shoe")
    s.add(box(local(q, (0, 0.33, -0.48)), (0.3, 0.06, 0.24), 0.04), "white")  # cuello
    for k in range(3):
        s.add(box(local(q, (0, 0.18 - k * 0.1, -0.12 + k * 0.16), rx(0.5)), (0.3, 0.03, 0.05), 0.01), "white")
    s.add(box(local(q, (0.3, -0.2, -0.05)), (0.02, 0.06, 0.4), 0.02), "white")  # raya
    return s


# ---------------------------------------------------------------- ventanas / varios
def trophy(p):
    s = Scene(p)
    q = local(p, (0, 0, 0), ry(0.3))
    cup = np.maximum(sphere(local(q, (0, 0.36, 0)), 0.56), q[:, 1] - 0.62)
    cup = np.maximum(cup, -sphere(local(q, (0, 0.5, 0)), 0.44))
    s.add(cup, "gold")
    for sx in (-1, 1):
        hq = local(q, (sx * 0.56, 0.36, 0), rx(np.pi / 2))
        s.add(np.maximum(torus(hq, 0.2, 0.06), -sx * (q[:, 0] - sx * 0.5)), "gold")
    s.add(cyl(local(q, (0, -0.32, 0)), 0.16, 0.09), "gold")
    s.add(box(local(q, (0, -0.62, 0)), (0.42, 0.14, 0.3), 0.04), "wood")
    s.add(box(local(q, (0, -0.44, 0)), (0.3, 0.06, 0.22), 0.03), "gold")
    s.add(sphere(local(q, (0, 0.3, 0.5)), 0.12), "ruby")
    return s


def crystal_ball(p):
    s = Scene(p)
    q = local(p, (0, 0, 0))
    ball = sphere(local(q, (0, 0.2, 0)), 0.64)
    swirl = np.sin(q[:, 0] * 7 + q[:, 1] * 5) > 0.5
    s.add(ball, np.where(swirl, MID["pink"], MID["crystal"]))
    s.add(cone(local(q, (0, -0.6, 0)), 0.18, 0.56, 0.4) - 0.02, "gold")
    s.add(torus(local(q, (0, -0.4, 0)), 0.42, 0.07), "gold")
    return s


def tower(p):
    s = Scene(p)
    q = local(p, (0, -0.1, 0), ry(0.6))
    for k, (y, w) in enumerate(((-0.62, 0.5), (-0.18, 0.42), (0.24, 0.34))):
        tq = local(q, (0, y, 0))
        holes = np.sin(tq[:, 0] * 12 + k) * np.sin(tq[:, 1] * 12) * np.sin(tq[:, 2] * 12 + k * 2) > 0.18
        s.add(box(tq, (w, 0.22, w), 0.04), np.where(holes, MID["towerdk"], MID["tower"]))
        s.add(box(local(q, (0, y + 0.24, 0)), (w + 0.05, 0.04, w + 0.05), 0.02), "towerdk")
    s.add(cyl(local(q, (0, 0.72, 0)), 0.32, 0.03), "wood")
    s.add(box(local(q, (0.16, 0.9, 0)), (0.16, 0.1, 0.02)), "flag")
    s.add(box(local(q, (0, -0.68, 0.5)), (0.12, 0.16, 0.02), 0.02), "door")
    return s


def gear(p):
    s = Scene(p)
    q = local(p, (0, 0, 0), rx(np.pi / 2 - 0.5) @ rz(0.0))
    q = q @ ry(0.3).T
    g = cyl(q, 0.16, 0.58)
    for a in range(8):
        ang = a / 8 * 2 * np.pi
        tq = local(q, (np.cos(ang) * 0.68, 0, np.sin(ang) * 0.68), ry(-ang))
        g = np.minimum(g, box(tq, (0.16, 0.16, 0.14), 0.03))
    g = np.maximum(g, -cyl(q, 0.4, 0.22))
    s.add(g - 0.02, "steel")
    return s


def lock(p):
    s = Scene(p)
    q = local(p, (0, -0.1, 0), ry(0.4))
    s.add(box(local(q, (0, -0.26, 0)), (0.52, 0.42, 0.26), 0.1), "gold")
    sq = local(q, (0, 0.18, 0), rx(np.pi / 2))
    s.add(np.maximum(torus(sq, 0.32, 0.09), -(q[:, 1] - 0.16)), "steel")
    for sx in (-1, 1):
        s.add(cyl(local(q, (sx * 0.32, 0.12, 0)), 0.1, 0.09), "steel")
    s.add(cyl(local(q, (0, -0.2, 0.26), rx(np.pi / 2)), 0.04, 0.09), "strap")
    s.add(box(local(q, (0, -0.36, 0.27)), (0.04, 0.1, 0.02)), "strap")
    return s


ICONS3D = {
    "roll_token": roll_token, "trait_token": trait_token, "cash_potion": cash_potion, "luck_potion": luck_potion,
    "trait_fortune1": fortune(1), "trait_fortune2": fortune(2), "trait_fortune3": fortune(3),
    "trait_health": health, "trait_assassin": assassin, "trait_king": king, "trait_phoenix": phoenix,
    "trait_mega": mega, "trait_angelic": angelic, "trait_zzz": zzz,
    "up_cash": up_cash, "up_luck": up_luck, "up_open": up_open, "up_throw": up_throw, "up_train": up_train, "up_speed": up_speed,
    "trophy": trophy, "crystal_ball": crystal_ball, "tower": tower, "gear": gear, "lock": lock, "sword": sword, "heart": heart,
}


# ---------------------------------------------------------------- estampados post-render
def stamp(img, pattern, x0, y0, color, outline=None):
    rows = pattern.strip("\n").split("\n")
    pts = [(x0 + i, y0 + j) for j, r in enumerate(rows) for i, c in enumerate(r) if c == "#"]
    if outline is not None:
        for x, y in pts:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < N and 0 <= yy < N and (xx, yy) not in pts:
                        img[yy, xx] = (*outline, 255)
    for x, y in pts:
        if 0 <= x < N and 0 <= y < N:
            img[y, x] = (*color, 255)


DOLLAR = """
.#.
###
#..
###
..#
###
.#.
"""
CLOVER = """
.#.#.
#####
.###.
#####
.#.#.
..#..
"""
Z_BIG = """
#####
...#.
..#..
.#...
#####
"""
Z_SMALL = """
###
.#.
###
"""


def mass_center(M, mat):
    ys, xs = np.nonzero(M == MID[mat])
    return int(round(xs.mean())), int(round(ys.mean()))


def post(name, img, M):
    if name == "cash_potion":
        cx, cy = mass_center(M, "liqgold")
        stamp(img, DOLLAR, cx - 1, cy - 2, (120, 70, 0))
    elif name == "luck_potion":
        cx, cy = mass_center(M, "liqgreen")
        stamp(img, CLOVER, cx - 2, cy - 2, (230, 255, 200), outline=(14, 90, 30))
    elif name == "trait_zzz":
        stamp(img, Z_BIG, 23, 2, (200, 160, 255), outline=(40, 16, 80))
        stamp(img, Z_SMALL, 19, 10, (236, 220, 255), outline=(40, 16, 80))
        for x, y in ((27, 14), (4, 4), (26, 26)):
            img[y, x] = (255, 255, 220, 255)


# ---------------------------------------------------------------- emblemas de rango (2D)
GLYPH = {
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "W": [".###.", "#...#", "#...#", "#...#", ".#.#.", ".#.#.", "##.##"],  # Omega
}


def glyph_mask(ch, sx, sy):
    g = GLYPH[ch]
    h, w = len(g), len(g[0])
    m = np.zeros((h, w + 1), bool)
    for y, row in enumerate(g):
        for x, c in enumerate(row):
            if c == "#":
                m[y, x] = m[y, x + 1] = True  # negrita: cada pixel tambien a la derecha
    return np.kron(m, np.ones((sy, sx), bool))


def lerp(a, b, t):
    return np.array(a, float) * (1 - t) + np.array(b, float) * t


def grad_color(cols, t):
    t = np.clip(t, 0, 1) * (len(cols) - 1)
    i = min(int(t), len(cols) - 2)
    return lerp(cols[i], cols[i + 1], t - i)


RANKS = [  # id, glifos, colores (arriba -> abajo), rainbow
    ("F", "F", [(220, 220, 230), (150, 150, 165), (96, 96, 112)]),
    ("E", "E", [(200, 255, 170), (110, 215, 90), (50, 140, 44)]),
    ("D", "D", [(180, 230, 255), (60, 170, 255), (24, 90, 200)]),
    ("C", "C", [(236, 196, 255), (190, 90, 255), (110, 36, 190)]),
    ("B", "B", [(255, 246, 170), (255, 205, 40), (210, 130, 10)]),
    ("A", "A", [(255, 220, 160), (255, 130, 40), (200, 60, 10)]),
    ("S", "S", [(255, 190, 190), (255, 50, 70), (170, 10, 40)]),
    ("SS", "SS", [(255, 170, 230), (255, 60, 150), (180, 20, 80)]),
    ("SSS", "SSS", [(255, 255, 220), (255, 206, 40), (230, 120, 10)]),
    ("X", "X", [(190, 255, 245), (0, 230, 210), (30, 100, 240)]),
    ("EX", "EX", [(255, 200, 250), (190, 80, 255), (60, 170, 255)]),
    ("OMEGA", "W", None),
]


def rank_emblem(letters, cols):
    n = len(letters)
    sx, sy = (3, 3) if n == 1 else (2, 3) if n == 2 else (2, 2)
    masks = [glyph_mask(c, sx, sy) for c in letters]
    gh, gw = masks[0].shape
    step = gw + 2 if n == 2 else (gw - 3 if n == 3 else gw)
    total_w = step * (n - 1) + gw
    canvas = np.zeros((N, N), int) - 1  # -1 vacio, k = letra k (las de adelante pisan)
    ox = (N - total_w) // 2 - 1
    oy = (N - gh) // 2 - 1
    for k in range(n - 1, -1, -1) if n == 3 else range(n):
        m = masks[k]
        for y in range(gh):
            for x in range(gw):
                if m[y, x]:
                    canvas[oy + y, ox + k * step + x] = k
    img = np.zeros((N, N, 4), np.uint8)
    fill = canvas >= 0
    ys, xs = np.nonzero(fill)
    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()
    dark = np.array(cols[-1], float) * 0.32 if cols else np.array((40, 20, 60), float)
    # extrusion (abajo a la derecha, 2 px) y borde negro
    ext = np.zeros_like(fill)
    for d in (1, 2):
        ext[d:, d:] |= fill[:-d, :-d]
    ext &= ~fill
    out = np.zeros_like(fill)
    solid = fill | ext
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            out |= np.roll(np.roll(solid, dy, 0), dx, 1)
    out &= ~solid
    img[out] = (14, 12, 20, 255)
    for y, x in zip(*np.nonzero(ext)):
        c = np.array(grad_color(cols, 1.0) if cols else (90, 40, 140)) * 0.45
        img[y, x] = (*np.clip(c, 0, 255).astype(np.uint8), 255)
    for y, x in zip(*np.nonzero(fill)):
        t = (y - y0) / max(1, y1 - y0)
        if cols:
            c = grad_color(cols, t)
        else:  # arcoiris en diagonal
            h = ((x - x0) / max(1, x1 - x0) * 0.8 + t * 0.35) % 1.0
            import colorsys
            r, g, b = colorsys.hsv_to_rgb(h, 0.78, 1.0)
            c = np.array((r, g, b)) * 255 * (1.05 - 0.25 * t)
        # bisel: arriba/izquierda claro, abajo/derecha oscuro (por letra)
        k = canvas[y, x]
        up = y == 0 or canvas[y - 1, x] != k
        lf = x == 0 or canvas[y, x - 1] != k
        dn = y == N - 1 or canvas[y + 1, x] != k
        rt = x == N - 1 or canvas[y, x + 1] != k
        if up or lf:
            c = c * 0.45 + 255 * 0.55
        elif dn or rt:
            c = c * 0.72
        img[y, x] = (*np.clip(c, 0, 255).astype(np.uint8), 255)
    # separacion entre letras superpuestas (SSS): borde oscuro donde una pisa a otra
    for y, x in zip(*np.nonzero(fill)):
        k = canvas[y, x]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = x + dx, y + dy
            if 0 <= xx < N and 0 <= yy < N and canvas[yy, xx] >= 0 and canvas[yy, xx] < k and n == 3:
                img[yy, xx] = (14, 12, 20, 255)
    return img


def sparkle(img, x, y, big=False, color=(255, 255, 255)):
    pts = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if big:
        pts += [(2, 0), (-2, 0), (0, 2), (0, -2)]
    for dx, dy in pts:
        xx, yy = x + dx, y + dy
        if 0 <= xx < N and 0 <= yy < N and img[yy, xx, 3] == 0:
            img[yy, xx] = (*color, 255)


def check_icon():
    img = np.zeros((N, N, 4), np.uint8)
    pts = [(6 + i, 16 + i) for i in range(6)] + [(11 + i, 21 - i) for i in range(14)]
    fill = np.zeros((N, N), bool)
    for x, y in pts:
        for dx in range(-2, 2):
            for dy in range(-2, 2):
                fill[y + dy, x + dx] = True
    out = np.zeros_like(fill)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            out |= np.roll(np.roll(fill, dy, 0), dx, 1)
    out &= ~fill
    img[out] = (14, 60, 20, 255)
    for y, x in zip(*np.nonzero(fill)):
        hi = not fill[y - 1, x]
        img[y, x] = (190, 255, 160, 255) if hi else (60, 220, 70, 255)
    return img


# ---------------------------------------------------------------- main
def main():
    made = {}
    only = [a for a in sys.argv[1:] if a in ICONS3D or a.startswith("rank_")]
    for name, fn in ICONS3D.items():
        if only and name not in only:
            continue
        M, T, D = B.render(fn)
        px = B.compose(M, T, D)
        post(name, px, M)
        made[name] = px
        print("ok", name)
    for rid, letters, cols in RANKS:
        name = "rank_" + rid
        if only and name not in only:
            continue
        img = rank_emblem(letters, cols)
        if rid in ("SSS", "X", "EX", "OMEGA"):
            sparkle(img, 3, 4, big=rid in ("EX", "OMEGA"))
            sparkle(img, 28, 27)
            if rid == "OMEGA":
                sparkle(img, 28, 5, big=True, color=(255, 240, 160))
                sparkle(img, 4, 27, color=(200, 240, 255))
        made[name] = img
        print("ok", name)
    if not only:
        made["check"] = check_icon()
    for name, px in made.items():
        Image.fromarray(px, "RGBA").resize((N * SCALE, N * SCALE), Image.NEAREST).save(os.path.join(OUT, "px4_" + name + ".png"))
    if "preview" in sys.argv:
        cols = 8
        rows = (len(made) + cols - 1) // cols
        T = 200
        sheet = Image.new("RGBA", (cols * (T + 10) + 10, rows * (T + 10) + 10), (36, 28, 60, 255))
        for i, (name, px) in enumerate(made.items()):
            tile = Image.new("RGBA", (T, T), (56, 44, 92, 255))
            tile.alpha_composite(Image.fromarray(px, "RGBA").resize((T, T), Image.NEAREST))
            sheet.paste(tile, (10 + (i % cols) * (T + 10), 10 + (i // cols) * (T + 10)))
        sheet.save(sys.argv[sys.argv.index("preview") + 1])


if __name__ == "__main__":
    main()
