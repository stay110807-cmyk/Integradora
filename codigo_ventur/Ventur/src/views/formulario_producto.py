"""Vista: diálogo para crear o editar un producto (flujo "Formulario" del mapa de navegación)."""
import flet as ft

from . import tema
from .componentes import Aviso, boton, campo, texto


class FormularioProducto:
    """Diálogo modal. al_guardar(datos) devuelve un mensaje de error, o None si todo salió bien."""

    def __init__(self, ventana, titulo, datos, codigo_editable, al_guardar):
        self._ventana = ventana
        self._al_guardar = al_guardar
        self._aviso = Aviso()

        self._campos = {
            "id": campo("Ej. 006", datos.get("id", ""), solo_lectura=not codigo_editable,
                        expand=True),
            "categoria": campo("Ej. Ropa", datos.get("categoria", ""), expand=True),
            "descripcion": campo("Ej. Camisa Deportiva M", datos.get("descripcion", ""),
                                 autofocus=True),
            "precio": campo("0.00", datos.get("precio", ""), expand=True,
                            teclado=ft.KeyboardType.NUMBER),
            "existencia": campo("0", datos.get("existencia", ""), expand=True,
                                teclado=ft.KeyboardType.NUMBER),
        }

        def con_etiqueta(etiqueta, control, **opciones):
            return ft.Column([texto(etiqueta, 15, True), control], spacing=6, **opciones)

        c = self._campos
        contenido = ft.Column(
            [
                self._aviso.control,
                ft.Row([con_etiqueta("Código", c["id"], expand=True),
                        con_etiqueta("Categoría", c["categoria"], expand=True)], spacing=16),
                con_etiqueta("Descripción", c["descripcion"]),
                ft.Row([con_etiqueta("Precio de venta", c["precio"], expand=True),
                        con_etiqueta("Existencia", c["existencia"], expand=True)], spacing=16),
            ],
            spacing=16,
            tight=True,
            width=480,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        self._dialogo = ft.AlertDialog(
            modal=True,
            title=texto(titulo, 26, True),
            content=contenido,
            actions=[
                boton("Cancelar", lambda e: ventana.cerrar_dialogo(), estilo="secundario",
                      ancho=130, alto=48),
                boton("Guardar", self._guardar, ancho=150, alto=48),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=tema.TARJETA,
        )
        ventana.mostrar_dialogo(self._dialogo)

    def _guardar(self, e):
        datos = {clave: (control.value or "") for clave, control in self._campos.items()}
        error = self._al_guardar(datos)
        if error:
            self._aviso.mostrar(error, "error")
        else:
            self._ventana.cerrar_dialogo()
