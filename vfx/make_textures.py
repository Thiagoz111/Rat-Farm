"""
Texturas de particulas para las mutaciones de ROLL A RAT.
Todas blancas (el Color del ParticleEmitter las tine) salvo glitch (colores horneados).
Flipbooks 1024x1024 (Grid4x4 = 16 cuadros de 256, Grid2x2 = 4 de 512).
  python make_textures.py   -> escribe los .png al lado de este script
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates, gaussian_filter

OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)


def save(name, rgb, a):
    """rgb: HxWx3 o HxW (0..1), a: HxW (0..1)"""
    if rgb.ndim == 2:
        rgb = np.repeat(rgb[..., None], 3, axis=2)
    img = np.concatenate([np.clip(rgb, 0, 1), np.clip(a, 0, 1)[..., None]], axis=2)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, name + ".png"))


def grid(n):
    """coords -1..1, y para arriba"""
    c = (np.arange(n) + 0.5) / n * 2 - 1
    x, y = np.meshgrid(c, -c)
    return x, y


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def sheet(frames, cols):
    n = frames[0][1].shape[0]
    rgb = np.zeros((n * cols, n * cols, 3))
    a = np.zeros((n * cols, n * cols))
    for i, (fr, fa) in enumerate(frames):
        r, c = divmod(i, cols)
        if fr.ndim == 2:
            fr = np.repeat(fr[..., None], 3, axis=2)
        rgb[r * n:(r + 1) * n, c * n:(c + 1) * n] = fr
        a[r * n:(r + 1) * n, c * n:(c + 1) * n] = fa
    return rgb, a


# ---------------------------------------------------------------- ruido 3D (x, y, tiempo) suave
class Noise3:
    def __init__(self, res=24, depth=24, seed=1):
        r = np.random.default_rng(seed)
        self.g = r.random((depth, res, res))
        self.res, self.depth = res, depth

    def __call__(self, x, y, t):
        # x, y en "celdas" (pueden ser grandes: se envuelve), t en celdas
        coords = np.array([np.full_like(x, t) % self.depth, y % self.res, x % self.res])
        return map_coordinates(self.g, coords, order=3, mode="grid-wrap")


def fbm(nz, x, y, t, oct=4):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(oct):
        f = 2 ** o
        s = s + amp * nz(x * f + o * 7.3, y * f + o * 3.1, t * f + o * 5.7)
        tot += amp
        amp *= 0.5
    return s / tot


# ---------------------------------------------------------------- glow
def glow():
    x, y = grid(256)
    r = np.sqrt(x * x + y * y)
    a = np.clip(1 - r, 0, 1) ** 2.4
    save("glow", np.ones_like(a), a)


# ---------------------------------------------------------------- sparkle (destello de 4 puntas + 4 chiquitas)
def sparkle():
    x, y = grid(256)
    r = np.sqrt(x * x + y * y)

    def ray(u, v, w, p):
        return np.exp(-(v / w) ** 2) * np.clip(1 - np.abs(u), 0, 1) ** p

    a = ray(x, y, 0.035, 2.2) + ray(y, x, 0.035, 2.2)
    d1, d2 = (x + y) / math.sqrt(2), (x - y) / math.sqrt(2)
    a += 0.45 * (ray(d1 * 1.6, d2, 0.025, 3) + ray(d2 * 1.6, d1, 0.025, 3))
    a += np.clip(1 - r / 0.32, 0, 1) ** 2.2 * 0.9
    a += np.clip(1 - r / 0.08, 0, 1) * 0.6
    save("sparkle", np.ones_like(a), np.clip(a, 0, 1))


# ---------------------------------------------------------------- formas con PIL (supersampleadas)
def poly_mask(n, polys_vals, ss=4):
    """polys_vals = [(lista de puntos en -1..1, valor)] -> mascara n x n"""
    N = n * ss
    im = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(im)
    for pts, val in polys_vals:
        d.polygon([((px + 1) / 2 * N, (1 - (py + 1) / 2) * N) for px, py in pts], fill=int(val * 255))
    return np.asarray(im.resize((n, n), Image.LANCZOS)).astype(float) / 255


def star():
    n = 256
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = 0.74 if i % 2 == 0 else 0.31
        pts.append((rr * math.cos(ang), rr * math.sin(ang) - 0.03))
    body = poly_mask(n, [(pts, 1)])
    halo = gaussian_filter(body, 14) * 0.55
    x, y = grid(n)
    r = np.sqrt(x * x + (y + 0.03) ** 2)
    shade = 0.82 + 0.18 * np.clip(1 - r / 0.6, 0, 1)
    a = np.clip(body + halo * (1 - body), 0, 1)
    save("star", np.where(body > 0.01, shade, 1), a)


def shard():
    n = 256
    T, UR, LR, B = (0, 0.95), (0.3, 0.32), (0.22, -0.55), (0, -0.95)
    UL, LL = (-0.3, 0.32), (-0.22, -0.55)
    C = (0.02, 0.1)
    facets = [
        ([T, UL, C], 1.0), ([T, C, UR], 0.78),
        ([UL, LL, B, C], 0.88), ([C, B, LR, UR], 0.55),
    ]
    body = poly_mask(n, [(p, 1) for p, _ in facets])
    shade = np.zeros((n, n))
    for p, v in facets:
        shade = np.maximum(shade, poly_mask(n, [(p, v)]))
    # bordes y arista brillantes
    edge = np.clip(body - gaussian_filter(body, 2.2), 0, 1) * 2.5
    ridge = poly_mask(n, [([(0.0, 0.93), (0.035, 0.1), (0.0, -0.93), (-0.015, 0.1)], 1)])
    halo = gaussian_filter(body, 10) * 0.45
    rgb = np.clip(np.where(body > 0.02, shade / np.maximum(body, 1e-3), 1) + edge + ridge * 0.6, 0, 1)
    a = np.clip(body + halo * (1 - body), 0, 1)
    save("shard", rgb, a)


# ---------------------------------------------------------------- anillo (onda expansiva)
def ring():
    x, y = grid(256)
    r = np.sqrt(x * x + y * y)
    a = np.exp(-((r - 0.82) / 0.045) ** 2) + 0.35 * np.exp(-((r - 0.72) / 0.13) ** 2) * (r < 0.82)
    a *= r < 0.99
    save("ring", np.ones_like(a), np.clip(a, 0, 1))


# ---------------------------------------------------------------- rayos (estallido)
def rays():
    n = 512
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    th = np.arctan2(y, x)
    a = np.zeros_like(r)
    k = 28
    for i in range(k):
        c = i / k * 2 * math.pi + rng.uniform(-0.08, 0.08)
        w = rng.uniform(0.02, 0.06)
        ln = rng.uniform(0.55, 0.98)
        d = np.angle(np.exp(1j * (th - c)))
        a += np.exp(-(d / w) ** 2) * np.clip(1 - r / ln, 0, 1) ** 1.4
    a = np.clip(a, 0, 1) * smoothstep(0.02, 0.15, r) + np.clip(1 - r / 0.28, 0, 1) ** 2
    save("rays", np.ones_like(a), np.clip(a, 0, 1))


# ---------------------------------------------------------------- estela vertical (aura que sube, lineas de velocidad)
def wisp():
    x, y = grid(256)
    a = np.exp(-(x / 0.09) ** 2) * np.clip(np.sin(math.pi * (y + 1) / 2), 0, 1) ** 1.6
    a += 0.35 * np.exp(-(x / 0.25) ** 2) * np.clip(np.sin(math.pi * (y + 1) / 2), 0, 1) ** 2.5
    save("wisp", np.ones_like(a), np.clip(a, 0, 1))


# ---------------------------------------------------------------- fuego: flipbook OneShot (una lengua nace, sube y se rompe)
def flame():
    n = 256
    nz = Noise3(24, 32, seed=3)
    x, y = grid(n)
    v = (y + 1) / 2  # 0 abajo .. 1 arriba
    frames = []
    for i in range(16):
        t = i / 15
        # warp: el ruido sube con el tiempo
        w1 = fbm(nz, (x + 1) * 3.0, (v - t * 0.9) * 3.0 + 4, t * 6, 3)
        w2 = fbm(nz, (x + 1) * 3.0 + 9, (v - t * 0.9) * 3.0 + 11, t * 6 + 3, 3)
        lift = 0.04 + 0.32 * t ** 1.6
        H = 0.42 + 0.48 * smoothstep(0, 0.45, t) - 0.2 * t ** 2
        W = 0.5 * (1 - 0.35 * t)
        s = np.clip((v - lift + (w2 - 0.5) * 0.18) / H, 0, 1.4)
        xw = x + (w1 - 0.5) * 0.55 * (0.25 + s)
        width = W * (1 - np.clip(s, 0, 1)) ** 0.75 * np.clip((s + 0.06) / 0.22, 0, 1) ** 0.45
        d = 1 - np.abs(xw) / np.maximum(width, 1e-4)
        d = np.where((s > 0) & (s < 1), d, -1)
        detail = fbm(nz, (x + 1) * 6 + 2, (v - t * 1.3) * 6, t * 9 + 7, 3)
        dens = d + (detail - 0.5) * (0.6 + 1.1 * t) - 0.55 * t ** 1.8
        a = smoothstep(0.02, 0.32, dens)
        a *= smoothstep(0, 0.12, t + 0.06) * (1 - smoothstep(0.62, 1.0, t))
        inten = 0.55 + 0.45 * smoothstep(0.25, 0.85, dens)
        frames.append((inten, a))
    rgb, a = sheet(frames, 4)
    save("flame_fb", rgb, a)


# ---------------------------------------------------------------- humo: flipbook OneShot (bocanada que se abre y se va)
def smoke():
    n = 256
    nz = Noise3(20, 32, seed=11)
    x, y = grid(n)
    frames = []
    for i in range(16):
        t = i / 15
        R = 0.38 + 0.5 * t
        w = fbm(nz, (x + 1) * 2.5, (y + 1) * 2.5 - t * 1.5, t * 5, 3)
        r = np.sqrt(x * x + y * y) / R + (w - 0.5) * 0.7
        det = fbm(nz, (x + 1) * 5 + 3, (y + 1) * 5 - t * 3, t * 7 + 4, 4)
        dens = (1 - r) + (det - 0.5) * (0.5 + 0.7 * t) - 0.35 * t
        a = smoothstep(-0.12, 0.3, dens) * (1 - t) ** 1.1 * smoothstep(0, 0.12, t + 0.04)
        shade = 0.72 + 0.28 * np.clip(0.5 + 0.6 * (y - x) * 0.5 + (det - 0.5), 0, 1)
        frames.append((shade, a))
    rgb, a = sheet(frames, 4)
    save("smoke_fb", rgb, a)


# ---------------------------------------------------------------- glitch: flipbook Random (bloques con aberracion RGB)
def glitch():
    n = 256
    cyan, mag, white, ink = (0.1, 1, 1), (1, 0.15, 0.9), (1, 1, 1), (0.05, 0.03, 0.12)
    frames = []
    for i in range(16):
        r = np.random.default_rng(100 + i)
        rgb = np.zeros((n, n, 3))
        a = np.zeros((n, n))

        def block(x0, y0, w, h, col, alpha, kind):
            x1, y1 = min(n, x0 + w), min(n, y0 + h)
            x0, y0 = max(0, x0), max(0, y0)
            if x1 <= x0 or y1 <= y0:
                return
            m = np.ones((y1 - y0, x1 - x0))
            if kind == "scan":
                m[1::3, :] = 0.25
            elif kind == "bits":
                cell = 4
                g = r.random(((y1 - y0) // cell + 1, (x1 - x0) // cell + 1)) > 0.45
                m = np.kron(g, np.ones((cell, cell)))[: y1 - y0, : x1 - x0] * 1.0
                m[::cell, :] = 0
                m[:, ::cell] = 0
            sl = (slice(y0, y1), slice(x0, x1))
            al = m * alpha
            rgb[sl] = rgb[sl] * (1 - al[..., None]) + np.array(col) * al[..., None]
            a[sl] = np.maximum(a[sl], al)

        cx, cy = n // 2, n // 2
        for _ in range(r.integers(14, 22)):
            horiz = r.random() < 0.7
            w = int(r.integers(50, 210) if horiz else r.integers(22, 80))
            h = int(r.integers(6, 30) if horiz else r.integers(22, 80))
            x0 = int(cx + r.normal(0, 42) - w / 2)
            y0 = int(cy + r.normal(0, 42) - h / 2)
            kind = r.choice(["solid", "scan", "bits", "solid"])
            sh = int(r.integers(3, 9))
            block(x0 - sh, y0, w, h, cyan, 0.85, kind)
            block(x0 + sh, y0, w, h, mag, 0.85, kind)
            block(x0, y0, w, h, white if r.random() < 0.6 else ink, 0.95, kind)
        # bordes del cuadro limpios (2 px) para que no se pegue al vecino del atlas
        a[:3, :] = a[-3:, :] = 0
        a[:, :3] = a[:, -3:] = 0
        frames.append((rgb, a))
    rgb, a = sheet(frames, 4)
    save("glitch_fb", rgb, a)


# ---------------------------------------------------------------- estatica de TV: flipbook Random
def static():
    n = 256
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    mask = np.clip(1 - r, 0, 1) ** 0.8
    frames = []
    for i in range(16):
        g = np.random.default_rng(300 + i)
        lo = g.random((48, 48))
        img = np.kron(lo, np.ones((n // 48 + 1, n // 48 + 1)))[:n, :n]
        # tirones horizontales
        for _ in range(3):
            y0 = int(g.integers(0, n - 20))
            h = int(g.integers(4, 18))
            img[y0:y0 + h] = np.roll(img[y0:y0 + h], int(g.integers(-40, 40)), axis=1)
        val = (img > 0.5) * 1.0
        a = mask * (0.35 + 0.65 * val)
        frames.append((0.15 + 0.85 * val, a))
    rgb, a = sheet(frames, 4)
    save("static_fb", rgb, a)


# ---------------------------------------------------------------- rayo electrico: flipbook 2x2 Random
def bolt():
    n, ss = 512, 2
    N = n * ss
    frames = []
    for i in range(4):
        g = np.random.default_rng(500 + i)
        im = Image.new("L", (N, N), 0)
        d = ImageDraw.Draw(im)

        def path(p0, p1, disp, depth):
            if depth == 0:
                return [p0, p1]
            mid = ((p0[0] + p1[0]) / 2 + g.normal(0, disp), (p0[1] + p1[1]) / 2 + g.normal(0, disp * 0.3))
            return path(p0, mid, disp / 2, depth - 1)[:-1] + path(mid, p1, disp / 2, depth - 1)

        main = path((N / 2 + g.normal(0, 30), 40), (N / 2 + g.normal(0, 60), N - 40), 150, 7)
        d.line(main, fill=255, width=int(7 * ss), joint="curve")
        for _ in range(3):
            k = int(g.integers(len(main) // 5, len(main) * 3 // 4))
            p0 = main[k]
            ang = math.radians(g.uniform(20, 70)) * g.choice([-1, 1])
            ln = g.uniform(0.15, 0.35) * N
            p1 = (p0[0] + math.sin(ang) * ln, p0[1] + math.cos(ang) * ln)
            d.line(path(p0, p1, 50, 5), fill=200, width=int(4 * ss), joint="curve")
        core = np.asarray(im.resize((n, n), Image.LANCZOS)).astype(float) / 255
        a = np.clip(core + 0.7 * gaussian_filter(core, 5) * 3 + 0.4 * gaussian_filter(core, 16) * 5, 0, 1)
        rgb = np.clip(0.7 + core, 0, 1)
        frames.append((rgb, a))
    rgb, a = sheet(frames, 2)
    save("bolt_fb", rgb, a)


# ---------------------------------------------------------------- grietas en el piso (Beast)
def crack():
    n, ss = 512, 2
    N = n * ss
    g = np.random.default_rng(42)
    im = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(im)

    def walk(p, ang, ln, width, depth):
        pts = [p]
        steps = 9
        for s in range(steps):
            ang += g.normal(0, 0.28)
            p = (p[0] + math.cos(ang) * ln / steps, p[1] + math.sin(ang) * ln / steps)
            pts.append(p)
            w = max(1, int(width * (1 - s / steps * 0.8)))
            d.line(pts[-2:], fill=255, width=w)
            if depth > 0 and g.random() < 0.22:
                walk(p, ang + g.choice([-1, 1]) * g.uniform(0.5, 1.0), ln * 0.45, w * 0.7, depth - 1)

    c = (N / 2, N / 2)
    k = 9
    for i in range(k):
        walk(c, i / k * 2 * math.pi + g.uniform(-0.2, 0.2), N * g.uniform(0.32, 0.46), 8 * ss, 2)
    lines = np.asarray(im.resize((n, n), Image.LANCZOS)).astype(float) / 255
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    fade = 1 - smoothstep(0.55, 0.95, r)
    a = np.clip(lines * 1.3 + gaussian_filter(lines, 5) * 1.4, 0, 1) * fade
    a = np.clip(a + np.clip(1 - r / 0.16, 0, 1) ** 2 * 0.7, 0, 1)
    rgb = np.clip(0.75 + 0.25 * lines + np.clip(1 - r / 0.25, 0, 1) * 0.3, 0, 1)
    save("crack", rgb, a)


# ---------------------------------------------------------------- espiral (portal / vacio)
def vortex():
    x, y = grid(256)
    r = np.sqrt(x * x + y * y)
    th = np.arctan2(y, x)
    arms = (0.5 + 0.5 * np.cos(3 * th + 9 * r)) ** 3
    a = arms * smoothstep(0.08, 0.35, r) * (1 - smoothstep(0.7, 0.98, r))
    a = np.clip(a + 0.25 * np.clip(1 - r, 0, 1) ** 2, 0, 1)
    save("vortex", np.ones_like(a), a)


if __name__ == "__main__":
    for f in (glow, sparkle, star, shard, ring, rays, wisp, flame, smoke, glitch, static, bolt, crack, vortex):
        f()
        print("ok", f.__name__)
