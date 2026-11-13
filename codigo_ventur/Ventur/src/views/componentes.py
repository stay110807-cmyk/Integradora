"""Piezas reutilizables: texto, botón, píldora, aviso, campo y selector."""
import inspect

import flet as ft

from . import tema

# estilo de botón: (fondo, color del texto, color del borde o None)
_ESTILOS_BOTON = {
    "primario": (tema.TINTA, tema.BLANCO, None),
    "secundario": (tema.TARJETA, tema.TINTA, tema.TINTA),
    "peligro": (tema.TARJETA, tema.ROJO, tema.ROJO),
    "campo": (tema.TARJETA, tema.TINTA, tema.CAMPO_BORDE),
    "claro": (tema.TINTA, tema.BLANCO, tema.BLANCO),   # sobre el banner oscuro
}


def texto(valor, tam=16, negrita=False, color=tema.TINTA, **opciones):
    return ft.Text(valor, size=tam, color=color,
                   weight=ft.FontWeight.BOLD if negrita else None, **opciones)


def espacio(alto):
    return ft.Container(height=alto)


def boton(contenido, al_click, estilo="primario", ancho=None, alto=44, tam=16):
    """Botón con esquinas redondeadas. al_click recibe el evento (puede ser async)."""
    fondo, color, borde = _ESTILOS_BOTON[estilo]
    return ft.Container(
        content=ft.Text(contenido, size=tam, weight=ft.FontWeight.BOLD, color=color),
        width=ancho,
        height=alto,
        bgcolor=fondo,
        border=ft.Border.all(2, borde) if borde else None,
        border_radius=ft.BorderRadius.all(6),
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.symmetric(horizontal=24, vertical=0),
        ink=True,
        on_click=al_click,
    )


def pildora(contenido, fondo, color, tam=14):
    """Etiqueta redonda (estado de un producto, insignias)."""
    return ft.Container(
        content=ft.Text(contenido, size=tam, weight=ft.FontWeight.BOLD, color=color),
        bgcolor=fondo,
        border_radius=ft.BorderRadius.all(16),
        padding=ft.Padding.symmetric(horizontal=16, vertical=5),
    )


class Aviso:
    """Franja de aviso: roja = error, amarilla = advertencia. Empieza oculta."""

    _ESTILOS = {
        "error": (tema.ERROR_FONDO, tema.ERROR_BORDE, tema.ERROR_TEXTO),
        "aviso": (tema.AVISO_FONDO, tema.AVISO_BORDE, tema.AVISO_TEXTO),
    }

    def __init__(self):
        self._texto = ft.Text("", size=15, weight=ft.FontWeight.BOLD)
        self.control = ft.Container(
            content=self._texto,
            padding=ft.Padding.symmetric(horizontal=20, vertical=13),
            border_radius=ft.BorderRadius.all(6),
            visible=False,
        )

    def mostrar(self, mensaje, tipo="error"):
        fondo, borde, color = self._ESTILOS[tipo]
        self._texto.value = mensaje
        self._texto.color = color
        self.control.bgcolor = fondo
        self.control.border = ft.Border.all(1, borde)
        self.control.visible = True

    def ocultar(self):
        self.control.visible = False


def campo(sugerencia="", valor="", clave=False, solo_lectura=False, buscador=False,
          al_cambiar=None, al_enviar=None, teclado=None, autofocus=False, expand=False):
    """Campo de texto con el estilo de los mockups.

    al_cambiar / al_enviar reciben el evento (e.control.value trae el texto).
    clave=True oculta lo escrito y muestra el ojito para revelarlo.
    """
    opciones = {}
    if buscador:
        opciones["prefix_icon"] = ft.Icons.SEARCH
    if teclado is not None:
        opciones["keyboard_type"] = teclado
    if al_cambiar is not None:
        opciones["on_change"] = al_cambiar
    if al_enviar is not None:
        opciones["on_submit"] = al_enviar
    return ft.TextField(
        value=valor,
        hint_text=sugerencia,
        password=clave,
        can_reveal_password=clave,
        read_only=solo_lectura,
        filled=True,
        bgcolor=tema.CAMPO_SOLO_LECTURA if solo_lectura else tema.TARJETA,
        border=tema.borde_campo(),
        text_size=16,
        color=tema.TINTA,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        autofocus=autofocus,
        expand=expand,
        **opciones,
    )


def selector(opciones, valor, al_cambiar, ancho=220):
    """Lista desplegable. al_cambiar recibe el evento (e.control.value trae la opción)."""
    return ft.Dropdown(
        width=ancho,
        value=valor,
        options=[ft.DropdownOption(key=o, text=o) for o in opciones],
        border=tema.borde_campo(),
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        on_select=al_cambiar,
    )


async def enfocar(control):
    """Pone el cursor en un campo (focus() es asíncrono en Flet 1.x)."""
    resultado = control.focus()
    if inspect.isawaitable(resultado):
        await resultado
