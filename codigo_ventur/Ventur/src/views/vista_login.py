"""Vista: inicio de sesión (Ventur_Mockup_Login.svg)."""
import flet as ft

from . import tema
from .componentes import Aviso, boton, campo, espacio, texto


class VistaLogin:
    def __init__(self, eslogan, al_entrar):
        self._al_entrar = al_entrar
        self._aviso = Aviso()
        self._usuario = campo("Tu usuario", autofocus=True, al_enviar=self._entrar)
        self._contrasena = campo("Tu contraseña", clave=True, al_enviar=self._entrar)

        tarjeta = ft.Container(
            width=450,
            padding=ft.Padding.all(40),
            bgcolor=tema.TARJETA,
            border=ft.Border.all(1, tema.BORDE),
            border_radius=ft.BorderRadius.all(12),
            content=ft.Column(
                [
                    ft.Row([ft.Image(src="logo_oscuro_login.png", width=117, height=88)],
                           alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([texto(eslogan, 15, color=tema.TINTA_SUAVE)],
                           alignment=ft.MainAxisAlignment.CENTER),
                    espacio(18),
                    texto("Iniciar sesión", 28, True),
                    espacio(2),
                    self._aviso.control,
                    texto("Usuario", 16, True),
                    self._usuario,
                    espacio(6),
                    texto("Contraseña", 16, True),
                    self._contrasena,
                    espacio(14),
                    boton("Entrar", self._entrar, alto=52, tam=17),
                    espacio(6),
                    ft.Row([texto("Funciona sin conexión a internet", 14, color=tema.TINTA_SUAVE)],
                           alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=6,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )
        # Con scroll, la tarjeta sigue siendo usable cuando el teclado ocupa media pantalla.
        self.control = ft.Container(
            bgcolor=tema.FONDO,
            expand=True,
            content=ft.Column(
                [tarjeta],
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
        )

    def _entrar(self, e):
        self._al_entrar(self._usuario.value or "", self._contrasena.value or "")

    def mostrar_error(self, mensaje):
        """El controlador lo llama cuando las credenciales no son válidas."""
        self._aviso.mostrar(mensaje, "error")
        self._contrasena.value = ""
