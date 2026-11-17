"""Punto de entrada de Ventur.

    flet run              (desde la carpeta ventur, con la app en la computadora)
    flet run --android    (para verla en tu tableta con la app Flet)
    flet build apk        (para generar el APK)
"""
import flet as ft

from controllers.app_controller import AppController


def main(page: ft.Page):
    AppController(page)


ft.run(main)
