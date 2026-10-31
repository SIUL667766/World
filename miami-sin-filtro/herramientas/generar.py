"""Genera las láminas de Miami Sin Filtro (SVG + PNG).

Uso:  python3 herramientas/generar.py
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dibujo import *  # noqa: E402,F401,F403

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SALIDA = os.path.join(RAIZ, "laminas")


def guardar(nombre, ancho, alto, contenido):
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, nombre + ".svg")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(documento(ancho, alto, contenido))
    return ruta, ancho, alto


def hoja_personajes():
    semilla(11)
    c = [texto(900, 70, "EL MUNDO DE: MIAMI SIN FILTRO", tam=56, fuente="gochi"),
         etiqueta(900, 118, "PERSONAJES · HOJA DE MODELO", fill=ROSA, tam=26)]
    fichas = [
        ("JAY FONTANA", ["Periodista independiente.", "\"Si es raro, es noticia.\""], jay(), MENTA),
        ("DJ CHISME", ["Amigo y fuente número uno.", "Sabe todo, siempre."], dj_chisme(), LAVANDA),
        ("LA INTERNA", ["Joven, rápida e irónica.", "Domina TikTok y el caos."], la_interna(), MENTA),
        ("DON PEPE", ["Taxista filósofo.", "Tiene la mejor información."], don_pepe(), AMARILLO),
        ("LA INFLUENCER", ["Quiere salir en la noticia,", "pero siempre sale mal."], la_influencer(), ROSA),
        ("EL EDITOR", ["Cínico, brillante y sin", "paciencia para nadie."], el_editor(), AZUL),
    ]
    for i, (nombre, desc, dibujo, color) in enumerate(fichas):
        x = 150 + i * 300
        c.append(forma([(x - 135, 170), (x + 135, 168), (x + 137, 700), (x - 133, 702)], "#fff", w=2.2, temblor=1.5,
                       color="#b8b2aa"))
        c.append(g([dibujo], x, 290, s=1.15))
        c.append(etiqueta(x, 610, nombre, fill=color, tam=24))
        for k, l in enumerate(desc):
            c.append(texto(x, 652 + k * 26, l, tam=21))
    return guardar("01-personajes", 1800, 740, c)


def jay_modos():
    semilla(23)
    c = [texto(700, 64, "JAY FONTANA · SUS TRES MODOS", tam=48, fuente="gochi")]
    modos = [("CALLE", "Micro MSF, credencial y libreta.", "\"Si es raro, es noticia.\"", jay("micro")),
             ("ON AIR", "Gafas negras: modo programa.", "Solo en intros y cierres.", jay("micro", gafas=True)),
             ("ESTUDIO", "7:00 AM. Café, titulares y caos.", "Trabaja mejor con café.", jay("cafe"))]
    for i, (titulo, a, b, dib) in enumerate(modos):
        x = 240 + i * 460
        c.append(g([dib], x, 210, s=1.35))
        c.append(etiqueta(x, 590, titulo, fill=[MENTA, ROSA, AMARILLO][i], tam=28))
        c.append(texto(x, 636, a, tam=22))
        c.append(texto(x, 664, b, tam=22))
    return guardar("02-jay-modos", 1400, 700, c)


def episodio1_portada():
    """EP. 01 · Solo en Miami: un flamenco dirige el tráfico en Ocean Drive."""
    semilla(5)
    c = [sol(1230, 210, 30),
         edificio_deco(40, 530, 220, 210, MENTA, "HOTEL"),
         edificio_deco(290, 530, 180, 250, ROSA),
         edificio_deco(880, 530, 190, 200, LAVANDA, "CAFÉ"),
         edificio_deco(1100, 530, 170, 230, AMARILLO),
         palmera(560, 540, 230, ang=8), palmera(1320, 540, 220, ang=-7), palmera(20, 545, 190, ang=5),
         forma([(0, 530), (1400, 528), (1400, 800), (0, 800)], "#E9E3D8", w=0.01, color="#E9E3D8"),
         trazo([(0, 530), (1400, 528)], w=3),
         "".join(trazo([(x, 660), (x + 70, 660)], w=5, color="#fff", temblor=.4) for x in range(40, 1400, 160)),
         auto(200, 650, CORAL), auto(1060, 650, AZUL, espejo=True), auto(1260, 770, AMARILLO, espejo=True, s=.9),
         flamenco(760, 600, s=1.35),
         g([jay("micro")], 400, 520, s=1.05),
         burbuja(480, 330, 260, 86, ["Aquí todo normal.", "Bueno... casi todo."], cola=(-60, 50)),
         forma([(330, 46), (1070, 40), (1076, 150), (326, 156)], "#fff", w=2.6),
         texto(700, 98, "UN FLAMENCO DIRIGE EL TRÁFICO", tam=44, fuente="gochi"),
         texto(700, 140, "EN OCEAN DRIVE", tam=36, fuente="gochi"),
         etiqueta(150, 60, "SOLO EN MIAMI", fill=ROSA, tam=32, rot=-4),
         etiqueta(1250, 70, "EP. 01", fill=AMARILLO, tam=30, rot=4),
         forma([(20, 720), (290, 720), (290, 780), (20, 780)], TINTA, w=2),
         texto(155, 760, "MIAMI SIN FILTRO NEWS", tam=22, color="#fff")]
    return guardar("03-ep01-portada", 1400, 800, c)


def renderizar(laminas):
    script = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
              "for(const [r,w,h] of %s){const p=await b.newPage({viewport:{width:w,height:h}});"
              "await p.goto('file://'+r);await p.waitForTimeout(300);"
              "await p.screenshot({path:r.replace(/\\.svg$/,'.png')});await p.close();}await b.close();})()"
              % repr([[os.path.abspath(r), w, h] for r, w, h in laminas]).replace("'", '"'))
    subprocess.run(["node", "-e", script], check=True)


if __name__ == "__main__":
    renderizar([hoja_personajes(), jay_modos(), episodio1_portada()])
    print("Listo:", sorted(os.listdir(SALIDA)))
