"""
Iconos pixel-art "3D" del HUD de ROLL A RAT (32x32), estilo los iconos renderizados de la referencia.
Cada objeto se arma con formas 3D (SDF), se ilumina y se pasa a pixel-art:
  - 3x3 muestras por pixel; gana el material que mas aparece (formas limpias, sin antialias)
  - sombreado por tonos (oscuro / medio / claro / luz) + brillo especular en los materiales con brillo
  - borde de 1 pixel del color oscuro del material que toca + lineas donde una pieza tapa a otra
Se exportan a x16 (512 px: los mipmaps siguen dando bloques enteros). En Roblox: ResampleMode Pixelated y
UIKit.SnapPixels (atributo Art = 32).
  python make_ui_icons3d.py            -> ui3d_*.png al lado de este script
  python make_ui_icons3d.py preview RUTA.png   -> ademas una hoja de prueba
"""
import os
import sys

import numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
N, SS, SCALE = 32, 3, 16


# ---------------------------------------------------------------- materiales: (oscuro, medio, claro, luz), brillo
def pal(*cols, gloss=0.0):
    return {"tones": [np.array(c, float) for c in cols], "gloss": gloss}


MATS = {
    "red": pal((118, 18, 38), (196, 38, 58), (240, 76, 86), (255, 150, 150), gloss=0.7),
    "redin": pal((84, 10, 28), (140, 24, 44), (180, 40, 58), (210, 70, 80)),
    "grey": pal((70, 80, 102), (150, 160, 182), (210, 216, 232), (255, 255, 255), gloss=0.8),
    "cheese": pal((176, 96, 8), (240, 170, 20), (255, 214, 60), (255, 246, 160), gloss=0.3),
    "hole": pal((150, 76, 6), (190, 110, 10), (214, 134, 20), (230, 160, 40)),
    "book": pal((110, 16, 38), (196, 36, 58), (238, 74, 86), (255, 140, 140), gloss=0.6),
    "page": pal((180, 160, 120), (232, 216, 180), (252, 244, 222), (255, 255, 250)),
    "pageline": pal((150, 130, 96), (196, 178, 140), (214, 198, 160), (230, 214, 180)),
    "gold": pal((150, 86, 10), (226, 160, 24), (255, 212, 60), (255, 248, 190), gloss=0.9),
    "green": pal((22, 148, 52), (52, 216, 76), (128, 250, 100), (226, 255, 190), gloss=0.9),  # verde vivo (UPGRADES)
    "pack": pal((128, 40, 18), (206, 82, 38), (244, 132, 66), (255, 196, 140), gloss=0.4),
    "packdk": pal((90, 26, 14), (156, 54, 26), (194, 82, 40), (226, 120, 70), gloss=0.3),
    "strap": pal((52, 28, 18), (96, 54, 30), (134, 80, 44), (170, 110, 66)),
    "purple": pal((56, 18, 104), (116, 46, 196), (164, 96, 240), (214, 170, 255), gloss=0.6),
    "sack": pal((122, 74, 30), (196, 136, 64), (232, 186, 112), (255, 230, 176), gloss=0.2),
    "rope": pal((84, 48, 20), (140, 86, 40), (182, 124, 64), (214, 160, 96)),
    "wall": pal((176, 140, 96), (236, 210, 164), (255, 236, 196), (255, 250, 230)),
    "roof": pal((120, 22, 22), (198, 44, 40), (236, 78, 60), (255, 128, 96), gloss=0.4),
    "door": pal((80, 40, 16), (140, 78, 36), (180, 112, 56), (210, 146, 84)),
    "glass": pal((40, 110, 170), (90, 180, 240), (160, 222, 255), (240, 252, 255), gloss=1.0),
    "stone": pal((80, 80, 96), (130, 130, 146), (172, 172, 186), (206, 206, 218)),
    "wood": pal((92, 50, 22), (156, 92, 44), (198, 132, 70), (228, 170, 104), gloss=0.2),
    "white": pal((170, 160, 160), (232, 226, 224), (252, 250, 248), (255, 255, 255), gloss=0.3),
    "dollar": pal((14, 80, 30), (30, 130, 50), (60, 170, 70), (110, 210, 110)),
}
NAMES = list(MATS)
MID = {n: i for i, n in enumerate(NAMES)}


# ---------------------------------------------------------------- SDF (numpy, p: (M,3))
def length(v):
    return np.sqrt((v * v).sum(-1))


def rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def local(p, c=(0, 0, 0), R=None):
    q = p - np.array(c, float)
    return q @ R if R is not None else q  # (R: local -> mundo)


def box(p, b, r=0.0):
    q = np.abs(p) - (np.array(b, float) - r)
    return length(np.maximum(q, 0)) + np.minimum(q.max(-1), 0) - r


def sphere(p, r):
    return length(p) - r


def torus(p, R, r):  # anillo en el plano XZ
    q = np.stack([np.sqrt(p[:, 0] ** 2 + p[:, 2] ** 2) - R, p[:, 1]], -1)
    return length(q) - r


def cyl(p, h, r):  # cilindro vertical (eje Y)
    d = np.stack([np.sqrt(p[:, 0] ** 2 + p[:, 2] ** 2) - r, np.abs(p[:, 1]) - h], -1)
    return np.minimum(d.max(-1), 0) + length(np.maximum(d, 0))


def prism(p, w, h, depth):  # triangulo (base w abajo, alto h, punta arriba) extruido en Z, centrado en su base
    x, y, z = np.abs(p[:, 0]), p[:, 1], np.abs(p[:, 2])
    n = np.array([h, w / 2]) / np.hypot(h, w / 2)  # normal del lado inclinado
    side = x * n[0] + (y - h) * n[1]
    return np.maximum.reduce([side, -y, z - depth])


def wedge(p, b):  # cuna de queso: caja cortada en diagonal (punta hacia -x, alta en +x)
    d = box(p, b)
    slope = (p[:, 1] - b[1]) * b[0] * 2 - (p[:, 0] - b[0]) * b[1] * 2
    return np.maximum(d, slope / np.hypot(b[0] * 2, b[1] * 2))


class Scene:
    def __init__(self, p):
        self.p = p
        self.d = np.full(len(p), 1e9)
        self.m = np.zeros(len(p), int)

    def add(self, d, mat):
        k = d < self.d
        self.d[k] = d[k]
        self.m[k] = mat[k] if isinstance(mat, np.ndarray) else MID[mat]

    def cut(self, d):  # resta (agujeros)
        self.d = np.maximum(self.d, -d)


# ---------------------------------------------------------------- escenas
def basket(p):
    s = Scene(p)
    q = local(p, (0, -0.32, 0))
    shell = np.maximum(box(q, (0.82, 0.46, 0.56), 0.12), -box(local(q, (0, 0.18, 0)), (0.7, 0.62, 0.44), 0.08))
    holes = np.full(len(p), 1e9)
    for x in (-0.44, 0.0, 0.44):
        for y in (-0.2, 0.1):
            holes = np.minimum(holes, box(local(q, (x, y, 0.55)), (0.12, 0.09, 0.2), 0.02))
    for z in (-0.2, 0.2):
        for y in (-0.2, 0.1):
            holes = np.minimum(holes, box(local(q, (0.8, y, z)), (0.2, 0.09, 0.12), 0.02))
    shell = np.maximum(shell, -holes)
    s.add(shell, "red")
    rim = np.maximum(box(local(q, (0, 0.44, 0)), (0.88, 0.07, 0.62), 0.05), -box(local(q, (0, 0.44, 0)), (0.7, 0.2, 0.44)))
    s.add(rim, "red")
    # queso adentro, asomando
    cq = local(p, (0.12, 0.3, -0.04), ry(-0.9))
    ch = wedge(cq, (0.46, 0.34, 0.28))
    spots = np.sin(cq[:, 0] * 11 + 1) * np.sin(cq[:, 1] * 11 + 2) * np.sin(cq[:, 2] * 11) > 0.12  # agujeritos
    s.add(ch, np.where(spots, MID["hole"], MID["cheese"]))
    # manija
    hq = local(p, (0, 0.14, 0), rx(np.pi / 2))
    handle = np.maximum(torus(hq, 0.66, 0.075), -(p[:, 1] - 0.14))
    s.add(handle, "grey")
    return s


def book(p):
    s = Scene(p)
    q = local(p, (0, 0, 0), ry(-0.3) @ rz(0.06))
    lines = (np.floor((q[:, 1] + 1) * 6) % 2 == 0) & (q[:, 0] > 0.45)  # rayitas de las hojas en el canto
    s.add(box(local(q, (0.02, 0, 0)), (0.5, 0.74, 0.17), 0.02), np.where(lines, MID["pageline"], MID["page"]))
    for z in (0.2, -0.2):
        s.add(box(local(q, (0, 0, z)), (0.58, 0.8, 0.045), 0.03), "book")
    s.add(box(local(q, (-0.55, 0, 0)), (0.06, 0.8, 0.24), 0.05), "book")
    # panel en relieve + queso dorado
    s.add(box(local(q, (0.02, 0.06, 0.25)), (0.4, 0.46, 0.02), 0.03), "book")
    mq = local(q, (0.02, 0.08, 0.27), rx(np.pi / 2))  # medallon dorado con gema
    s.add(cyl(mq, 0.035, 0.24) - 0.01, "gold")
    s.add(sphere(local(q, (0.02, 0.08, 0.27)), 0.11), "glass")
    # esquineros dorados
    for y in (0.72, -0.72):
        s.add(box(local(q, (0.52, y, 0.21)), (0.09, 0.09, 0.06), 0.02), "gold")
    # cinta marcador
    s.add(box(local(q, (0.25, -0.86, 0.1)), (0.06, 0.14, 0.015)), "gold")
    return s


def arrow(p):
    s = Scene(p)
    q = local(p, (0, -0.05, 0), ry(0.2) @ rx(0.16))  # el frente mira a la luz: verde brillante, el costado hace de sombra
    shaft = box(local(q, (0, -0.42, 0)), (0.26, 0.42, 0.24), 0.1)
    head = prism(local(q, (0, -0.06, 0)), 1.16, 0.8, 0.16) - 0.09  # (bordes redondeados: los cantos toman luz)
    s.add(np.minimum(shaft, head), "green")
    # base dorada
    s.add(cyl(local(p, (0, -0.9, 0)), 0.07, 0.58) - 0.03, "gold")
    return s


def backpack(p):
    s = Scene(p)
    q = local(p, (0, -0.06, 0), ry(0.5))
    s.add(box(local(q, (0, -0.08, 0)), (0.56, 0.72, 0.36), 0.26), "pack")
    s.add(box(local(q, (0, -0.4, 0.33)), (0.4, 0.28, 0.13), 0.12), "packdk")  # bolsillo
    s.add(box(local(q, (0, 0.3, 0.3)), (0.5, 0.24, 0.12), 0.1), "packdk")  # tapa
    s.add(box(local(q, (0, 0.1, 0.42)), (0.09, 0.08, 0.05), 0.02), "gold")  # hebilla
    s.add(box(local(q, (0, -0.3, 0.46)), (0.07, 0.06, 0.04), 0.02), "gold")
    for x in (-0.36, 0.36):  # correas laterales
        s.add(box(local(q, (x, -0.1, 0.36)), (0.05, 0.6, 0.04), 0.02), "strap")
    hq = local(q, (0, 0.62, 0), rx(np.pi / 2))
    s.add(np.maximum(torus(hq, 0.2, 0.055), -(q[:, 1] - 0.62)), "strap")
    return s


def gift(p):
    s = Scene(p)
    q = local(p, (0, -0.12, 0), ry(0.62))
    s.add(box(local(q, (0, -0.32, 0)), (0.58, 0.44, 0.58), 0.05), "purple")
    s.add(box(local(q, (0, 0.18, 0)), (0.66, 0.12, 0.66), 0.05), "purple")
    s.add(box(local(q, (0, -0.32, 0)), (0.14, 0.46, 0.6), 0.02), "gold")
    s.add(box(local(q, (0, -0.32, 0)), (0.6, 0.46, 0.14), 0.02), "gold")
    s.add(box(local(q, (0, 0.18, 0)), (0.15, 0.14, 0.68), 0.02), "gold")
    s.add(box(local(q, (0, 0.18, 0)), (0.68, 0.14, 0.15), 0.02), "gold")
    for sx in (-1, 1):  # mono: dos lazos
        lq = local(q, (sx * 0.24, 0.44, 0), rz(sx * 0.5) @ rx(np.pi / 2))
        s.add(torus(lq, 0.2, 0.07), "gold")
    s.add(sphere(local(q, (0, 0.38, 0)), 0.12), "gold")
    return s


def moneybag(p):
    s = Scene(p)
    q = local(p, (0, -0.28, 0))
    qs = q * np.array([1.0, 1.15, 1.0])
    s.add(sphere(qs, 0.66) * 0.85, "sack")
    s.add(cyl(local(p, (0, 0.38, 0)), 0.1, 0.2) - 0.03, "sack")
    for a in range(5):  # punta atada (volados)
        ang = a / 5 * 2 * np.pi
        s.add(sphere(local(p, (0.18 * np.cos(ang), 0.58, 0.18 * np.sin(ang))), 0.13), "sack")
    s.add(torus(local(p, (0, 0.36, 0)), 0.22, 0.055), "rope")
    return s


def house(p):
    s = Scene(p)
    q = local(p, (0, -0.1, 0), ry(0.6))
    s.add(box(local(q, (0, -0.4, 0)), (0.56, 0.48, 0.48), 0.03), "wall")
    s.add(prism(local(q, (0, 0.06, 0)), 1.34, 0.56, 0.56) - 0.03, "roof")
    s.add(box(local(q, (0.3, 0.5, -0.15)), (0.09, 0.2, 0.09), 0.02), "stone")
    s.add(box(local(q, (-0.18, -0.58, 0.48)), (0.15, 0.3, 0.03), 0.02), "door")
    s.add(box(local(q, (0.26, -0.3, 0.48)), (0.14, 0.13, 0.02), 0.02), "glass")
    s.add(box(local(q, (0.56, -0.36, 0.0)), (0.02, 0.11, 0.13), 0.02), "glass")
    return s


def stall(p):
    s = Scene(p)
    q = local(p, (0, 0, 0), ry(0.5))
    s.add(box(local(q, (0, -0.56, 0.05)), (0.72, 0.3, 0.36), 0.04), "wood")
    for x in (-0.62, 0.62):
        s.add(cyl(local(q, (x, -0.05, -0.22)), 0.55, 0.05), "wood")
    aq = local(q, (0, 0.5, -0.02), rx(0.42))
    stripe = np.where(np.floor((aq[:, 0] + 1) * 3.0) % 2 == 0, MID["red"], MID["white"])
    s.add(box(aq, (0.86, 0.1, 0.5), 0.03), stripe)
    vq = local(q, (0, 0.2, 0.47))
    stripe2 = np.where(np.floor((vq[:, 0] + 1) * 3.0) % 2 == 0, MID["red"], MID["white"])
    s.add(box(vq, (0.86, 0.14, 0.06), 0.03), stripe2)
    for x in (-0.3, 0.26):
        s.add(wedge(local(q, (x, -0.14, 0.12), ry(0.3)), (0.22, 0.14, 0.15)), "cheese")
    return s


ICONS = {"cart": basket, "book": book, "upgrade": arrow, "backpack": backpack, "gift": gift,
         "moneybag": moneybag, "house": house, "stall": stall}


# ---------------------------------------------------------------- render
def camera(yaw=0.42, pitch=0.42):
    fwd = np.array([np.sin(yaw) * np.cos(pitch), np.sin(pitch), np.cos(yaw) * np.cos(pitch)])
    right = np.cross([0, 1, 0], fwd)
    right /= np.linalg.norm(right)
    up = np.cross(fwd, right)
    return fwd, right, up


def march(fn, cam, center, extent, res):
    fwd, right, up = cam
    u = ((np.arange(res) + 0.5) / res * 2 - 1) * extent
    uu, vv = np.meshgrid(u, -u)
    o = center + uu.reshape(-1, 1) * right + vv.reshape(-1, 1) * up + fwd * 4
    t = np.zeros(len(o))
    hit = np.zeros(len(o), bool)
    for _ in range(160):
        p = o - fwd * t[:, None]
        d = fn(p).d
        hit |= d < 1e-3
        t = np.where(hit, t, t + np.maximum(d * 0.8, 1e-3))
        if hit.all() or (t > 8).all():
            break
    hit &= t < 8
    return o, t, hit


def render(fn, yaw=0.42, pitch=0.42):
    cam = camera(yaw, pitch)
    fwd, right, up = cam
    # 1) encuadre: caja del objeto en pantalla
    o, t, hit = march(fn, cam, np.zeros(3), 1.6, 96)
    ys, xs = np.nonzero(hit.reshape(96, 96))
    u = ((np.arange(96) + 0.5) / 96 * 2 - 1) * 1.6
    cx, cy = (u[xs.min()] + u[xs.max()]) / 2, -(u[ys.min()] + u[ys.max()]) / 2
    half = max(u[xs.max()] - u[xs.min()], u[ys.max()] - u[ys.min()]) / 2 + 1.6 / 96
    extent = half * N / (N - 3)  # deja lugar para el borde
    center = right * cx + up * cy
    # 2) render final con 3x3 muestras por pixel
    R = N * SS
    o, t, hit = march(fn, cam, center, extent, R)
    p = o - fwd * t[:, None]
    sc = fn(p)
    e = 2e-3
    grad = np.stack([fn(p + np.eye(3)[i] * e).d - fn(p - np.eye(3)[i] * e).d for i in range(3)], -1)
    n = grad / (length(grad)[:, None] + 1e-9)
    light = -right * 0.5 + up * 0.72 + fwd * 0.75
    light /= np.linalg.norm(light)
    diff = np.clip((n * light).sum(-1), 0, 1)
    # oclusion barata: cuanto espacio libre hay un poquito afuera
    ao = np.clip(fn(p + n * 0.12).d / 0.12, 0, 1)
    val = 0.3 + 0.7 * diff * (0.6 + 0.4 * ao)
    tone = np.digitize(val, [0.44, 0.66, 0.9])
    h = light + fwd
    h /= np.linalg.norm(h)
    spec = np.clip((n * h).sum(-1), 0, 1) ** 36
    gloss = np.array([MATS[k]["gloss"] for k in NAMES])[sc.m]
    tone = np.where((spec * gloss > 0.45) & hit, 4, tone)
    mat = np.where(hit, sc.m, -1)
    # 3) voto por pixel
    mat = mat.reshape(N, SS, N, SS).transpose(0, 2, 1, 3).reshape(N, N, SS * SS)
    tone = tone.reshape(N, SS, N, SS).transpose(0, 2, 1, 3).reshape(N, N, SS * SS)
    depth = t.reshape(N, SS, N, SS).transpose(0, 2, 1, 3).reshape(N, N, SS * SS)
    M = np.full((N, N), -1)
    T = np.zeros((N, N), int)
    D = np.full((N, N), 99.0)
    for y in range(N):
        for x in range(N):
            vals, counts = np.unique(mat[y, x], return_counts=True)
            m = vals[counts.argmax()]
            if m < 0 and counts.max() < SS * SS * 0.67:  # medio pixel de objeto: gana el objeto (mas lleno)
                k = vals >= 0
                m = vals[k][counts[k].argmax()]
            M[y, x] = m
            if m >= 0:
                sel = mat[y, x] == m
                tv, tc = np.unique(tone[y, x][sel], return_counts=True)
                T[y, x] = tv[tc.argmax()]
                D[y, x] = depth[y, x][sel].mean()
    return M, T, D


def compose(M, T, D):
    img = np.zeros((N, N, 4), np.uint8)
    for y in range(N):
        for x in range(N):
            m = M[y, x]
            if m < 0:
                continue
            mt = MATS[NAMES[m]]["tones"]
            tn = T[y, x]
            # linea donde una pieza tapa a esta (vecino bastante mas cerca)
            behind = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < N and 0 <= yy < N and M[yy, xx] >= 0 and D[yy, xx] < D[y, x] - 0.16:
                    behind = True
            if behind:
                c = mt[0] * 0.55
            elif tn == 4:
                c = mt[3] * 0.5 + 255 * 0.5
            else:
                c = mt[min(tn, 3)]
            img[y, x] = (*np.clip(c, 0, 255).astype(np.uint8), 255)
    # borde de afuera: el oscuro del material vecino
    out = img.copy()
    for y in range(N):
        for x in range(N):
            if M[y, x] >= 0:
                continue
            best = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < N and 0 <= yy < N and M[yy, xx] >= 0:
                    if best is None or D[yy, xx] < best[1]:
                        best = (M[yy, xx], D[yy, xx])
            if best:
                c = MATS[NAMES[best[0]]]["tones"][0] * 0.42
                out[y, x] = (*np.clip(c, 0, 255).astype(np.uint8), 255)
    return out


DOLLAR = ["..#..", ".###.", "#.#..", ".###.", "..#.#", ".###.", "..#.."]


def stamp_dollar(img, M):
    ys, xs = np.nonzero(M == MID["sack"])
    cy, cx = int(round(ys.mean() + 2)), int(round(xs.mean()))
    dark, lite = MATS["dollar"]["tones"][1], MATS["dollar"]["tones"][3]
    for j, row in enumerate(DOLLAR):
        for i, ch in enumerate(row):
            if ch == "#":
                x, y = cx - 2 + i, cy - 3 + j
                img[y, x] = (*dark.astype(np.uint8), 255)
                if j in (1, 3, 5) and img[y - 1, x][1] < 140:
                    pass
    img[cy - 2, cx - 1] = (*lite.astype(np.uint8), 255)  # brillito


def bevel(img, M, name, glint=None):
    """bisel pixel a mano: borde interno claro arriba/izquierda, oscuro abajo/derecha (+ brillito opcional)"""
    m = MID[name]
    tones = MATS[name]["tones"]
    out = img.copy()
    for y in range(N):
        for x in range(N):
            if M[y, x] != m:
                continue
            edge = lambda dx, dy: not (0 <= x + dx < N and 0 <= y + dy < N) or M[y + dy, x + dx] != m
            if edge(0, -1) or edge(-1, 0):
                out[y, x] = (*tones[2].astype(np.uint8), 255)
            elif edge(0, 1) or edge(1, 0):
                out[y, x] = (*tones[0].astype(np.uint8), 255)
    if glint:
        for gx, gy in glint:
            if M[gy, gx] == m:
                out[gy, gx] = (*(tones[3] * 0.4 + 255 * 0.6).astype(np.uint8), 255)
    img[:] = out


def main():
    made = {}
    for name, fn in ICONS.items():
        M, T, D = render(fn)
        px = compose(M, T, D)
        if name == "moneybag":
            stamp_dollar(px, M)
        if name == "upgrade":
            ys, xs = np.nonzero(M == MID["green"])
            top = ys.min()
            cx = int(np.round(xs[ys == top].mean()))
            bevel(px, M, "green", glint=[(cx - 2, top + 4), (cx - 3, top + 5), (cx - 2, top + 5)])
        im = Image.fromarray(px, "RGBA")
        im.resize((N * SCALE, N * SCALE), Image.NEAREST).save(os.path.join(OUT, "ui3d_" + name + ".png"))
        made[name] = im
        print("ok", name)
    if "preview" in sys.argv:
        bgs = [(255, 160, 20), (60, 130, 255), (120, 60, 230), (40, 170, 70), (226, 50, 140), (40, 30, 70), (40, 30, 70), (40, 30, 70)]
        sheet = Image.new("RGBA", (4 * 340, 2 * 340), (30, 30, 40, 255))
        for i, (name, im) in enumerate(made.items()):
            tile = Image.new("RGBA", (320, 320), bgs[i] + (255,))
            big = im.resize((320, 320), Image.NEAREST)
            tile.alpha_composite(big)
            sheet.paste(tile, (10 + (i % 4) * 340, 10 + (i // 4) * 340))
        sheet.save(sys.argv[sys.argv.index("preview") + 1])


if __name__ == "__main__":
    main()
