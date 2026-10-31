"""Motor de dibujo a mano para Miami Sin Filtro.

Reproduce el trazo de la ficha original: tinta negra con ligero temblor,
círculos que casi cierran, papel crema y rellenos pastel de marcador.
Todas las figuras se dibujan en coordenadas locales (cabeza centrada en 0,0)
y se colocan con translate/scale.
"""
import base64
import math
import os
import random

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(AQUI, "..", "fuentes")

# Paleta tomada de la ficha original
TINTA = "#1E1E1E"
PAPEL = "#FBF7EF"
ROSA = "#F2A7B5"
MENTA = "#9ED6CB"
AMARILLO = "#F7DC8C"
AZUL = "#A9CDEB"
CORAL = "#F4A483"
LAVANDA = "#C9BCEB"
GRIS_PELO = "#4A4440"
GRIS = "#8A8580"
ROJO = "#E0646A"

rng = random.Random(7)


def semilla(n):
    rng.seed(n)


def _j(v, a):
    return v + rng.uniform(-a, a)


def _curva(pts):
    """Catmull-Rom -> Bezier, para que el trazo fluya como a mano."""
    if len(pts) < 3:
        (x0, y0), (x1, y1) = pts
        return f"M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}"
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


def trazo(puntos, w=3.0, color=TINTA, temblor=1.2, pasos=None, fill="none", cerrar=False):
    """Línea a mano que pasa por los puntos dados (subdivide y tiembla)."""
    pts = []
    for i in range(len(puntos) - 1):
        (x0, y0), (x1, y1) = puntos[i], puntos[i + 1]
        largo = math.hypot(x1 - x0, y1 - y0)
        n = pasos or max(2, int(largo / 18))
        for k in range(n):
            t = k / n
            pts.append((_j(x0 + (x1 - x0) * t, temblor), _j(y0 + (y1 - y0) * t, temblor)))
    pts.append((_j(puntos[-1][0], temblor * 0.5), _j(puntos[-1][1], temblor * 0.5)))
    d = _curva(pts) + (" Z" if cerrar else "")
    return (f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def curva(d_puntos, **kw):
    """Igual que trazo pero sin subdividir: los puntos ya describen la curva."""
    kw.setdefault("pasos", 1)
    return trazo(d_puntos, **kw)


def ovalo(cx, cy, rx, ry, fill="#fff", w=3.0, color=TINTA, temblor=0.012, sobra=0.12):
    """Círculo a mano: radio irregular y el trazo se pasa un poquito al cerrar."""
    n = 26
    a0 = rng.uniform(0, 2 * math.pi)
    rel = []
    for k in range(n + 1):
        a = a0 + (2 * math.pi) * k / n
        f = 1 + rng.uniform(-temblor, temblor)
        rel.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
    relleno = (f'<path d="{_curva(rel)} Z" fill="{fill}" stroke="none"/>' if fill != "none" else "")
    extra = []
    for k in range(int(n * sobra) + 1):
        a = a0 + 2 * math.pi + (2 * math.pi) * k / n
        extra.append((cx + rx * 1.015 * math.cos(a), cy + ry * 1.015 * math.sin(a)))
    linea = (f'<path d="{_curva(rel + extra[1:])}" fill="none" stroke="{color}" '
             f'stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    return relleno + linea


def forma(puntos, fill, w=3.0, temblor=1.0, color=TINTA):
    """Forma cerrada rellena con contorno a mano."""
    return trazo(list(puntos) + [puntos[0]], w=w, temblor=temblor, fill=fill, color=color)


def punto(x, y, r=3.2):
    return f'<circle cx="{_j(x, .3):.1f}" cy="{_j(y, .3):.1f}" r="{r}" fill="{TINTA}"/>'


def texto(x, y, s, tam=22, peso="normal", color=TINTA, ancla="middle", fuente="mano", rot=0):
    fam = "PatrickHand" if fuente == "mano" else "GochiHand"
    r = f' transform="rotate({rot} {x} {y})"' if rot else ""
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{tam}" font-weight="{peso}" '
            f'fill="{color}" text-anchor="{ancla}"{r}>{s}</text>')


def g(contenido, x=0, y=0, s=1.0, rot=0, espejo=False):
    t = f"translate({x} {y})"
    if rot:
        t += f" rotate({rot})"
    t += f" scale({-s if espejo else s} {s})"
    return f'<g transform="{t}">{"".join(contenido)}</g>'


def documento(ancho, alto, contenido, fondo=PAPEL):
    def b64(n):
        with open(os.path.join(FUENTES, n), "rb") as f:
            return base64.b64encode(f.read()).decode()
    estilos = (
        "@font-face{font-family:PatrickHand;src:url(data:font/woff2;base64,%s) format('woff2')}"
        "@font-face{font-family:GochiHand;src:url(data:font/woff2;base64,%s) format('woff2')}"
        % (b64("PatrickHand.woff2"), b64("GochiHand.woff2")))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" '
            f'width="{ancho}" height="{alto}"><style>{estilos}</style>'
            f'<rect width="{ancho}" height="{alto}" fill="{fondo}"/>'
            f'{"".join(contenido)}</svg>')


# ---------------------------------------------------------------- cuerpo base
# Cabeza grande (r≈50) centrada en 0,0. Torso en forma de saco/camisa con
# contorno, brazos y piernas de un solo trazo, manos redondas, pies pequeños.

def torso(fill="#fff"):
    return forma([(-21, 46), (-27, 95), (-31, 148), (0, 152), (31, 148), (27, 95), (21, 46), (0, 49)], fill)


def brazo(puntos, mano=True):
    out = [trazo(puntos, w=2.8)]
    if mano:
        x, y = puntos[-1]
        out.append(ovalo(x, y, 5, 5, fill="#fff", w=2.4))
    return "".join(out)


def piernas(abiertas=1.0, zapato=TINTA):
    a = 14 * abiertas
    return "".join([
        trazo([(-12, 150), (-a - 6, 238)], w=2.8),
        trazo([(12, 150), (a + 6, 238)], w=2.8),
        ovalo(-a - 12, 240, 9, 4.5, fill=zapato, w=2.2),
        ovalo(a + 12, 240, 9, 4.5, fill=zapato, w=2.2),
    ])


def cabeza(rx=50, ry=47):
    return ovalo(0, 0, rx, ry, fill="#fff", w=3.2)


# ojos de párpado pesado: la línea del párpado tapa medio ojo
def ojos_jay(ceja_der=-4, ceja_izq=0, mirada=0):
    out = []
    for sx in (-1, 1):
        x0, x1 = sx * 9, sx * 30
        out.append(trazo([(x0, -4), (x1, -4)], w=3.2, temblor=.5))
        cx = sx * 19 + mirada
        out.append(f'<path d="M{cx-6:.1f} -4 A6 6 0 0 0 {cx+6:.1f} -4 Z" fill="{TINTA}"/>')
    out.append(trazo([(-30, -16 + ceja_izq), (-11, -15)], w=2.6, temblor=.4))
    out.append(trazo([(11, -15), (30, -16 + ceja_der)], w=2.6, temblor=.4))
    return "".join(out)


def boca_plana(ancho=9, y=24, caida=1.5):
    return trazo([(-ancho, y), (0, y + .3), (ancho, y + caida)], w=3, temblor=.3)


def gafas_sol():
    return "".join([
        forma([(-36, -12), (-6, -12), (-8, 6), (-32, 7)], TINTA, w=2.5, temblor=.4),
        forma([(6, -12), (36, -12), (32, 7), (8, 6)], TINTA, w=2.5, temblor=.4),
        trazo([(-6, -8), (6, -8)], w=3, temblor=.3),
        trazo([(-36, -10), (-48, -14)], w=2.5, temblor=.3),
        trazo([(36, -10), (48, -14)], w=2.5, temblor=.3),
    ])


def micro(x, y, ang=-20, etiqueta=True):
    partes = [
        forma([(-5, 0), (5, 0), (4, 42), (-4, 42)], TINTA, w=2, temblor=.3),
        ovalo(0, -8, 12, 12, fill=TINTA, w=2.4),
    ]
    if etiqueta:
        partes += [forma([(-10, 6), (10, 6), (10, 22), (-10, 22)], ROJO, w=2, temblor=.3),
                   texto(0, 19, "MSF", tam=10, color="#fff")]
    return g(partes, x, y, rot=ang)


def credencial():
    return "".join([
        trazo([(-14, 47), (0, 88), (14, 47)], w=2, temblor=.6),
        forma([(-11, 86), (11, 86), (11, 114), (-11, 114)], "#fff", w=2.2, temblor=.3),
        ovalo(0, 96, 3.5, 3.5, fill="none", w=1.6),
        curva([(-5, 108), (0, 102), (5, 108)], w=1.6, temblor=.2),
    ])


# ---------------------------------------------------------------- personajes

def jay(pose="micro", gafas=False):
    """Jay Fontana: cara de 'no me sorprende nada', credencial, micro MSF, libreta."""
    p = [piernas(), torso(), credencial()]
    if pose == "micro":
        p += [brazo([(-22, 60), (-40, 104), (-38, 128)]),
              g([forma([(-14, -20), (14, -20), (14, 20), (-14, 20)], "#fff", w=2.6, temblor=.4),
                 trazo([(-8, -10), (8, -10)], w=1.5), trazo([(-8, -2), (8, -2)], w=1.5),
                 trazo([(-8, 6), (6, 6)], w=1.5)], -42, 118, rot=-14),
              brazo([(22, 60), (46, 92), (48, 64)]),
              micro(52, 44, ang=-12)]
    elif pose == "señala":
        p += [brazo([(-22, 60), (-38, 102), (-30, 132)]),
              brazo([(22, 60), (62, 70), (92, 58)])]
    elif pose == "cafe":
        p += [brazo([(-22, 60), (-38, 104), (-30, 132)]),
              brazo([(22, 60), (44, 96), (36, 74)]),
              taza(44, 66, "CAFÉ + CAOS")]
    p.append(cabeza())
    if gafas:
        p += [gafas_sol(), curva([(-8, 25), (2, 28), (12, 23)], w=3, temblor=.3)]
    else:
        p += [ojos_jay(), boca_plana()]
    return "".join(p)


def taza(x, y, letrero=None, s=1.0):
    partes = [forma([(-14, -16), (14, -16), (12, 16), (-12, 16)], "#fff", w=2.4, temblor=.4),
              curva([(14, -8), (24, -6), (24, 6), (13, 8)], w=2.4, temblor=.3),
              curva([(-5, -22), (-1, -30), (-5, -38)], w=1.8, temblor=.3),
              curva([(4, -22), (8, -30), (4, -38)], w=1.8, temblor=.3)]
    if letrero:
        a, b = (letrero.split(" + ") + [""])[:2]
        partes += [texto(0, -2, a, tam=8), texto(0, 6, "+", tam=7), texto(0, 13, b, tam=8)]
    return g(partes, x, y, s=s)


def dj_chisme():
    p = [piernas(), torso(fill="#3A3A3A"),
         trazo([(-8, 50), (0, 72), (8, 50)], w=2, color="#fff", temblor=.4),
         brazo([(-22, 60), (-52, 92), (-62, 62)]), brazo([(22, 60), (52, 92), (62, 62)]),
         cabeza(), gafas_sol(),
         curva([(-6, 26), (6, 28), (16, 20)], w=3, temblor=.3),
         # fedora
         forma([(-64, -34), (64, -36), (60, -26), (-60, -24)], TINTA, w=2.5, temblor=.6),
         forma([(-36, -32), (-30, -78), (0, -86), (30, -78), (36, -34)], TINTA, w=2.5, temblor=.6),
         forma([(-34, -44), (34, -46), (34, -36), (-34, -34)], ROSA, w=2, temblor=.4)]
    return "".join(p)


def la_interna():
    pelo = forma([(-56, 10), (-60, -40), (-30, -66), (10, -68), (50, -50), (60, -5), (58, 60),
                  (40, 74), (34, 40), (-34, 40), (-40, 74), (-58, 60)], GRIS_PELO, w=2.6)
    mechones = "".join(trazo([(x, -40), (x + 4, 10), (x - 2, 60)], w=1.4, color="#7a716b", temblor=1.4)
                       for x in (-50, -44, 46, 52))
    flequillo = forma([(-50, -16), (-38, -48), (0, -58), (36, -50), (52, -18), (20, -30), (-10, -26)], GRIS_PELO, w=2.4)
    p = [pelo, mechones, piernas(), torso(fill=MENTA),
         "".join(trazo([(-24, y), (24, y)], w=1.6, temblor=.8) for y in (80, 100, 120)),
         brazo([(-22, 60), (-48, 92), (-58, 56)]),
         forma([(-74, 22), (-52, 20), (-50, 60), (-72, 62)], AZUL, w=2.4, temblor=.4),
         brazo([(22, 60), (46, 104), (66, 98)]), micro(72, 82, ang=30, etiqueta=False),
         cabeza(), flequillo,
         punto(-17, 4, 4), punto(17, 4, 4),
         curva([(-12, 24), (0, 33), (13, 23)], w=3, temblor=.3)]
    return "".join(p)


def don_pepe():
    p = [piernas(), torso(),
         trazo([(-6, 50), (0, 62), (6, 50)], w=2, temblor=.3),
         brazo([(-22, 60), (-36, 104), (-14, 112)]),
         brazo([(22, 60), (40, 92), (16, 36)]),
         cabeza(),
         # pelo blanco a los lados, calvo arriba
         curva([(-50, -6), (-56, -20), (-48, -32)], w=2.4, temblor=.8),
         curva([(-46, 2), (-54, -12), (-50, -22)], w=1.6, temblor=.8),
         curva([(50, -6), (56, -20), (48, -32)], w=2.4, temblor=.8),
         curva([(-18, -38), (-12, -34)], w=1.6), curva([(12, -36), (20, -40)], w=1.6),
         ovalo(-17, 0, 12, 11, fill="#fff", w=2.4), ovalo(17, 0, 12, 11, fill="#fff", w=2.4),
         trazo([(-5, -1), (5, -1)], w=2.2, temblor=.2),
         punto(-15, 2, 3), punto(19, 2, 3),
         trazo([(-30, -20), (-8, -24)], w=2.4, temblor=.4), trazo([(8, -24), (30, -22)], w=2.4, temblor=.4),
         forma([(-30, 24), (-16, 13), (0, 18), (16, 13), (30, 24), (14, 22), (0, 27), (-14, 22)], GRIS, w=2.4, temblor=.5),
         texto(52, -56, "?", tam=34, fuente="gochi"), texto(70, -76, "?", tam=24, fuente="gochi")]
    return "".join(p)


def corazon(x, y, s=1.0, fill=ROSA):
    return g([forma([(0, 10), (-12, -2), (-12, -10), (-6, -14), (0, -8), (6, -14), (12, -10), (12, -2)], fill, w=2.2, temblor=.4)], x, y, s=s)


def la_influencer():
    pelo = forma([(-58, 10), (-60, -42), (-28, -66), (14, -68), (52, -48), (60, 0), (62, 88),
                  (40, 96), (34, 40), (-34, 40), (-40, 96), (-62, 88)], GRIS_PELO, w=2.6)
    p = [pelo,
         "".join(trazo([(x, -30), (x + 3, 30), (x - 2, 88)], w=1.4, color="#7a716b", temblor=1.4) for x in (-54, -46, 48, 55)),
         piernas(.8), torso(fill=ROSA),
         brazo([(-22, 60), (-50, 80), (-58, 44)]),
         trazo([(-58, 44), (-64, 28)], w=2.4), trazo([(-58, 44), (-52, 28)], w=2.4),
         brazo([(22, 60), (46, 40), (60, -6)]),
         forma([(52, -50), (76, -46), (72, -4), (48, -8)], "#fff", w=2.4, temblor=.4),
         corazon(62, -28, .6), cabeza(),
         forma([(-50, -18), (-34, -52), (6, -58), (40, -48), (54, -16), (14, -36)], GRIS_PELO, w=2.4),
         curva([(-26, 0), (-17, -7), (-8, 0)], w=3, temblor=.2), curva([(8, 0), (17, -7), (26, 0)], w=3, temblor=.2),
         trazo([(-26, -1), (-30, -5)], w=1.8), trazo([(26, -1), (30, -5)], w=1.8),
         forma([(-12, 20), (12, 20), (6, 32), (-6, 32)], TINTA, w=2, temblor=.3),
         ovalo(-30, 14, 6, 3.5, fill=ROSA, w=0.01, color=ROSA), ovalo(30, 14, 6, 3.5, fill=ROSA, w=0.01, color=ROSA),
         corazon(-82, -44, .9), corazon(-66, -84, .6), corazon(-96, 4, .5)]
    return "".join(p)


def el_editor(sentado=False):
    p = [] if sentado else [piernas()]
    p += [torso(fill=AZUL),
          trazo([(-6, 48), (0, 70), (6, 48)], w=2, temblor=.3),
          brazo([(-22, 60), (-30, 100), (18, 108)], mano=False),
          brazo([(22, 60), (32, 96), (-18, 104)], mano=False),
          taza(-34, 100, s=.85),
          cabeza(),
          trazo([(-30, -2), (-9, -2)], w=3.4, temblor=.3), trazo([(9, -2), (30, -2)], w=3.4, temblor=.3),
          '<path d="M-25 -2 A6 5 0 0 0 -13 -2 Z" fill="#1E1E1E"/>',
          '<path d="M13 -2 A6 5 0 0 0 25 -2 Z" fill="#1E1E1E"/>',
          trazo([(-31, -20), (-10, -11)], w=3, temblor=.3), trazo([(10, -11), (31, -20)], w=3, temblor=.3),
          curva([(-12, 30), (0, 23), (12, 30)], w=3, temblor=.3)]
    return "".join(p)


# ---------------------------------------------------------------- escenografía

def palmera(x, y, alto=170, s=1.0, ang=6):
    tronco = curva([(0, 0), (ang, -alto * .35), (ang * 2.2, -alto * .7), (ang * 3, -alto)], w=3, temblor=.5)
    anillos = "".join(trazo([(ang * k / 2.6 - 6, -alto * k / 8), (ang * k / 2.6 + 6, -alto * k / 8 - 2)], w=1.6)
                      for k in range(1, 8))
    tx, ty = ang * 3, -alto
    hojas = ""
    for dx, dy in ((-70, 10), (-55, 40), (60, 12), (52, 44), (-10, -30), (20, -26)):
        hojas += forma([(tx, ty), (tx + dx * .5, ty + dy * .5 - 14), (tx + dx, ty + dy), (tx + dx * .5, ty + dy * .5 - 2)],
                       MENTA, w=2.4, temblor=.8)
    return g([tronco, anillos, hojas], x, y, s=s)


def sol(x, y, r=26):
    rayos = "".join(trazo([(x + math.cos(a) * (r + 8), y + math.sin(a) * (r + 8)),
                           (x + math.cos(a) * (r + 20), y + math.sin(a) * (r + 20))], w=2.4)
                    for a in [k * math.pi / 4 for k in range(8)])
    return ovalo(x, y, r, r, fill=AMARILLO, w=2.6) + rayos


def auto(x, y, color=CORAL, s=1.0, espejo=False):
    partes = [forma([(-80, 0), (-78, -30), (-46, -34), (-30, -60), (30, -60), (48, -34), (80, -30), (82, 0)], color, w=2.8),
              forma([(-24, -54), (-2, -54), (-2, -36), (-38, -36)], AZUL, w=2.2, temblor=.4),
              forma([(4, -54), (26, -54), (40, -36), (4, -36)], AZUL, w=2.2, temblor=.4),
              ovalo(-46, 2, 15, 15, fill=TINTA, w=2.4), ovalo(-46, 2, 6, 6, fill="#fff", w=1.6),
              ovalo(48, 2, 15, 15, fill=TINTA, w=2.4), ovalo(48, 2, 6, 6, fill="#fff", w=1.6),
              ovalo(76, -20, 5, 4, fill=AMARILLO, w=1.6)]
    return g(partes, x, y, s=s, espejo=espejo)


def edificio_deco(x, y, ancho, alto, color, letrero=None):
    p = [forma([(0, 0), (0, -alto), (ancho * .2, -alto), (ancho * .2, -alto - 20), (ancho * .8, -alto - 20),
                (ancho * .8, -alto), (ancho, -alto), (ancho, 0)], color, w=2.6)]
    for fila in range(1, int(alto / 42)):
        for c in range(3):
            wx = ancho * (.15 + .27 * c)
            p.append(forma([(wx, -fila * 42), (wx + ancho * .16, -fila * 42), (wx + ancho * .16, -fila * 42 + 22),
                            (wx, -fila * 42 + 22)], "#fff", w=1.8, temblor=.4))
    for k in range(3):
        p.append(trazo([(ancho * .3, -alto - 6 - k * 5), (ancho * .7, -alto - 6 - k * 5)], w=1.6))
    if letrero:
        p.append(texto(ancho / 2, -alto + 22, letrero, tam=18, color=TINTA))
    return g(p, x, y)


def flamenco(x, y, s=1.0, silbato=True):
    """Flamenco agente de tránsito: cuerpo ovalado, cuello en S, ojos de Jay (no le sorprende nada)."""
    p = [trazo([(-6, 0), (-8, 92)], w=2.6), trazo([(10, 0), (22, 44), (4, 52)], w=2.6),
         ovalo(-8, 94, 10, 3.5, fill=ROSA, w=2),
         g([ovalo(0, 0, 46, 26, fill=ROSA, w=2.8)], 0, -14, rot=-12),
         forma([(-44, -6), (-62, -18), (-48, 4)], ROSA, w=2.4, temblor=.3),
         curva([(-14, -20), (4, -8), (22, -18)], w=1.8),
         curva([(30, -28), (42, -52), (24, -74), (30, -96)], w=9, temblor=.2, color=TINTA),
         curva([(30, -28), (42, -52), (24, -74), (30, -96)], w=5.5, temblor=.1, color=ROSA),
         ovalo(34, -104, 15, 13, fill=ROSA, w=2.6),
         forma([(46, -108), (66, -102), (62, -90), (47, -97)], "#fff", w=2.2, temblor=.3),
         forma([(58, -98), (66, -102), (63, -89)], TINTA, w=1.6, temblor=.2),
         trazo([(25, -110), (39, -110)], w=2.6, temblor=.2),
         '<path d="M28 -110 A4 4 0 0 0 36 -110 Z" fill="#1E1E1E"/>',
         # gorra de tránsito
         forma([(18, -114), (22, -128), (46, -128), (50, -114)], AZUL, w=2.2, temblor=.3),
         trazo([(14, -114), (54, -114)], w=2.6, temblor=.2)]
    if silbato:
        p += [forma([(60, -94), (76, -94), (76, -86), (60, -86)], AMARILLO, w=1.8, temblor=.2),
              trazo([(82, -98), (94, -104)], w=1.8), trazo([(82, -90), (96, -90)], w=1.8),
              trazo([(82, -82), (94, -76)], w=1.8)]
    return g(p, x, y, s=s)


def burbuja(x, y, ancho, alto, lineas, cola=(-30, 40), fill="#fff", tam=22):
    p = [forma([(x, y), (x + ancho, y), (x + ancho, y + alto), (x + ancho * .4, y + alto),
                (x + ancho * .4 + cola[0], y + alto + cola[1]), (x + ancho * .25, y + alto), (x, y + alto)], fill, w=2.6)]
    for i, l in enumerate(lineas):
        p.append(texto(x + ancho / 2, y + 30 + i * (tam + 4), l, tam=tam))
    return "".join(p)


def etiqueta(x, y, s, fill=ROSA, tam=24, ancho=None, rot=0):
    ancho = ancho or len(s) * tam * .52 + 34
    return g([forma([(-ancho / 2, -tam * .9), (ancho / 2, -tam * .95), (ancho / 2 + 2, tam * .55),
                     (-ancho / 2, tam * .6)], fill, w=2.4, temblor=.8),
              texto(0, tam * .3, s, tam=tam)], x, y, rot=rot)
