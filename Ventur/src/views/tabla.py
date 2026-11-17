"""Tabla hecha con filas y columnas: encabezado oscuro, filas alternadas y widgets en las celdas."""
from dataclasses import dataclass

import flet as ft

from . import tema
from .componentes import texto

ANCHO_ACENTO = 5   # barra de color al inicio de cada fila (stock bajo / agotado)

_ALINEACION = {
    "izq": ft.Alignment.CENTER_LEFT,
    "centro": ft.Alignment.CENTER,
    "der": ft.Alignment.CENTER_RIGHT,
}


@dataclass(frozen=True)
class Columna:
    titulo: str
    flex: int = 1          # proporción del ancho que ocupa la columna
    ancla: str = "izq"     # "izq", "centro" o "der"


def _celda(contenido, columna):
    return ft.Container(
        content=contenido,
        expand=columna.flex,
        alignment=_ALINEACION[columna.ancla],
        padding=ft.Padding.symmetric(horizontal=12, vertical=0),
    )


def encabezado(columnas):
    celdas = [ft.Container(width=ANCHO_ACENTO)]
    celdas += [_celda(texto(c.titulo, 15, True, tema.BLANCO), c) for c in columnas]
    return ft.Container(
        content=ft.Row(celdas, spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        height=44,
        bgcolor=tema.TINTA,
    )


def fila(columnas, celdas, indice, alto=56, acento=None):
    """celdas: un control por columna. indice: para alternar el color de fondo."""
    contenido = [ft.Container(width=ANCHO_ACENTO, bgcolor=acento)]
    contenido += [_celda(c, col) for c, col in zip(celdas, columnas)]
    return ft.Container(
        content=ft.Row(contenido, spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        height=alto,
        bgcolor=tema.TARJETA if indice % 2 == 0 else tema.FILA_ALTERNA,
    )


def cuerpo_con_scroll():
    """Columna que se desplaza cuando hay más filas de las que caben."""
    return ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
