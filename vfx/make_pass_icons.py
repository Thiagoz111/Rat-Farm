"""
Pixel-art 32x32 de los GAMEPASSES / PRODUCTOS de la tienda y del cartel de ofertas de la derecha (ROLL A RAT).
Mismo render que make_ui_icons4.py (formas 3D SDF -> pixel-art con tonos, brillo y borde) + borde NEGRO de
make_outline.py, como todos los iconos del juego.
  VIP        corona dorada a mano: 3 puntas facetadas con perlas, puntas de atras, aro con rubi / zafiro / esmeralda
  luck4      trebol MORADO (x4 Luck): hojas violeta, gema dorada al centro, tallo dorado, destellos
  cash2      dos fajos de billetes con faja dorada ("lingotes" de plata) cruzados + monedas
  jackpot    dado ARCOIRIS isometrico (franjas que atraviesan el dado, puntos 1/2/3) -> jackpot_x1 / x5 / x10 (cartelito)
  auto       engranaje dorado + flecha verde en circulo (Auto Conveyor)
  fast       cronometro rojo + rayo amarillo (Fast Open)
  trait_x10 / rank_x10   las fichas que ya existen con cartelito x10
  robux      icono de Robux 16x16 blanco con borde negro (se tine con ImageColor3) para los precios
  python make_pass_icons.py                 -> pass_*.png (x16) en vfx/outlined/
  python make_pass_icons.py preview RUTA    -> ademas una hoja de prueba
En Roblox: ResampleMode Pixelated + UIKit.SnapPixels (atributo Art = 32; robux Art = 16).
"""
import colorsys
import os
import sys

import numpy as np
from PIL import Image

import make_ui_icons4 as I4
from make_ui_icons3d import Scene, box, cyl, local, length, pal, prism, rx, ry, rz, sphere, torus
from make_outline import outline

B = I4.B
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outlined")
N, SCALE = 32, 16
ellip, octa, capsule = I4.ellip, I4.octa, I4.capsule

B.MATS.update({
    "diamond": pal((40, 120, 180), (110, 210, 250), (190, 245, 255), (255, 255, 255), gloss=1.0),
    "diamondlt": pal((70, 160, 210), (160, 235, 255), (220, 252, 255), (255, 255, 255), gloss=1.0),
    "emerald": pal((10, 90, 50), (30, 180, 90), (90, 240, 150), (210, 255, 230), gloss=1.0),
    "orange": pal((150, 60, 6), (250, 130, 20), (255, 186, 70), (255, 236, 180), gloss=1.0),
    "pearl": pal((170, 150, 170), (240, 232, 244), (255, 252, 255), (255, 255, 255), gloss=0.8),
    "velvet": pal((90, 10, 30), (170, 24, 56), (214, 50, 84), (240, 110, 140), gloss=0.2),
    "cash": pal((22, 96, 40), (58, 168, 64), (112, 214, 96), (196, 250, 170), gloss=0.2),
    "cashpale": pal((120, 170, 110), (196, 236, 176), (226, 250, 210), (245, 255, 240)),
    "band": pal((150, 86, 10), (232, 168, 28), (255, 214, 64), (255, 248, 190), gloss=0.7),
})
B.NAMES[:] = list(B.MATS)
B.MID.clear()
B.MID.update({n: i for i, n in enumerate(B.NAMES)})
MID = B.MID


# ---------------------------------------------------------------- piezas
def coin_flat(s, c, r=0.26, tilt=None, mat="coin"):
    q = local(s.p, c, tilt)
    s.add(cyl(q, 0.05, r) - 0.015, mat)


# ---------------------------------------------------------------- escenas
def cash_brick(s, c, R, band=True):
    q = local(s.p, c, R)
    b = (0.74, 0.17, 0.4)
    d = box(q, b, 0.03)
    # cantos de los billetes: rayitas en los costados (claro / verde)
    sheet = (np.floor((q[:, 1] + 0.2) * 22).astype(int) % 2 == 0)
    side = np.abs(q[:, 1]) < b[1] - 0.035
    mat = np.where(side & sheet, MID["cashpale"], MID["cash"])
    s.add(d, mat)
    if band:
        s.add(box(q, (0.15, b[1] + 0.025, b[2] + 0.025), 0.01), "band")


def cash2(p):
    s = Scene(p)
    cash_brick(s, (0, -0.22, 0), ry(0.1))
    cash_brick(s, (0.02, 0.15, 0.0), ry(-0.5))
    return s


# ---------------------------------------------------------------- dibujo 2D a mano (fajos x2)
YY, XX = np.mgrid[0:N, 0:N] + 0.5


def poly(pts):
    """mascara de un poligono (centro de cada pixel adentro)"""
    pts = np.array(pts, float)
    inside = np.zeros((N, N), bool)
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        cond = ((yi > YY) != (yj > YY)) & (XX < (xj - xi) * (YY - yi) / (yj - yi + 1e-9) + xi)
        inside ^= cond
        j = i
    return inside


def disc(cx, cy, r):
    return (XX - cx) ** 2 + (YY - cy) ** 2 <= r * r


# tonos 2D: (sombra, base, luz, brillo)
T2 = {
    "gold": ((196, 112, 14), (250, 186, 34), (255, 226, 96), (255, 250, 200)),
    "golddk": ((150, 76, 8), (206, 130, 18), (236, 168, 36), (255, 214, 110)),
    "ruby": ((140, 10, 36), (220, 30, 60), (255, 96, 116), (255, 214, 220)),
    "sapph": ((20, 50, 150), (40, 110, 230), (100, 180, 255), (220, 240, 255)),
    "emerald": ((10, 110, 56), (30, 190, 96), (100, 240, 150), (220, 255, 230)),
    "pearl": ((190, 176, 196), (240, 234, 246), (255, 255, 255), (255, 255, 255)),
    "dia": ((60, 150, 210), (140, 224, 255), (206, 248, 255), (255, 255, 255)),
    "diadk": ((40, 110, 180), (90, 180, 240), (150, 220, 255), (220, 248, 255)),
    "cash": ((34, 120, 46), (70, 180, 70), (126, 222, 104), (200, 250, 170)),
    "cashdk": ((22, 84, 34), (44, 136, 52), (70, 170, 70), (110, 210, 100)),
    "pale": ((150, 200, 130), (206, 240, 186), (232, 252, 220), (250, 255, 245)),
    "line": ((28, 100, 40), (40, 128, 50), (40, 128, 50), (40, 128, 50)),
}


def paint2d(layers, shade=True):
    """layers = [(mascara, tono)] de atras hacia adelante. Cada pieza: luz arriba-izquierda, sombra abajo-derecha"""
    img = np.zeros((N, N, 4), np.uint8)
    owner = np.full((N, N), -1)
    for k, (m, _) in enumerate(layers):
        owner[m] = k
    for y in range(N):
        for x in range(N):
            k = owner[y, x]
            if k < 0:
                continue
            tones = T2[layers[k][1]]
            same = lambda dx, dy: 0 <= x + dx < N and 0 <= y + dy < N and owner[y + dy, x + dx] == k
            c = tones[1]
            if shade:
                if not same(1, 1) or not same(0, 1):
                    c = tones[0]
                elif not same(-1, -1) or not same(0, -1):
                    c = tones[2]
            img[y, x] = (*c, 255)
    # linea oscura donde una pieza de adelante tapa a otra (separa las piezas)
    for y in range(N):
        for x in range(N):
            k = owner[y, x]
            if k < 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < N and 0 <= yy < N and owner[yy, xx] > k and layers[owner[yy, xx]][1] != layers[k][1]:
                    img[y, x] = (*(np.array(T2[layers[k][1]][0]) * 0.55).astype(np.uint8), 255)
                    break
    return img, owner


def put(img, pts, col):
    for x, y in pts:
        if 0 <= x < N and 0 <= y < N:
            img[y, x] = (*col, 255)


# ---------------------------------------------------------------- corona VIP, dado arcoiris, engranaje auto, reloj rapido (a mano)
GOLD = [(104, 36, 12), (178, 82, 14), (230, 136, 20), (255, 188, 36), (255, 222, 80), (255, 246, 170), (255, 255, 246)]
PEARL = [(120, 104, 156), (198, 190, 226), (240, 238, 252), (255, 255, 255)]
GEMS = {
    "ruby": [(92, 6, 30), (178, 18, 52), (234, 46, 72), (255, 120, 130), (255, 230, 232)],
    "sapph": [(14, 30, 110), (30, 80, 200), (60, 140, 250), (140, 200, 255), (236, 246, 255)],
    "emer": [(6, 74, 40), (16, 146, 72), (40, 206, 110), (130, 250, 170), (230, 255, 238)],
}


def ell(cx, cy, rx, ry):
    return ((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2 <= 1


def shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = m[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
    return out


def gem(img, cx, cy, rx, ry, T):
    """cabujon: borde oscuro, luz arriba-izquierda, brillo blanco, reflejo abajo-derecha"""
    m = ell(cx, cy, rx, ry)
    ys, xs = np.where(m)
    for y, x in zip(ys, xs):
        inner = all(m[y + dy, x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        u, v = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
        c = T[0] if not inner else T[3] if u + v < -0.6 else T[2] if u + v < 0.6 else T[1]
        img[y, x] = (*c, 255)
    sx, sy = int(cx - rx * 0.4), int(cy - ry * 0.4)
    img[sy, sx] = (*T[4], 255)
    if rx > 3:
        img[sy, sx + 1] = (*T[4], 255)
    bx, by = int(cx + rx * 0.35), int(cy + ry * 0.35)
    if m[by, bx] and m[by + 1, bx] and m[by, bx + 1]:
        img[by, bx] = (*T[3], 255)


def star(img, x, y, size, col=(255, 255, 255), tip=(255, 236, 140)):
    """destello de 4 puntas (sin borde): centro blanco y puntas de color"""
    pts = [(0, 0, col)]
    for i in range(1, size + 1):
        c = col if i == 1 else tip
        pts += [(i, 0, c), (-i, 0, c), (0, i, c), (0, -i, c)]
    for dx, dy, c in pts:
        xx, yy = x + dx, y + dy
        if 0 <= xx < N and 0 <= yy < N and img[yy, xx, 3] == 0:
            img[yy, xx] = (*c, 255)


# ---------------------------------------------------------------- corona
def crown():
    img = np.zeros((N, N, 4), np.uint8)
    own = np.full((N, N), -1)
    cx = 15.5
    arc = lambda y0, dip: y0 + dip * (1 - ((XX - cx) / 13.5) ** 2)
    band = (XX > 2) & (XX < 29) & (YY > arc(17.6, 2.2)) & (YY < arc(27.6, 2.2))
    pieces = [
        ("back", poly([(6, 20), (9.5, 10), (13, 20)])),
        ("back", poly([(18, 20), (21.5, 10), (25, 20)])),
        ("pt", poly([(2.4, 22), (2.2, 9.5), (7.2, 9.5), (12.6, 22)])),
        ("pt", poly([(18.4, 22), (23.8, 9.5), (28.8, 9.5), (28.6, 22)])),
        ("pt", poly([(9, 22), (13.2, 7), (17.8, 7), (22, 22)])),
        ("band", band),
        ("orb", ell(15.5, 4.4, 3.9, 3.9), (15.5, 4.4, 3.9)),
        ("orb", ell(4.7, 7.6, 3.5, 3.5), (4.7, 7.6, 3.5)),
        ("orb", ell(26.3, 7.6, 3.5, 3.5), (26.3, 7.6, 3.5)),
    ]
    for k, p in enumerate(pieces):
        own[p[1]] = k
    for y in range(N):
        for x in range(N):
            k = own[y, x]
            if k < 0:
                continue
            kind = pieces[k][0]
            if kind in ("back", "pt"):
                xs = np.where(pieces[k][1][y])[0]
                mid = (xs.min() + xs.max()) / 2
                if kind == "back":
                    t = 2 if x < mid else 1
                else:
                    if abs(x - mid) < 0.6:
                        t = 6 if y < 13 else 5
                    elif x < mid:
                        t = 5 if x <= xs.min() + 1 else 4
                    else:
                        t = 3 if x < xs.max() - 1 else 2
                    if y >= 19:
                        t -= 1
                c = GOLD[t]
            elif kind == "band":
                col = np.where(band[:, x])[0]
                r = y - col.min()
                h = col.max() - col.min()
                n = (x + 0.5 - cx) / 13.5
                face = 4 if -0.8 < n < -0.1 else 3 if n < 0.4 else 2 if n < 0.78 else 1
                if r == 1:
                    t = min(face + 2, 6) if -0.7 < n < -0.2 else min(face + 1, 5)
                elif r == 2 or r == h - 1:
                    t = max(face - 2, 0)
                else:
                    t = face
                c = GOLD[t]
            else:  # perla
                ox, oy, rr = pieces[k][2]
                d = np.hypot(x + 0.5 - (ox - rr * 0.35), y + 0.5 - (oy - rr * 0.35)) / rr
                c = PEARL[3] if d < 0.3 else PEARL[2] if d < 0.7 else PEARL[1] if d < 1.1 else PEARL[0]
            img[y, x] = (*c, 255)
    # costura oscura donde una pieza tapa a otra
    for y in range(N):
        for x in range(N):
            k = own[y, x]
            if k < 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < N and 0 <= yy < N and own[yy, xx] > k:
                    img[y, x] = (*GOLD[0], 255)
                    break
    # joyas: rubi grande al centro del aro, zafiro / esmeralda a los costados, zafiro en la punta del medio
    for gx, rx, ry, g in ((15.5, 3.7, 3.0, "ruby"), (7.8, 2.5, 2.5, "sapph"), (23.2, 2.5, 2.5, "emer")):
        col = np.where(band[:, int(gx)])[0]
        gem(img, gx, (col.min() + col.max()) / 2 + 1.0, rx, ry, GEMS[g])
    gem(img, 15.5, 14.0, 2.1, 2.7, GEMS["sapph"])
    # remaches del aro
    for x in (11, 20):
        col = np.where(band[:, x])[0]
        y = int((col.min() + col.max()) / 2 + 1)
        img[y, x] = (*GOLD[6], 255)
        img[y + 1, x] = (*GOLD[1], 255)
    return img


# ---------------------------------------------------------------- dado arcoiris (isometrico)
RAINBOW = [  # (oscuro, medio, claro, palido)
    ((150, 14, 52), (232, 38, 66), (255, 96, 96), (255, 186, 176)),
    ((176, 58, 10), (250, 122, 24), (255, 172, 60), (255, 218, 146)),
    ((182, 122, 0), (250, 200, 20), (255, 236, 80), (255, 250, 186)),
    ((14, 118, 62), (40, 196, 84), (120, 240, 110), (204, 255, 184)),
    ((20, 60, 172), (40, 132, 240), (92, 192, 255), (184, 232, 255)),
    ((82, 20, 152), (150, 52, 232), (202, 112, 255), (232, 194, 255)),
]
PIP = [(92, 64, 140), (214, 214, 236), (255, 255, 255)]


def die(top=(16, 2), w=13, h=6.5, H=14.5):
    T = np.array(top, float)
    R, L = T + (w, h), T + (-w, h)
    Bm = T + (0, 2 * h)
    D = np.array((0, H))
    faces = {
        "top": poly([T, R, Bm, L]),
        "left": poly([L, Bm, Bm + D, L + D]),
        "right": poly([Bm, R, R + D, Bm + D]),
    }
    img = np.zeros((N, N, 4), np.uint8)
    face_of = np.full((N, N), "", object)
    for k in ("left", "right", "top"):
        face_of[faces[k]] = k
    # esquinas redondeadas (el borde negro termina de redondearlas)
    for V in (T, R, L, R + D, L + D, Bm + D):
        cut = np.hypot(XX - V[0], YY - V[1]) < 1.7
        face_of[cut] = ""
    tone = {"top": 2, "left": 1, "right": 0}

    def uv(k, P):
        if k == "top":  # P = T + u*(R-T) + v*(L-T)
            A = np.array([R - T, L - T]).T
            u, v = np.linalg.solve(A, P - T)
            return u, v, (u, v, 0.0)  # (X, Z, Y)
        if k == "left":  # P = L + u*(Bm-L) + v*D
            A = np.array([Bm - L, D]).T
            u, v = np.linalg.solve(A, P - L)
            return u, v, (u, 1.0, v)
        A = np.array([R - Bm, D]).T  # right
        u, v = np.linalg.solve(A, P - Bm)
        return u, v, (1.0, 1 - u, v)

    for y in range(N):
        for x in range(N):
            k = face_of[y, x]
            if not k:
                continue
            u, v, (X, Z, Y) = uv(k, np.array((x + 0.5, y + 0.5)))
            s = 0.3 * (X + Z) + 0.4 * Y  # franjas = planos en diagonal que atraviesan el dado
            band = int(np.clip(s * 6, 0, 5.999))
            t = tone[k]
            # cantos redondeados: luz en los bordes de adelante de la tapa y en la arista vertical
            if k == "top" and (u > 0.86 or v > 0.86):
                t = 3
            if k == "left" and u > 0.9:
                t = 2
            img[y, x] = (*RAINBOW[band][t], 255)
    # puntos del dado (hoyuelos: borde de arriba en sombra): 1 en la tapa, 2 a la izquierda, 3 a la derecha
    SPR = {
        "top": [".SSS.", "SWWWW", "WWWWW", ".WWW."],
        "left": ["SS..", "SWW.", ".WWW", "..WW"],
        "right": [".SS", "SWW", "WWW", "WW."],
    }
    COL = {"S": PIP[0], "W": PIP[2], "G": PIP[1]}
    E = {"top": (T, R - T, L - T), "left": (L, Bm - L, D), "right": (Bm, R - Bm, D)}
    spots = {"top": [(0.5, 0.5)], "left": [(0.27, 0.3), (0.73, 0.72)], "right": [(0.22, 0.26), (0.5, 0.5), (0.78, 0.74)]}
    for k, lst in spots.items():
        o, e1, e2 = E[k]
        rows = SPR[k]
        for u, v in lst:
            P = o + u * e1 + v * e2
            x0, y0 = int(round(P[0] - len(rows[0]) / 2)), int(round(P[1] - len(rows) / 2))
            for j, row in enumerate(rows):
                for i, ch in enumerate(row):
                    if ch != "." and face_of[y0 + j, x0 + i] == k:
                        img[y0 + j, x0 + i] = (*COL[ch], 255)
    # brillo blanco en la tapa (cerca de la esquina de atras) y en la arista vertical
    for p in ((12, 6), (13, 6), (11, 7)):
        if face_of[p[1], p[0]] == "top":
            img[p[1], p[0]] = (255, 255, 255, 255)
    return img



# ---------------------------------------------------------------- sombreado generico por piezas (luz arriba-izquierda)
def ring_depth(m):
    """profundidad de cada pixel desde el borde de la mascara (1 = borde)"""
    d = np.zeros(m.shape, int)
    cur = m.copy()
    k = 0
    while cur.any() and k < 6:
        k += 1
        inner = cur.copy()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            inner &= shift(cur, dx, dy)
        d[cur & ~inner] = k
        cur = inner
    d[cur] = k + 1
    return d


def bevel(img, m, T, light=(-1, -1), rings=2):
    """T = (oscuro, medio, claro, brillo). borde arriba-izq claro, abajo-der oscuro"""
    dep = ring_depth(m)
    lx, ly = light
    for y, x in zip(*np.where(m)):
        c = T[1]
        if dep[y, x] <= rings:
            up = not (m[y + ly, x] if 0 <= y + ly < N else False) or not (m[y, x + lx] if 0 <= x + lx < N else False)
            dn = not (m[y - ly, x] if 0 <= y - ly < N else False) or not (m[y, x - lx] if 0 <= x - lx < N else False)
            if dep[y, x] == rings:  # segundo anillo: mira 2 px
                up = not m[min(max(y + 2 * ly, 0), N - 1), x] or not m[y, min(max(x + 2 * lx, 0), N - 1)]
                dn = not m[min(max(y - 2 * ly, 0), N - 1), x] or not m[y, min(max(x - 2 * lx, 0), N - 1)]
            if up and not dn:
                c = T[3] if dep[y, x] == rings else T[2]
            elif dn and not up:
                c = T[0]
        img[y, x] = (*c, 255)


def seam(img, m, col):
    """linea oscura de 1 px alrededor de una pieza que va adelante (la separa de lo de atras)"""
    ring = np.zeros_like(m)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            ring |= shift(m, dx, dy)
    ring &= ~m & (img[..., 3] > 0)
    img[ring] = (*col, 255)


def gear_auto():
    img = np.zeros((N, N, 4), np.uint8)
    cx, cy = 14.0, 14.0
    r = np.hypot(XX - cx, YY - cy)
    body = r < 10.0
    for k in range(8):
        t = k / 8 * 2 * np.pi + 0.39
        along = (XX - cx) * np.cos(t) + (YY - cy) * np.sin(t)
        perp = -(XX - cx) * np.sin(t) + (YY - cy) * np.cos(t)
        body |= (np.abs(perp) < 2.9 - 0.12 * np.maximum(along - 9, 0)) & (along > 0) & (along < 13.8)
    hole = r < 3.4
    G = (GOLD[1], GOLD[3], GOLD[4], GOLD[6])
    bevel(img, body & ~hole, G, rings=3)
    for y, x in zip(*np.where((r > 5.0) & (r < 7.6))):  # anillo rebajado
        img[y, x] = (*(GOLD[2] if (XX[y, x] - cx + YY[y, x] - cy) < 0 else GOLD[3]), 255)
    for y, x in zip(*np.where((r >= 7.6) & (r < 8.6) & ((XX - cx + YY - cy) < 0))):
        img[y, x] = (*GOLD[5], 255)
    # flecha verde en circulo (auto) abajo a la derecha
    ax, ay = 22.0, 22.0
    ra = np.hypot(XX - ax, YY - ay)
    aa = np.degrees(np.arctan2(YY - ay, XX - ax)) % 360
    arc = (ra > 3.4) & (ra < 7.8) & ~((aa > 258) & (aa < 350))
    head = poly([(ax - 1.8, ay - 11.4), (ax + 5.8, ay - 5.6), (ax - 1.8, ay + 0.2)])
    arrow = arc | head
    seam(img, arrow, (10, 40, 16))
    GR = ((24, 120, 44), (60, 204, 70), (140, 252, 110), (230, 255, 210))
    bevel(img, arrow, GR, rings=1)
    return img


def stopwatch_fast():
    img = np.zeros((N, N, 4), np.uint8)
    cx, cy = 14.5, 18.0
    r = np.hypot(XX - cx, YY - cy)
    RED = ((120, 10, 30), (214, 36, 52), (255, 92, 92), (255, 200, 190))
    SIL = ((110, 120, 150), (196, 204, 226), (236, 240, 252), (255, 255, 255))
    knob = poly([(12, 2), (17, 2), (17, 5), (12, 5)]) | poly([(13.5, 4), (15.5, 4), (15.5, 8), (13.5, 8)])
    bevel(img, knob, SIL, rings=1)
    side = poly([(23, 6.5), (26.5, 9.5), (24.5, 11.5), (21, 8.5)])
    bevel(img, side, SIL, rings=1)
    bevel(img, r < 12.6, RED, rings=2)
    face = r < 9.2
    for y, x in zip(*np.where(face)):
        img[y, x] = (*(SIL[2] if (XX[y, x] - cx + YY[y, x] - cy) < 4 else SIL[1]), 255)
    for y, x in zip(*np.where((r >= 9.2) & (r < 10.2))):
        img[y, x] = (*RED[0], 255)
    # marcas y aguja
    for ang in range(0, 360, 90):
        t = np.radians(ang)
        img[int(cy + np.sin(t) * 7.3), int(cx + np.cos(t) * 7.3)] = (60, 60, 80, 255)
    for k in range(6):
        img[int(cy - k), int(cx)] = (40, 40, 60, 255)
    for k in range(4):
        img[int(cy + k * 0.6), int(cx + k)] = (214, 36, 52, 255)
    # rayo amarillo adelante (rapido)
    bolt = poly([(20.5, 7.5), (30.8, 7.5), (26, 15.5), (30.8, 15.5), (16.5, 31.2), (20.5, 20.5), (15.5, 20.5)])
    seam(img, bolt, (60, 20, 10))
    YEL = ((214, 110, 0), (255, 200, 24), (255, 238, 100), (255, 255, 230))
    bevel(img, bolt, YEL, rings=2)
    return img



def brick(L, x0, y0, w=19, h=6, d=5):
    """fajo en vista 3/4: tapa (paralelogramo), frente con cantos de billetes y costado; faja dorada"""
    top = poly([(x0, y0), (x0 + d, y0 - d), (x0 + d + w, y0 - d), (x0 + w, y0)])
    front = poly([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)])
    side = poly([(x0 + w, y0), (x0 + w + d, y0 - d), (x0 + w + d, y0 - d + h), (x0 + w, y0 + h)])
    bx = x0 + w * 0.42
    band_top = poly([(bx, y0), (bx + d, y0 - d), (bx + d + 4, y0 - d), (bx + 4, y0)])
    band_front = poly([(bx, y0), (bx + 4, y0), (bx + 4, y0 + h), (bx, y0 + h)])
    L += [(top, "cash"), (front, "pale"), (side, "cashdk"), (band_top, "gold"), (band_front, "golddk")]
    return top, front, side


def cash2d():
    L = []
    b1 = brick(L, 1, 26, w=22, h=6)
    b2 = brick(L, 4, 15, w=22, h=6)
    img, own = paint2d(L, shade=True)
    # cantos de los billetes: rayas en el frente y el costado
    for (top, front, side) in (b1, b2):
        for y in range(N):
            for x in range(N):
                if (front[y, x] or side[y, x]) and img[y, x, 1] > 150 and y % 2 == 0:
                    owner_mat = L[own[y, x]][1]
                    if owner_mat in ("pale", "cashdk"):
                        img[y, x] = (*T2["line"][1], 255) if owner_mat == "pale" else (*T2["cash"][0], 255)
    # tapa del fajo de arriba: medallon con $ (vista inclinada)
    dol = [".#.", "###", "#..", "###", "..#", "###", ".#."]
    for j, row in enumerate(dol[1:6]):
        for i, ch in enumerate(row):
            if ch == "#":
                x, y = 21 + i - j // 2, 8 + j
                if L[own[y, x]][1] == "cash":
                    img[y, x] = (*T2["cashdk"][0], 255)
    put(img, [(6, 14), (7, 13), (8, 12), (3, 25), (4, 24), (5, 23)], T2["cash"][3])  # brillo del borde
    return img


# ---------------------------------------------------------------- trebol morado (2D a mano, como make_clover.py)
def clover_px(pal_, center_gem=True):
    OUTL, SEAM, SHADOW, BASE, LIGHT, HILITE, MID2, STEM, STEM_DK = pal_
    C = np.array((15.5, 13.5))
    ys, xs = np.mgrid[0:N, 0:N]
    P = np.stack([xs + 0.5, ys + 0.5], -1)

    def disk(c, r):
        return ((P - np.array(c)) ** 2).sum(-1) <= r * r

    leaf_id = np.full((N, N), -1)
    dirs = []
    for k, a in enumerate((225, 315, 45, 135)):
        t = np.radians(a)
        d = np.array((np.cos(t), np.sin(t)))
        n = np.array((-d[1], d[0]))
        v = P - C
        along, side = v @ d, v @ n
        wedge = (along > 0.3) & (np.abs(side) <= along * 0.72 + 0.4) & (along < 8.2)
        m = disk(C + d * 7.6 + n * 2.6, 3.25) | disk(C + d * 7.6 - n * 2.6, 3.25) | wedge
        leaf_id[m & (leaf_id < 0)] = k
        dirs.append((d, n))
    leaf = leaf_id >= 0
    stem = np.zeros((N, N), bool)
    for t in np.linspace(0, 1, 60):
        x = C[0] + 1.0 + t * 8.0 + np.sin(t * 2.2) * 1.5
        y = C[1] + 5.0 + t * 11.5
        stem |= disk((x, y), 1.25)
    stem &= ~leaf
    shape = leaf | stem
    img = np.zeros((N, N, 4), np.uint8)
    inside = lambda x, y: 0 <= x < N and 0 <= y < N
    for y in range(N):
        for x in range(N):
            if not leaf[y, x]:
                continue
            k = leaf_id[y, x]
            same = lambda dx, dy: inside(x + dx, y + dy) and leaf_id[y + dy, x + dx] == k
            col = BASE
            if not same(1, 1):
                col = SHADOW
            elif not same(-1, -1):
                col = HILITE if k == 0 else LIGHT
            elif not same(-2, -2):
                col = LIGHT
            elif not same(2, 2):
                col = MID2
            img[y, x] = (*col, 255)
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
    for y in range(N):
        for x in range(N):
            if stem[y, x]:
                edge = not (inside(x + 1, y) and stem[y, x + 1])
                img[y, x] = (*(STEM_DK if edge else STEM), 255)
    cx, cy = int(C[0]), int(C[1])
    if center_gem:  # gema dorada en rombo (5x5) al centro
        GEM = {(0, -2): 2, (-1, -1): 3, (0, -1): 3, (1, -1): 2, (-2, 0): 3, (-1, 0): 3, (0, 0): 2, (1, 0): 2, (2, 0): 1,
               (-1, 1): 2, (0, 1): 1, (1, 1): 1, (0, 2): 1}
        tones = {1: (196, 120, 14), 2: (255, 200, 50), 3: (255, 246, 180)}
        for (dx, dy), t in GEM.items():
            img[cy + dy, cx + dx] = (*tones[t], 255)
        for dx, dy in ((0, -3), (-2, -1), (2, -1), (-3, 0), (3, 0), (-2, 1), (2, 1), (-1, 2), (1, 2), (0, 3), (-1, -2), (1, -2)):
            if img[cy + dy, cx + dx, 3] and tuple(img[cy + dy, cx + dx, :3]) not in tones.values():
                img[cy + dy, cx + dx] = (120, 60, 6, 255)
    else:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            img[cy + dy, cx + dx] = (*SEAM, 255)
    for x, y in ((8, 6), (9, 5), (7, 8), (19, 5), (20, 6)):
        if leaf[y, x]:
            img[y, x] = (255, 255, 255, 255)
    out = np.zeros((N, N), bool)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            out |= np.roll(np.roll(shape, dy, 0), dx, 1)
    out &= ~shape
    img[out] = (*OUTL, 255)
    return img


def gold_rim(img, outl, col=(250, 196, 40)):
    """borde dorado por dentro del contorno (despues va el negro): el trebol de x4 se ve "epico" y se leen las hojas"""
    img = img.copy()
    a = img[..., 3] > 0
    o = np.all(img[..., :3] == np.array(outl), -1) & a
    near = np.zeros_like(o)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            near |= np.roll(np.roll(o, dy, 0), dx, 1)
    img[near & a & ~o] = (*col, 255)
    return img


PURPLE = ((40, 10, 70), (84, 24, 140), (128, 50, 200), (176, 86, 246), (214, 140, 255), (246, 214, 255), (150, 66, 222),
          (232, 172, 30), (168, 100, 8))


# ---------------------------------------------------------------- cartelito x1 / x5 / x10 y destellos
FONT = {
    "x": ["....", "....", "#..#", ".##.", ".##.", "#..#"],
    "0": [".##.", "#..#", "#..#", "#..#", "#..#", ".##."],
    "1": [".#.", "##.", ".#.", ".#.", ".#.", "###"],
    "5": ["####", "#...", "###.", "...#", "#..#", ".##."],
}


def badge(img, text, right=31, bottom=31):
    glyphs = [FONT[c] for c in text]
    w = sum(len(g[0]) for g in glyphs) + len(glyphs) - 1
    x0, y0 = right - 1 - w + 1 - 1, bottom - 1 - 6 + 1 - 1
    pts = []
    x = x0
    for g in glyphs:
        for j, row in enumerate(g):
            for i, ch in enumerate(row):
                if ch == "#":
                    pts.append((x + i, y0 + j, j))
        x += len(g[0]) + 1
    S = {(a, b) for a, b, _ in pts}
    for a, b, _ in pts:  # borde negro (8 vecinos)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = a + dx, b + dy
                if 0 <= xx < N and 0 <= yy < N and (xx, yy) not in S:
                    img[yy, xx] = (10, 10, 12, 255)
    for a, b, j in pts:  # degrade amarillo -> naranja, como el texto dorado
        t = j / 5
        c = np.array((255, 250, 170)) * (1 - t) + np.array((255, 150, 20)) * t
        img[b, a] = (*c.astype(np.uint8), 255)


def sparkle(img, x, y, big=False, color=(255, 255, 255)):
    pts = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)] + ([(2, 0), (-2, 0), (0, 2), (0, -2)] if big else [])
    for dx, dy in pts:
        xx, yy = x + dx, y + dy
        if 0 <= xx < N and 0 <= yy < N and img[yy, xx, 3] == 0:
            img[yy, xx] = (*color, 255)


ROBUX = [
    "......##......",
    "....######....",
    "..####..####..",
    "####......####",
    "###..####..###",
    "##..######..##",
    "##..######..##",
    "##..######..##",
    "##..######..##",
    "###..####..###",
    "####......####",
    "..####..####..",
    "....######....",
    "......##......",
]


def robux():
    """icono de Robux 16x16: hexagono con un cuadrado adentro, blanco con borde negro (ImageColor3 lo tine)"""
    n = 16
    a = np.zeros((n, n, 4), np.uint8)
    solid = np.zeros((n, n), bool)
    for j, row in enumerate(ROBUX):
        for i, ch in enumerate(row):
            solid[j + 1, i + 1] = ch == "#"
    a[solid] = (255, 255, 255, 255)
    ring = np.zeros_like(solid)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            ring |= np.roll(np.roll(solid, dy, 0), dx, 1)
    a[ring & ~solid] = (10, 10, 12, 255)
    return a


# ---------------------------------------------------------------- main
def finish(px, art=N):
    """borde negro de make_outline (trabaja sobre la imagen x16)"""
    im, _ = outline(Image.fromarray(px, "RGBA").resize((art * SCALE, art * SCALE), Image.NEAREST))
    return np.array(im.resize((art, art), Image.NEAREST))


def load_icon(name):
    return np.array(Image.open(os.path.join(OUT, name + ".png")).convert("RGBA").resize((N, N), Image.NEAREST))


def main():
    made = {}
    v = finish(crown())
    star(v, 29, 2, 2)
    star(v, 2, 26, 1)
    made["pass_vip"] = v

    c4 = finish(gold_rim(clover_px(PURPLE), PURPLE[0]))
    sparkle(c4, 27, 3, big=True, color=(255, 236, 140))
    sparkle(c4, 3, 26, color=(240, 200, 255))
    sparkle(c4, 4, 3)
    made["pass_luck4"] = c4

    made["pass_cash2"] = finish(cash2d())
    sparkle(made["pass_cash2"], 4, 4, big=True, color=(255, 246, 170))
    sparkle(made["pass_cash2"], 28, 6)

    jp = finish(die())
    star(jp, 3, 3, 2, tip=(150, 220, 255))
    star(jp, 28, 3, 1, tip=(255, 160, 220))
    made["pass_jackpot"] = jp  # (sin cartelito: inventario y tienda)
    for k in ("1", "5", "10"):
        img = jp.copy()
        badge(img, "x" + k)
        made["pass_jackpot_x" + k] = img
    for src, dst in (("px4_trait_token", "pass_trait_x10"), ("px4_roll_token", "pass_rank_x10")):
        img = load_icon(src)
        badge(img, "x10")
        made[dst] = img

    made["pass_auto"] = finish(gear_auto())
    star(made["pass_auto"], 3, 3, 2)
    made["pass_fast"] = finish(stopwatch_fast())
    star(made["pass_fast"], 3, 4, 2)

    for name, px in made.items():
        Image.fromarray(px, "RGBA").resize((N * SCALE, N * SCALE), Image.NEAREST).save(os.path.join(OUT, name + ".png"))
    rb = robux()
    Image.fromarray(rb, "RGBA").resize((16 * SCALE, 16 * SCALE), Image.NEAREST).save(os.path.join(OUT, "pass_robux.png"))
    print("ok", list(made) + ["pass_robux"])

    if "preview" in sys.argv:
        extra = {"pass_luck2 (ya hecho)": load_icon("px5_clover")}
        allp = list(made.items()) + list(extra.items())
        T = 192
        cols = 5
        rows = (len(allp) + cols - 1) // cols
        sheet = Image.new("RGBA", (cols * (T + 12) + 12, rows * (T + 12) + 12 + 80), (40, 52, 90, 255))
        for i, (name, px) in enumerate(allp):
            tile = Image.new("RGBA", (T, T), (70, 96, 150, 255))
            tile.alpha_composite(Image.fromarray(px, "RGBA").resize((T, T), Image.NEAREST))
            sheet.paste(tile, (12 + (i % cols) * (T + 12), 12 + (i // cols) * (T + 12)))
        sheet.alpha_composite(Image.fromarray(rb, "RGBA").resize((64, 64), Image.NEAREST), (12, rows * (T + 12) + 8))
        sheet.save(sys.argv[sys.argv.index("preview") + 1])


if __name__ == "__main__":
    main()
