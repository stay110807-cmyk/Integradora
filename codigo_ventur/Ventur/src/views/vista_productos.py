"""Vista: módulo Productos (Ventur_Mockup_Productos.svg)."""
import flet as ft

from models.productos import AGOTADO, DISPONIBLE, STOCK_BAJO

from . import tabla, tema
from .componentes import boton, campo, pildora, selector, texto
from .tabla import Columna
from .vista_base import VistaBase

TODAS = "Todas las categorías"

# estado -> (texto de la píldora, fondo, color del texto, color de la barra lateral)
_ESTADOS = {
    DISPONIBLE: ("Disponible", tema.OK_FONDO, tema.OK_TEXTO, None),
    STOCK_BAJO: ("Stock bajo", tema.AVISO_FONDO, tema.AVISO_TEXTO, tema.AVISO_BORDE),
    AGOTADO: ("Agotado", tema.ERROR_FONDO, tema.ERROR_TEXTO, tema.ROJO),
}

_COLUMNAS = [
    Columna("ID", 1),
    Columna("Descripción", 4),
    Columna("Categoría", 2),
    Columna("Precio venta", 2, "der"),
    Columna("Existencia", 2, "centro"),
    Columna("Estado", 2),
    Columna("Acciones", 2, "centro"),
]


class VistaProductos(VistaBase):
    def __init__(self, modulo, al_volver, al_buscar, al_categorias, al_nuevo, al_editar):
        super().__init__(modulo, al_volver)
        self._al_buscar = al_buscar
        self._al_categorias = al_categorias
        self._al_editar = al_editar

        self._busqueda = campo("Ej. 001, Camisa, Ropa", buscador=True, expand=True,
                               al_cambiar=lambda e: self._llenar())
        self._categoria = selector([TODAS] + list(al_categorias()), TODAS,
                                   lambda e: self._llenar())
        self._filas = tabla.cuerpo_con_scroll()
        self._resumen = texto("", 15, color=tema.TINTA_SUAVE)

        superior = ft.Column(
            [
                texto("Buscar por código, nombre o categoría", 16, True),
                ft.Row(
                    [self._busqueda, self._categoria,
                     boton("Nuevo producto", lambda e: al_nuevo(), ancho=160, alto=48)],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=8,
        )
        self.cuerpo.controls = [
            ft.Container(content=superior, padding=ft.Padding.only(left=24, right=24, top=24, bottom=20)),
            ft.Container(
                content=ft.Column([tabla.encabezado(_COLUMNAS), self._filas], spacing=0,
                                  expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                padding=ft.Padding.symmetric(horizontal=24, vertical=0),
                expand=True,
            ),
            ft.Container(content=self._resumen,
                         padding=ft.Padding.only(left=24, right=24, top=14, bottom=24)),
        ]
        self._llenar()

    def refrescar(self):
        """Vuelve a leer los productos (después de crear o editar uno)."""
        opciones = [TODAS] + list(self._al_categorias())
        self._categoria.options = [ft.DropdownOption(key=o, text=o) for o in opciones]
        if self._categoria.value not in opciones:
            self._categoria.value = TODAS
        self._llenar()

    def _fila(self, indice, p):
        etiqueta, fondo, color, acento = _ESTADOS[p.estado]
        return tabla.fila(_COLUMNAS, [
            texto(p.id),
            texto(p.descripcion, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            texto(p.categoria, color=tema.TINTA_SUAVE),
            texto(tema.dinero(p.precio)),
            texto(str(p.existencia), negrita=True),
            pildora(etiqueta, fondo, color),
            boton("Editar", lambda e: self._al_editar(p), estilo="secundario",
                  ancho=96, alto=32, tam=14),
        ], indice, alto=56, acento=acento)

    def _llenar(self):
        categoria = self._categoria.value
        productos = self._al_buscar(self._busqueda.value or "",
                                    None if categoria in (None, TODAS) else categoria)
        self._filas.controls = [self._fila(i, p) for i, p in enumerate(productos)]

        total = len(productos)
        alertas = sum(1 for p in productos if p.con_alerta)
        if total == 0:
            self._resumen.value = "No se encontraron productos."
        else:
            self._resumen.value = (f"{total} producto{'' if total == 1 else 's'} · "
                                   f"{alertas} con alerta de existencias")
