"""
Rayos pixel-art (destello de atras de los iconos, como la referencia): 12 rayos blancos desde el centro, mas opacos
cerca del centro y desvaneciendose en 3 escalones. 64x64 exportado x8 = 512 px. En Roblox gira con el atributo Spin
(UIKit) y se tine con ImageColor3 / ImageTransparency.
  python make_rays.py   -> px5_rays.png + px6_rays_soft.png
px6_rays_soft: igual pero SUAVE (pedido del usuario): la opacidad baja de a poco hacia afuera (sin escalones ni corte
seco en el borde) y los costados de cada rayo se desvanecen. Sigue en bloques de 64x64 (pixel), solo el alfa es suave.
"""
import os

import numpy as np
from PIL import Image

N, SCALE, RAYS = 64, 8, 12
ys, xs = np.mgrid[0:N, 0:N]
dx, dy = xs + 0.5 - N / 2, ys + 0.5 - N / 2
r = np.hypot(dx, dy) / (N / 2)
ang = (np.degrees(np.arctan2(dy, dx)) % (360 / RAYS)) / (360 / RAYS)  # 0..1 dentro de cada par rayo/hueco
width = 0.5 - 0.12 * r  # (los rayos se afinan un poco hacia afuera)
ray = np.abs(ang - 0.5) < width / 2 + 0.02
alpha = np.select([r < 0.45, r < 0.72, r < 1.0], [235, 160, 80], 0)
a = np.zeros((N, N, 4), np.uint8)
a[..., :3] = 255
a[..., 3] = np.where(ray, alpha, 0)
a[r < 0.16, 3] = 255  # centro
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "px5_rays.png")
Image.fromarray(a, "RGBA").resize((N * SCALE, N * SCALE), Image.NEAREST).save(path)
print("saved", path)

# ---------------------------------------------------------------- version suave
def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


side = np.abs(ang - 0.5) - width / 2  # <0 adentro del rayo
soft_side = 1 - smooth(-0.01, 0.09, side)  # (costados que se desvanecen)
fade = 1 - smooth(0.25, 1.0, r)  # (baja suave hasta 0 justo en el borde)
b = np.zeros((N, N, 4), np.uint8)
b[..., :3] = 255
b[..., 3] = np.clip(245 * soft_side * fade + 255 * (1 - smooth(0.08, 0.2, r)), 0, 255).astype(np.uint8)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "px6_rays_soft.png")
Image.fromarray(b, "RGBA").resize((N * SCALE, N * SCALE), Image.NEAREST).save(path)
print("saved", path)

# ---------------------------------------------------------------- halo pixel (atras del icono de las cartas de la tienda)
# 32x32 x8: circulos blancos con la opacidad bajando en 4 escalones (pixel, sin borde suave). Se tine con ImageColor3.
G = 32
gy, gx = np.mgrid[0:G, 0:G]
gr = np.hypot(gx + 0.5 - G / 2, gy + 0.5 - G / 2) / (G / 2)
g = np.zeros((G, G, 4), np.uint8)
g[..., :3] = 255
g[..., 3] = np.select([gr < 0.34, gr < 0.58, gr < 0.8, gr < 1.0], [200, 130, 70, 28], 0)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "px7_glow.png")
Image.fromarray(g, "RGBA").resize((G * 8, G * 8), Image.NEAREST).save(path)
print("saved", path)
