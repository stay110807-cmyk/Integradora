"""Vista: pantalla provisional para los módulos que todavía no se construyen."""
import flet as ft

from . import tema
from .componentes import texto
from .vista_base import VistaBase


class VistaModulo(VistaBase):
    def __init__(self, modulo, al_volver):
        super().__init__(modulo, al_volver)
        icono = ft.Container(
            content=ft.Image(src=f"icono_{modulo.id}.png", width=28, height=28),
            width=64, height=64, bgcolor=tema.TINTA,
            border_radius=ft.BorderRadius.all(12), alignment=ft.Alignment.CENTER,
        )
        self.cuerpo.controls = [
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        icono,
                        texto("Este módulo todavía no está disponible.", 18, True),
                        texto("Se construirá en una siguiente fase.", 15, color=tema.TINTA_SUAVE),
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                ),
            )
        ]
