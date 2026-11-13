"""Ventana principal: muestra una vista a la vez y se encarga de los diálogos."""
import flet as ft

from . import tema
from .componentes import boton, texto


class Ventana:
    def __init__(self, page: ft.Page, titulo: str):
        self.page = page
        page.title = titulo
        page.padding = 0
        page.spacing = 0
        page.bgcolor = tema.FONDO
        page.theme_mode = ft.ThemeMode.LIGHT
        self._tamano_de_escritorio(page)

        self._raiz = ft.Container(expand=True, bgcolor=tema.FONDO)
        # SafeArea evita que el contenido quede bajo la barra de estado / navegación de Android
        page.add(ft.SafeArea(content=self._raiz, expand=True))
        self.vista_actual = None

    @staticmethod
    def _tamano_de_escritorio(page):
        """Solo afecta cuando pruebas en la computadora; en Android se ignora."""
        try:
            page.window.width = 1280
            page.window.height = 800
        except Exception:  # noqa: BLE001 - si la plataforma no lo soporta, no pasa nada
            pass

    def mostrar(self, vista):
        """vista: cualquier objeto con un atributo .control (el control raíz de la pantalla)."""
        self._raiz.content = vista.control
        self.vista_actual = vista

    # ---- Diálogos ----
    def mostrar_dialogo(self, dialogo):
        self.page.show_dialog(dialogo)

    def cerrar_dialogo(self):
        self.page.pop_dialog()

    def avisar(self, titulo, mensaje):
        dialogo = ft.AlertDialog(
            title=texto(titulo, 22, True),
            content=texto(mensaje, 16),
            actions=[boton("Aceptar", lambda e: self.cerrar_dialogo(), ancho=120, alto=44)],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=tema.TARJETA,
        )
        self.mostrar_dialogo(dialogo)
