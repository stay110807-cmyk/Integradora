"""Modelo: la venta en curso (el carrito de la Caja)."""
from dataclasses import dataclass
from typing import Dict, List, Optional

from .database import BaseDatos
from .productos import Producto


@dataclass
class LineaVenta:
    producto: Producto
    cantidad: int = 1

    @property
    def subtotal(self) -> float:
        return self.producto.precio * self.cantidad

    @property
    def restantes(self) -> int:
        """Piezas que quedarían en inventario si se cobrara esta venta."""
        return self.producto.existencia - self.cantidad


class Venta:
    def __init__(self):
        self._lineas: Dict[str, LineaVenta] = {}

    @property
    def lineas(self) -> List[LineaVenta]:
        return list(self._lineas.values())

    @property
    def total(self) -> float:
        return sum(linea.subtotal for linea in self._lineas.values())

    @property
    def vacia(self) -> bool:
        return not self._lineas

    def linea(self, id_producto: str) -> Optional[LineaVenta]:
        return self._lineas.get(id_producto)

    def agregar(self, producto: Producto) -> bool:
        """Suma una unidad. Devuelve False si ya no hay existencias."""
        linea = self._lineas.get(producto.id)
        en_venta = linea.cantidad if linea else 0
        if en_venta >= producto.existencia:
            return False
        if linea:
            linea.cantidad += 1
        else:
            self._lineas[producto.id] = LineaVenta(producto)
        return True

    def cambiar_cantidad(self, id_producto: str, delta: int) -> bool:
        """Suma o resta piezas. La cantidad se queda entre 1 y la existencia."""
        linea = self._lineas.get(id_producto)
        if linea is None:
            return False
        nueva = linea.cantidad + delta
        if nueva < 1 or nueva > linea.producto.existencia:
            return False
        linea.cantidad = nueva
        return True

    def quitar(self, id_producto: str) -> None:
        self._lineas.pop(id_producto, None)

    def limpiar(self) -> None:
        self._lineas.clear()


class RepositorioVentas:
    """Guarda las ventas cobradas (tablas venta y detalle_venta)."""

    def __init__(self, bd: BaseDatos):
        self._bd = bd

    def registrar(self, venta: Venta, id_empleado: int, metodo_pago: str = "Efectivo") -> int:
        """Guarda la venta completa o nada. Los triggers de la base generan la salida de
        inventario de cada línea y descuentan las existencias. Devuelve el id de la venta.
        Lanza ValueError con un mensaje legible si algo falla."""
        with self._bd.transaccion() as con:
            id_venta = con.execute("INSERT INTO venta (id_empleado, metodo_pago) VALUES (?, ?)",
                                   (id_empleado, metodo_pago)).lastrowid
            for linea in venta.lineas:
                fila = con.execute("SELECT id_producto FROM producto "
                                   "WHERE codigo = ? AND estado = 'Activo'",
                                   (linea.producto.id,)).fetchone()
                if fila is None:
                    raise ValueError(f"{linea.producto.descripcion} ya no está disponible.")
                con.execute("INSERT INTO detalle_venta (id_venta, id_producto, cantidad,"
                            " precio_unitario) VALUES (?, ?, ?, ?)",
                            (id_venta, fila["id_producto"], linea.cantidad, linea.producto.precio))
        return id_venta
