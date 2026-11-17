"""Vista base de los módulos: botón "Volver al panel", título y un recuadro blanco (cuerpo)."""
import flet as ft

from . import tema
from .componentes import boton, texto


class VistaBase:
    """Las pantallas de cada módulo heredan de aquí y llenan self.cuerpo.controls."""

    def __init__(self, modulo, al_volver):
        barra = ft.Row(
            [
                boton("Volver al panel", lambda e: al_volver(), ancho=150, alto=52),
                ft.Column(
                    [texto(modulo.titulo, 32, True), texto(modulo.descripcion, 17, color=tema.TINTA_SUAVE)],
                    spacing=0,
                ),
            ],
            spacing=30,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.cuerpo = ft.Column(spacing=0, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        tarjeta = ft.Container(
            content=self.cuerpo,
            bgcolor=tema.TARJETA,
            border=ft.Border.all(1, tema.BORDE),
            border_radius=ft.BorderRadius.all(8),
            expand=True,
        )
        self.control = ft.Container(
            content=ft.Column([barra, tarjeta], spacing=36, expand=True),
            padding=ft.Padding.only(left=40, right=40, top=32, bottom=40),
            bgcolor=tema.FONDO,
            expand=True,
        )
