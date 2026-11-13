"""Controlador: conecta modelos y vistas, y decide la navegación."""
from models.autenticacion import RepositorioUsuarios
from models.marca import VENTUR
from models.modulos import RepositorioModulos
from models.productos import Producto, RepositorioProductos
from models.venta import Venta
from views.formulario_producto import FormularioProducto
from views.tema import dinero
from views.ventana import Ventana
from views.vista_caja import VistaCaja
from views.vista_dashboard import VistaDashboard
from views.vista_login import VistaLogin
from views.vista_modulo import VistaModulo
from views.vista_productos import VistaProductos


class AppController:
    def __init__(self, page):
        # --- Modelos ---
        self.marca = VENTUR
        self.usuarios = RepositorioUsuarios()
        self.catalogo_modulos = RepositorioModulos()
        self.productos = RepositorioProductos()
        self.venta = Venta()          # la venta en curso persiste aunque salgas de Caja
        self.usuario = None           # quién inició sesión (None = nadie)

        # Vistas abiertas que el controlador necesita actualizar
        self._vista_login = None
        self._vista_caja = None
        self._vista_productos = None

        # --- Vista raíz ---
        self.ventana = Ventana(page, self.marca.nombre)
        self.mostrar_login()

    # ---------------- Sesión ----------------
    def mostrar_login(self):
        self.usuario = None
        self._vista_login = VistaLogin(self.marca.eslogan, al_entrar=self.iniciar_sesion)
        self.ventana.mostrar(self._vista_login)

    def iniciar_sesion(self, nombre_usuario, contrasena):
        if not nombre_usuario.strip() or not contrasena:
            self._vista_login.mostrar_error("Escribe tu usuario y tu contraseña.")
            return
        usuario = self.usuarios.autenticar(nombre_usuario, contrasena)
        if usuario is None:
            # Mismo mensaje exista o no el usuario, para no dar pistas.
            self._vista_login.mostrar_error("Usuario o contraseña incorrectos")
            return
        self.usuario = usuario
        self.mostrar_dashboard()

    def cerrar_sesion(self):
        self.venta.limpiar()          # la venta no pasa de una sesión a otra
        self.mostrar_login()

    # ---------------- Navegación ----------------
    def mostrar_dashboard(self):
        modulos = self.catalogo_modulos.para_rol(self.usuario.rol)
        insignias = {}
        alertas = self.productos.con_alerta()
        if alertas:
            insignias["alertas"] = f"{alertas} alerta{'' if alertas == 1 else 's'}"
        vista = VistaDashboard(self.usuario, modulos, insignias,
                               al_abrir_modulo=self.abrir_modulo,
                               al_cerrar_sesion=self.cerrar_sesion)
        self.ventana.mostrar(vista)

    def abrir_modulo(self, modulo):
        if modulo.solo_duena and not self.usuario.es_duena:
            return  # por seguridad, aunque el empleado nunca ve esas tarjetas
        if modulo.id == "productos":
            vista = VistaProductos(modulo, self.mostrar_dashboard,
                                   al_buscar=self.productos.buscar,
                                   al_categorias=self.productos.categorias,
                                   al_nuevo=self.productos_nuevo,
                                   al_editar=self.productos_editar)
            self._vista_productos = vista
        elif modulo.id == "caja":
            vista = VistaCaja(modulo, self.mostrar_dashboard,
                              al_agregar=self.caja_agregar,
                              al_cambiar_cantidad=self.caja_cambiar_cantidad,
                              al_quitar=self.caja_quitar,
                              al_vaciar=self.caja_vaciar,
                              al_cobrar=self.caja_cobrar,
                              venta=self.venta)
            self._vista_caja = vista
        else:
            vista = VistaModulo(modulo, al_volver=self.mostrar_dashboard)
        self.ventana.mostrar(vista)

    # ---------------- Productos ----------------
    def productos_nuevo(self):
        datos = {"id": self.productos.siguiente_id()}
        FormularioProducto(self.ventana, "Nuevo producto", datos, codigo_editable=True,
                           al_guardar=lambda d: self._guardar_producto(d, nuevo=True))

    def productos_editar(self, producto):
        datos = {"id": producto.id, "descripcion": producto.descripcion,
                 "categoria": producto.categoria, "precio": f"{producto.precio:.2f}",
                 "existencia": str(producto.existencia)}
        FormularioProducto(self.ventana, "Editar producto", datos, codigo_editable=False,
                           al_guardar=lambda d: self._guardar_producto(d, nuevo=False))

    def _guardar_producto(self, datos, nuevo):
        """Convierte lo escrito en el formulario y lo guarda. Devuelve un error o None."""
        try:
            precio = float(datos["precio"].replace("$", "").replace(",", "").strip())
        except ValueError:
            return "El precio debe ser un número, por ejemplo 320.50."
        try:
            existencia = int(datos["existencia"].strip())
        except ValueError:
            return "La existencia debe ser un número entero, por ejemplo 12."
        producto = Producto(
            id=datos["id"].strip(),
            descripcion=datos["descripcion"].strip(),
            categoria=datos["categoria"].strip().capitalize(),
            precio=precio,
            existencia=existencia,
        )
        try:
            self.productos.guardar(producto, nuevo)
        except ValueError as error:
            return str(error)
        self._vista_productos.refrescar()
        return None

    # ---------------- Caja ----------------
    def caja_agregar(self, texto):
        """Busca el producto y lo suma a la venta. Devuelve True si se agregó."""
        texto = texto.strip()
        if not texto:
            return self._caja_error("Escribe el código o el nombre del producto.")

        coincidencias = self.productos.buscar(texto)
        producto = self.productos.obtener(texto)
        if producto is None and len(coincidencias) == 1:
            producto = coincidencias[0]

        if not coincidencias:
            return self._caja_error(f"No se encontró «{texto}».")
        if producto is None:
            return self._caja_error(
                f"Hay {len(coincidencias)} coincidencias. Escribe el código o más del nombre.")
        if not self.venta.agregar(producto):
            if producto.existencia <= 0:
                return self._caja_error(f"{producto.descripcion} está agotado.")
            return self._caja_error(f"No hay más existencias de {producto.descripcion}.")

        self._vista_caja.actualizar(self.venta)
        return True

    def caja_cambiar_cantidad(self, id_producto, delta):
        if self.venta.cambiar_cantidad(id_producto, delta):
            self._vista_caja.actualizar(self.venta)
        elif delta > 0:
            linea = self.venta.linea(id_producto)
            nombre = linea.producto.descripcion if linea else "el producto"
            self._caja_error(f"No hay más existencias de {nombre}.")
        else:
            self._vista_caja.actualizar(self.venta)   # ya está en 1: usa "Quitar"

    def caja_quitar(self, id_producto):
        self.venta.quitar(id_producto)
        self._vista_caja.actualizar(self.venta)

    def caja_vaciar(self):
        self.venta.limpiar()
        self._vista_caja.actualizar(self.venta)

    def caja_cobrar(self):
        if self.venta.vacia:
            self._caja_error("Agrega al menos un producto para cobrar.")
            return
        for linea in self.venta.lineas:   # por si cambió el inventario mientras tanto
            if linea.cantidad > linea.producto.existencia:
                self._caja_error(
                    f"No hay existencias suficientes de {linea.producto.descripcion}.")
                return
        total = self.venta.total
        for linea in self.venta.lineas:
            self.productos.descontar(linea.producto.id, linea.cantidad)
        self.venta.limpiar()
        self._vista_caja.actualizar(self.venta)
        self.ventana.avisar(self.marca.nombre, f"Cobro realizado: {dinero(total)}")

    def _caja_error(self, mensaje):
        self._vista_caja.actualizar(self.venta, error=mensaje)
        return False
