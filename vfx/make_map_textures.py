"""Texturas del mapa multijugador (ServerStorage.WorldBuilder.TEX): flecha de la cinta, grilla del piso y paredes de luz
de las zonas animadas. Subir: servir la carpeta con python -m http.server en 127.0.0.1 + upload_image (Studio MCP)."""
import random
from PIL import Image, ImageDraw

# flecha ^ blanca con sombra celeste (tile = ancho de la cinta)
im = Image.new('RGBA', (512, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
def chev(dy, col, t=46):
    d.polygon([(70, 200 + dy), (256, 70 + dy), (442, 200 + dy), (442, 200 + t + dy), (256, 70 + t + dy), (70, 200 + t + dy)], fill=col)
chev(10, (150, 190, 255, 255))
chev(0, (255, 255, 255, 255))
im.save('chevron.png')

# tablero 2x2 verde oscuro muy suave (grilla del piso, StudsPerTile 16)
N = 256
c = Image.new('RGBA', (N * 2, N * 2), (0, 0, 0, 0))
dc = ImageDraw.Draw(c)
dc.rectangle([0, 0, N - 1, N - 1], fill=(0, 60, 0, 30))
dc.rectangle([N, N, 2 * N - 1, 2 * N - 1], fill=(0, 60, 0, 30))
c.save('grid_checker.png')

# pared de luz: blanca, opaca abajo y se desvanece arriba
w = Image.new('RGBA', (64, 256))
px = w.load()
for y in range(256):
    u = 1 - y / 255
    a = 255 if y > 246 else int(255 * (u ** 1.8) * 0.85)
    for x in range(64):
        px[x, y] = (255, 255, 255, a)
w.save('zone_wall.png')

# chispitas (rombos) que suben por la pared
s = Image.new('RGBA', (128, 256), (0, 0, 0, 0))
p2 = s.load()
random.seed(3)
for _ in range(18):
    cx, cy, r = random.randrange(6, 122), random.randrange(6, 250), random.choice([3, 4, 5])
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if abs(dx) + abs(dy) <= r:
                p2[(cx + dx) % 128, (cy + dy) % 256] = (255, 255, 255, 230)
s.save('zone_sparks.png')

# circulo de las zonas (como el video 2026-10-12 02-41-40): relleno suave que se aclara al borde + anillo de 40 rayitas
import math
N = 512
c = N / 2
z = Image.new('RGBA', (N, N), (0, 0, 0, 0))
pz = z.load()
R, DASH = 0.9, 40
for y in range(N):
    for x in range(N):
        dx, dy = (x + 0.5 - c) / c, (y + 0.5 - c) / c
        r = math.hypot(dx, dy)
        a = 0.10 + 0.30 * (r / R) ** 3 if r < R - 0.03 else (0.42 if r < R + 0.01 else 0.0)
        d = abs(r - R)
        a = max(a, 0.35 * max(0, 1 - d / 0.05))
        if d < 0.022 and ((math.atan2(dy, dx) / (2 * math.pi)) % 1 * DASH) % 1 < 0.55:
            a = 1.0
        if r > R + 0.06:
            a = 0
        pz[x, y] = (255, 255, 255, int(255 * min(1, a)))
z.save('zone_ring.png')
