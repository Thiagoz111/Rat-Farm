"""
Iconos pixel-art 24x24 del HUD de ROLL A RAT: carrito (SHOP), libro (INDEX), carita (bonus de amigos),
mochila (INVENTORY), regalo (REWARDS), flecha+engranaje (UPGRADES), bolsa de plata (SELL), casa (HOME), puesto (PLAZA).
Se dibujan con figuras sin antialias y el borde negro sale solo (todo pixel vecino a la figura).
En Roblox van con ResampleMode = Pixelated.
  python make_ui_icons2.py   -> ui_*.png al lado de este script
"""
import os

from PIL import Image, ImageDraw

OUT = os.path.dirname(os.path.abspath(__file__))
N, SCALE = 24, 16  # x16: los mipmaps (192, 96, 48) siguen dando bloques enteros -> bordes limpios
K = (24, 14, 8, 255)  # borde


def outline(img):
    """borde de 1 pixel (8 vecinos) alrededor de todo lo pintado"""
    px = img.load()
    filled = {(x, y) for x in range(N) for y in range(N) if px[x, y][3] > 0}
    for x in range(N):
        for y in range(N):
            if (x, y) in filled:
                continue
            if any((x + dx, y + dy) in filled for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                px[x, y] = K
    return img


def save(name, img):
    img.resize((N * SCALE, N * SCALE), Image.NEAREST).save(os.path.join(OUT, name + ".png"))


def cart():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    metal, metal_hi, metal_lo = (236, 242, 252, 255), (255, 255, 255, 255), (150, 165, 190, 255)
    wheel, hub = (52, 52, 66, 255), (200, 200, 210, 255)
    y_, yl, yd, hole = (255, 204, 32, 255), (255, 240, 140, 255), (236, 140, 18, 255), (196, 112, 8, 255)
    # queso asomando del canasto
    d.polygon([(9, 9), (9, 6), (17, 3), (18, 3), (18, 9)], fill=y_)
    d.line([(9, 6), (17, 3)], fill=yl)
    d.line([(10, 6), (17, 4)], fill=yl)
    d.point([(12, 7), (15, 6), (16, 8)], fill=hole)
    d.line([(18, 3), (18, 9)], fill=yd)
    # manija
    d.line([(1, 4), (4, 4)], fill=metal_lo)
    d.line([(5, 5), (6, 9)], fill=metal)
    # canasto (trapecio) con rejilla
    d.polygon([(5, 9), (22, 9), (20, 16), (8, 16)], fill=metal)
    d.line([(6, 9), (21, 9)], fill=metal_hi)
    for x in (10, 14, 18):
        d.line([(x, 10), (x - 1 if x > 14 else x, 15)], fill=metal_lo)
    d.line([(7, 12), (20, 12)], fill=metal_lo)
    # chasis y ruedas
    d.line([(8, 17), (8, 18), (20, 18)], fill=metal_lo)
    for cx in (10, 18):
        d.rectangle([cx - 1, 19, cx + 1, 21], fill=wheel)
        d.point((cx, 20), fill=hub)
    return outline(img)


def book():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    cover, cover_hi, cover_lo = (232, 58, 72, 255), (255, 120, 120, 255), (150, 24, 44, 255)
    page, page_lo = (255, 246, 222, 255), (214, 196, 160, 255)
    gold, gold_lo = (255, 210, 50, 255), (210, 140, 20, 255)
    # bloque de hojas (abajo y a la derecha) y tapa
    d.rectangle([6, 3, 20, 20], fill=page)
    for y in (17, 19):
        d.line([(7, y), (19, y)], fill=page_lo)
    d.rectangle([4, 2, 18, 18], fill=cover)
    d.rectangle([4, 2, 6, 18], fill=cover_lo)  # lomo
    d.line([(7, 3), (17, 3)], fill=cover_hi)
    d.line([(7, 3), (7, 16)], fill=cover_hi)
    # emblema: queso dorado en el centro
    d.polygon([(9, 12), (9, 10), (15, 7), (15, 12)], fill=gold)
    d.line([(9, 10), (15, 7)], fill=(255, 245, 160, 255))
    d.point([(11, 11), (13, 10)], fill=gold_lo)
    # esquineros dorados
    for x, y in ((17, 2), (17, 17)):
        d.rectangle([x, y, x + 1, y + 1], fill=gold)
    # cinta (marcador) colgando
    d.rectangle([14, 19, 15, 22], fill=gold)
    d.point((14, 22), fill=(0, 0, 0, 0))
    return outline(img)


def smile():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    face, hi, lo = (255, 214, 40, 255), (255, 246, 150, 255), (232, 150, 20, 255)
    eye, cheek = (40, 22, 10, 255), (255, 120, 110, 255)
    d.ellipse([2, 2, 21, 21], fill=lo)  # sombra abajo a la derecha
    d.ellipse([2, 2, 20, 20], fill=face)
    d.ellipse([5, 4, 11, 8], fill=hi)  # brillo
    for x in (8, 14):  # ojos
        d.rectangle([x, 8, x + 1, 11], fill=eye)
    d.point([(8, 8), (14, 8)], fill=(255, 255, 255, 255))
    d.rectangle([5, 13, 6, 14], fill=cheek)
    d.rectangle([16, 13, 17, 14], fill=cheek)
    d.line([(7, 14), (8, 15), (14, 15), (15, 14)], fill=eye)  # sonrisa
    d.line([(9, 16), (13, 16)], fill=eye)
    return outline(img)


def backpack():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    bag, hi, lo = (214, 128, 62, 255), (246, 178, 108, 255), (156, 82, 38, 255)
    strap, gold = (120, 60, 30, 255), (255, 210, 50, 255)
    d.rectangle([9, 1, 14, 2], fill=strap)  # manija
    d.point([(8, 2), (15, 2)], fill=strap)
    d.rounded_rectangle([4, 4, 19, 21], radius=4, fill=bag)
    d.rectangle([5, 5, 6, 18], fill=hi)  # luz
    d.rectangle([17, 7, 18, 19], fill=lo)  # sombra
    d.rounded_rectangle([5, 4, 18, 9], radius=3, fill=lo)  # tapa
    d.line([(6, 5), (17, 5)], fill=bag)
    d.rectangle([11, 8, 12, 11], fill=gold)  # hebilla
    d.rounded_rectangle([7, 13, 16, 20], radius=2, fill=lo)  # bolsillo
    d.line([(8, 14), (15, 14)], fill=bag)
    d.rectangle([11, 15, 12, 16], fill=gold)
    return outline(img)


def gift():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    box, hi, lo = (236, 58, 96, 255), (255, 130, 160, 255), (168, 28, 64, 255)
    rib, rib_lo = (255, 214, 50, 255), (220, 150, 20, 255)
    # mono
    d.polygon([(11, 7), (5, 2), (4, 4), (6, 7)], fill=rib)
    d.polygon([(12, 7), (18, 2), (19, 4), (17, 7)], fill=rib)
    d.point([(6, 4), (17, 4)], fill=rib_lo)
    # caja + tapa
    d.rectangle([4, 11, 19, 21], fill=box)
    d.rectangle([17, 11, 19, 21], fill=lo)
    d.rectangle([3, 7, 20, 10], fill=hi)
    d.line([(3, 10), (20, 10)], fill=lo)
    # cinta
    d.rectangle([10, 7, 13, 21], fill=rib)
    d.line([(13, 11), (13, 21)], fill=rib_lo)
    d.point([(6, 13), (15, 18), (7, 19)], fill=hi)  # puntitos
    return outline(img)


def upgrade():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    gear, gear_hi, gear_lo = (255, 196, 54, 255), (255, 236, 140, 255), (206, 130, 20, 255)
    arr, arr_hi, arr_lo = (96, 232, 90, 255), (200, 255, 180, 255), (36, 150, 56, 255)
    cx, cy = 11.5, 12.5
    # engranaje dorado: 8 dientes + cuerpo
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0), (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)):
        x, y = cx + dx * 9, cy + dy * 9
        d.rectangle([round(x - 1.5), round(y - 1.5), round(x + 1.5), round(y + 1.5)], fill=gear)
    d.ellipse([4, 5, 19, 20], fill=gear)
    d.arc([4, 5, 19, 20], 150, 260, fill=gear_hi)
    d.arc([4, 5, 19, 20], 330, 80, fill=gear_lo)
    # flecha verde adentro
    d.polygon([(11, 6), (12, 6), (17, 11), (14, 11), (14, 17), (9, 17), (9, 11), (6, 11)], fill=arr)
    d.line([(11, 7), (8, 10)], fill=arr_hi)
    d.line([(10, 11), (10, 16)], fill=arr_hi)
    d.line([(13, 12), (13, 16)], fill=arr_lo)
    return outline(img)


def moneybag():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    sack, hi, lo = (222, 170, 92, 255), (250, 214, 150, 255), (168, 112, 52, 255)
    rope, dollar = (120, 70, 30, 255), (40, 150, 60, 255)
    d.polygon([(8, 2), (10, 4), (12, 2), (14, 4), (16, 2), (15, 6), (9, 6)], fill=sack)  # punta atada
    d.ellipse([3, 7, 20, 22], fill=sack)
    d.rectangle([9, 5, 14, 8], fill=sack)
    d.line([(8, 6), (15, 6)], fill=rope)
    d.ellipse([5, 9, 9, 13], fill=hi)  # brillo
    d.arc([3, 7, 20, 22], 300, 80, fill=lo)
    # signo $
    for x, y in ((11, 10), (11, 20), (9, 12), (10, 11), (12, 11), (13, 12), (9, 13), (10, 14), (11, 15), (12, 15),
                 (13, 16), (13, 17), (12, 18), (11, 18), (10, 18), (9, 17)):
        d.point((x, y), fill=dollar)
    d.line([(11, 10), (11, 20)], fill=dollar)
    return outline(img)


def house():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    roof, roof_hi, roof_lo = (226, 64, 52, 255), (255, 120, 96, 255), (160, 30, 30, 255)
    wall, wall_lo = (255, 232, 186, 255), (220, 184, 130, 255)
    door, win = (150, 84, 40, 255), (120, 210, 255, 255)
    d.rectangle([15, 2, 17, 7], fill=(150, 150, 160, 255))  # chimenea
    d.rectangle([5, 11, 18, 21], fill=wall)
    d.rectangle([16, 11, 18, 21], fill=wall_lo)
    d.polygon([(11, 2), (12, 2), (22, 11), (1, 11)], fill=roof)
    d.line([(11, 3), (3, 10)], fill=roof_hi)
    d.line([(2, 11), (21, 11)], fill=roof_lo)
    d.rectangle([9, 15, 12, 21], fill=door)
    d.point((11, 18), fill=(255, 210, 50, 255))
    d.rectangle([14, 13, 16, 15], fill=win)
    d.point((14, 13), fill=(255, 255, 255, 255))
    return outline(img)


def stall():
    img = Image.new("RGBA", (N, N))
    d = ImageDraw.Draw(img)
    red, white, wood, wood_lo = (232, 56, 64, 255), (255, 246, 236, 255), (176, 104, 52, 255), (124, 70, 34, 255)
    y_, yl = (255, 204, 32, 255), (255, 240, 140, 255)
    # toldo a rayas con borde ondulado
    for i, x in enumerate(range(2, 22, 4)):
        d.rectangle([x, 3, x + 3, 8], fill=red if i % 2 == 0 else white)
        d.rectangle([x + 1, 9, x + 2, 9], fill=red if i % 2 == 0 else white)
    d.line([(2, 2), (21, 2)], fill=red)
    # postes y mostrador
    d.rectangle([3, 10, 4, 20], fill=wood_lo)
    d.rectangle([19, 10, 20, 20], fill=wood_lo)
    d.rectangle([2, 15, 21, 21], fill=wood)
    d.line([(2, 15), (21, 15)], fill=(214, 140, 80, 255))
    d.line([(2, 18), (21, 18)], fill=wood_lo)
    # quesos en el mostrador
    d.polygon([(6, 14), (6, 12), (11, 10), (11, 14)], fill=y_)
    d.line([(6, 12), (11, 10)], fill=yl)
    d.polygon([(13, 14), (13, 12), (17, 11), (17, 14)], fill=y_)
    d.line([(13, 12), (17, 11)], fill=yl)
    return outline(img)


save("ui_cart", cart())
save("ui_backpack", backpack())
save("ui_gift", gift())
save("ui_upgrade", upgrade())
save("ui_moneybag", moneybag())
save("ui_house", house())
save("ui_stall", stall())
save("ui_smile", smile())
save("ui_book", book())
