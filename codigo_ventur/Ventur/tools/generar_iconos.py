"""
Genera los iconos de los módulos como PNG blancos con fondo transparente.

Solo hace falta ejecutarlo si quieres cambiar los iconos (requiere Pillow).
La aplicación en sí NO necesita Pillow: lee los PNG ya generados.

    pip install pillow
    python tools/generar_iconos.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

SALIDA = Path(__file__).resolve().parent.parent / "src" / "assets"
LIENZO = 192          # se dibuja grande y se reduce (suaviza los bordes)
TAM_FINAL = 84        # 3x: en pantalla se muestran a 28 px y así se ven nítidos
TRAZO = 13
BLANCO = (255, 255, 255, 255)


class Pincel:
    def __init__(self):
        self.img = Image.new("RGBA", (LIENZO, LIENZO), (255, 255, 255, 0))
        self.d = ImageDraw.Draw(self.img)

    def _punto(self, x, y):
        r = TRAZO / 2
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=BLANCO)

    def linea(self, *pts, cerrada=False):
        pts = list(pts) + ([pts[0]] if cerrada else [])
        self.d.line(pts, fill=BLANCO, width=TRAZO, joint="curve")
        for p in pts:
            self._punto(*p)

    def rect(self, x1, y1, x2, y2, r=16):
        self.d.rounded_rectangle((x1, y1, x2, y2), radius=r, outline=BLANCO, width=TRAZO)

    def circulo(self, cx, cy, r, relleno=False):
        self.d.ellipse((cx - r, cy - r, cx + r, cy + r),
                       outline=None if relleno else BLANCO,
                       fill=BLANCO if relleno else None, width=TRAZO)

    def arco(self, caja, ini, fin):
        self.d.arc(caja, ini, fin, fill=BLANCO, width=TRAZO)

    def guardar(self, nombre):
        SALIDA.mkdir(parents=True, exist_ok=True)
        self.img.resize((TAM_FINAL, TAM_FINAL), Image.LANCZOS).save(SALIDA / f"icono_{nombre}.png")


def productos():
    p = Pincel()
    p.linea((96, 26), (156, 61), (156, 131), (96, 166), (36, 131), (36, 61), cerrada=True)
    p.linea((36, 61), (96, 96), (156, 61))
    p.linea((96, 96), (96, 166))
    p.guardar("productos")


def caja():
    p = Pincel()
    p.rect(24, 52, 168, 150, 20)
    p.linea((24, 90), (168, 90))
    p.circulo(134, 124, 8, relleno=True)
    p.guardar("caja")


def movimientos():
    p = Pincel()
    p.linea((62, 152), (62, 44))
    p.linea((36, 70), (62, 44), (88, 70))
    p.linea((130, 40), (130, 148))
    p.linea((104, 122), (130, 148), (156, 122))
    p.guardar("movimientos")


def alertas():
    p = Pincel()
    p.linea((96, 28), (170, 156), (22, 156), cerrada=True)
    p.linea((96, 72), (96, 112))
    p.circulo(96, 136, 6, relleno=True)
    p.guardar("alertas")


def historial():
    p = Pincel()
    p.circulo(96, 96, 66)
    p.linea((96, 56), (96, 98), (126, 116))
    p.guardar("historial")


def respaldo():
    p = Pincel()
    p.linea((96, 30), (96, 122))
    p.linea((58, 86), (96, 124), (134, 86))
    p.linea((36, 158), (156, 158))
    p.guardar("respaldo")


def reporte():
    p = Pincel()
    p.linea((52, 150), (52, 104))
    p.linea((96, 150), (96, 50))
    p.linea((140, 150), (140, 84))
    p.linea((28, 164), (164, 164))
    p.guardar("reporte")


def empleados():
    p = Pincel()
    p.circulo(80, 66, 26)
    p.arco((30, 108, 130, 208), 180, 360)
    p.circulo(140, 78, 18)
    p.arco((116, 112, 170, 170), 200, 340)
    p.guardar("empleados")


if __name__ == "__main__":
    for archivo in SALIDA.glob("icono_*.png"):   # borra iconos viejos (no toca los logos)
        archivo.unlink()
    for fn in (productos, caja, movimientos, alertas, empleados,
               historial, respaldo, reporte):
        fn()
    print(f"Iconos generados en {SALIDA}")
