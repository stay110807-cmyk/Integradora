"""Vista: panel de control (Ventur_Mockup_Panel_Duena.svg / Panel_Empleado.svg)."""
import flet as ft

from . import tema
from .componentes import boton, pildora, texto


def _pildora_hero(contenido, con_punto=False):
    elementos = []
    if con_punto:
        elementos.append(ft.Container(width=10, height=10, bgcolor=tema.VERDE_PUNTO,
                                      border_radius=ft.BorderRadius.all(5)))
    elementos.append(texto(contenido, 14, True, tema.BLANCO))
    return ft.Container(
        content=ft.Row(elementos, spacing=10, tight=True,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=tema.HERO_PILDORA,
        border_radius=ft.BorderRadius.all(16),
        padding=ft.Padding.symmetric(horizontal=18, vertical=7),
    )


def _encabezado(usuario, al_cerrar_sesion):
    izquierda = ft.Column(
        [
            _pildora_hero("Panel de control", con_punto=True),
            texto(f"Hola, {usuario.nombre}", 52, True, tema.BLANCO),
            texto(usuario.descripcion, 18, color=tema.HERO_TEXTO),
            _pildora_hero(f"Rol: {usuario.rol.value}"),
        ],
        spacing=4,
        tight=True,
    )
    derecha = ft.Column(
        [
            ft.Image(src="logo_claro_header.png", width=173, height=130),
            boton("Cerrar sesión", lambda e: al_cerrar_sesion(), estilo="claro",
                  ancho=176, alto=40, tam=15),
        ],
        spacing=8,
        tight=True,
        horizontal_alignment=ft.CrossAxisAlignment.END,
    )
    return ft.Container(
        content=ft.Row([izquierda, derecha], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                       vertical_alignment=ft.CrossAxisAlignment.START),
        bgcolor=tema.TINTA,
        border_radius=ft.BorderRadius.all(12),
        padding=ft.Padding.only(left=32, right=32, top=24, bottom=20),
    )


def _tarjeta(modulo, al_abrir, insignia):
    icono = ft.Container(
        content=ft.Image(src=f"icono_{modulo.id}.png", width=28, height=28),
        width=54, height=54, bgcolor=tema.TINTA,
        border_radius=ft.BorderRadius.all(8), alignment=ft.Alignment.CENTER,
    )
    contenido = [icono, ft.Text(modulo.titulo, size=20, weight=ft.FontWeight.BOLD,
                                color=tema.TINTA, expand=True, max_lines=2)]
    if insignia:
        contenido.append(pildora(insignia, tema.AVISO_FONDO, tema.AVISO_TEXTO))
    return ft.Container(
        content=ft.Row(contenido, spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        height=88,
        padding=ft.Padding.symmetric(horizontal=20, vertical=0),
        bgcolor=tema.TARJETA,
        border=ft.Border.all(1, tema.BORDE),
        border_radius=ft.BorderRadius.all(8),
        ink=True,
        on_click=lambda e: al_abrir(modulo),
        # 1 columna en teléfonos, 2 en tabletas chicas, 3 en tabletas grandes
        col={"xs": 12, "md": 6, "lg": 4},
    )


class VistaDashboard:
    def __init__(self, usuario, modulos, insignias, al_abrir_modulo, al_cerrar_sesion):
        """insignias: {id_modulo: texto}, p. ej. {"alertas": "2 alertas"}"""
        tarjetas = ft.ResponsiveRow(
            [_tarjeta(m, al_abrir_modulo, insignias.get(m.id)) for m in modulos],
            spacing=36,
            run_spacing=20,
        )
        self.control = ft.Container(
            bgcolor=tema.FONDO,
            expand=True,
            padding=ft.Padding.only(left=40, right=40, top=32, bottom=24),
            content=ft.Column(
                [_encabezado(usuario, al_cerrar_sesion), tarjetas],
                spacing=24,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )
