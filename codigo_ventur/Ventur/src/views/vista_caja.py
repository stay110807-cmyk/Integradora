"""Vista: módulo Caja (Ventur_Mockup_Caja.svg)."""
import flet as ft

from models.productos import UMBRAL_STOCK_BAJO

from . import tabla, tema
from .componentes import Aviso, boton, campo, enfocar, texto
from .tabla import Columna
from .vista_base import VistaBase

_COLUMNAS = [
    Columna("Producto", 5),
    Columna("Cant.", 3, "centro"),
    Columna("Precio", 2, "der"),
    Columna("Subtotal", 2, "der"),
    Columna("Quitar", 2, "centro"),
]


class VistaCaja(VistaBase):
    def __init__(self, modulo, al_volver, al_agregar, al_cambiar_cantidad,
                 al_quitar, al_vaciar, al_cobrar, venta):
        super().__init__(modulo, al_volver)
        self._al_agregar = al_agregar
        self._al_cambiar_cantidad = al_cambiar_cantidad
        self._al_quitar = al_quitar

        self._busqueda = campo("Escribe o escanea el código", buscador=True, expand=True,
                               autofocus=True, al_enviar=self._agregar)
        self._filas = tabla.cuerpo_con_scroll()
        self._aviso = Aviso()
        self._total = texto("Total: $0.00", 36, True)
        self._boton_cobrar = boton("Procesar cobro ($0.00)", lambda e: al_cobrar(),
                                   ancho=300, alto=56, tam=17)

        captura = ft.Column(
            [
                texto("Código o nombre del producto", 16, True),
                ft.Row([self._busqueda, boton("Agregar", self._agregar, ancho=136, alto=48)],
                       spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ],
            spacing=8,
        )
        cobro = ft.Row(
            [
                self._total,
                ft.Row([boton("Vaciar", lambda e: al_vaciar(), estilo="secundario", ancho=140,
                              alto=56, tam=17), self._boton_cobrar], spacing=20),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.cuerpo.controls = [
            ft.Container(content=captura,
                         padding=ft.Padding.only(left=24, right=24, top=24, bottom=20)),
            ft.Container(
                content=ft.Column([tabla.encabezado(_COLUMNAS), self._filas], spacing=0,
                                  expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                padding=ft.Padding.symmetric(horizontal=24, vertical=0),
                expand=True,
            ),
            ft.Container(content=self._aviso.control,
                         padding=ft.Padding.only(left=24, right=24, top=16, bottom=0)),
            ft.Container(height=2, bgcolor=tema.BORDE, margin=ft.Margin.only(left=24, right=24, top=16)),
            ft.Container(content=cobro, padding=ft.Padding.symmetric(horizontal=24, vertical=20)),
        ]
        self.actualizar(venta)

    async def _agregar(self, e):
        # El controlador responde True si se agregó; entonces limpiamos el campo.
        if self._al_agregar(self._busqueda.value or ""):
            self._busqueda.value = ""
        await enfocar(self._busqueda)

    # ---- Celdas ----
    def _stepper(self, linea):
        id_producto = linea.producto.id
        return ft.Row(
            [
                boton("−", lambda e: self._al_cambiar_cantidad(id_producto, -1), estilo="campo",
                      ancho=36, alto=36, tam=22),
                ft.Container(content=texto(str(linea.cantidad), 17, True), width=36,
                             alignment=ft.Alignment.CENTER),
                boton("+", lambda e: self._al_cambiar_cantidad(id_producto, +1), estilo="campo",
                      ancho=36, alto=36, tam=22),
            ],
            spacing=4,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _fila(self, indice, linea):
        p = linea.producto
        id_producto = p.id
        return tabla.fila(_COLUMNAS, [
            texto(p.descripcion, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            self._stepper(linea),
            texto(tema.dinero(p.precio)),
            texto(tema.dinero(linea.subtotal), negrita=True),
            boton("Quitar", lambda e: self._al_quitar(id_producto), estilo="peligro",
                  ancho=96, alto=32, tam=14),
        ], indice, alto=60)

    # ---- Actualización desde el modelo ----
    def actualizar(self, venta, error=""):
        """Redibuja tabla, total y avisos a partir del modelo Venta."""
        self._filas.controls = [self._fila(i, linea) for i, linea in enumerate(venta.lineas)]
        self._total.value = f"Total: {tema.dinero(venta.total)}"
        self._boton_cobrar.content.value = f"Procesar cobro ({tema.dinero(venta.total)})"

        if error:
            self._aviso.mostrar(error, "error")
            return
        avisos = self._avisos_de_stock(venta)
        if avisos:
            self._aviso.mostrar(avisos, "aviso")
        else:
            self._aviso.ocultar()

    @staticmethod
    def _avisos_de_stock(venta):
        lineas = []
        for linea in venta.lineas:
            if linea.restantes > UMBRAL_STOCK_BAJO:
                continue
            nombre = linea.producto.descripcion
            if linea.restantes <= 0:
                lineas.append(f"Agotado: con esta venta se terminan las piezas de {nombre}.")
            elif linea.restantes == 1:
                lineas.append(f"Stock bajo: después de esta venta queda 1 pieza de {nombre}.")
            else:
                lineas.append(f"Stock bajo: después de esta venta quedan "
                              f"{linea.restantes} piezas de {nombre}.")
        return "\n".join(lineas)
