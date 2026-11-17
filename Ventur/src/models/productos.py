"""Modelo: productos y su repositorio (SQLite, tabla producto).

Las vistas y el controlador no saben que hay una base de datos: siguen
recibiendo objetos Producto.
"""
import math
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from .database import BaseDatos

UMBRAL_STOCK_BAJO = 5  # stock mínimo que se asigna a los productos nuevos

DISPONIBLE = "disponible"
STOCK_BAJO = "bajo"
AGOTADO = "agotado"

_SELECT = """
SELECT p.codigo, p.nombre, c.nombre AS categoria, p.precio, p.existencias, p.stock_minimo
  FROM producto p
  JOIN categoria c ON c.id_categoria = p.id_categoria
 WHERE p.estado = 'Activo'
"""


@dataclass
class Producto:
    id: str                 # código del producto (ej. "P-001")
    descripcion: str
    categoria: str
    precio: float
    existencia: int
    stock_minimo: int = UMBRAL_STOCK_BAJO

    @property
    def estado(self) -> str:
        if self.existencia <= 0:
            return AGOTADO
        if self.existencia <= self.stock_minimo:
            return STOCK_BAJO
        return DISPONIBLE

    @property
    def con_alerta(self) -> bool:
        return self.estado != DISPONIBLE


class RepositorioProductos:
    def __init__(self, bd: BaseDatos):
        self._bd = bd
        # Un solo objeto Producto por código: así una venta en curso ve los cambios
        # (precio, existencias) en cuanto se vuelven a leer de la base.
        self._conocidos: Dict[str, Producto] = {}

    def _hidratar(self, fila) -> Producto:
        datos = dict(descripcion=fila["nombre"], categoria=fila["categoria"],
                     precio=float(fila["precio"]), existencia=int(fila["existencias"]),
                     stock_minimo=int(fila["stock_minimo"]))
        producto = self._conocidos.get(fila["codigo"])
        if producto is None:
            producto = Producto(id=fila["codigo"], **datos)
            self._conocidos[producto.id] = producto
        else:
            for campo, valor in datos.items():
                setattr(producto, campo, valor)
        return producto

    # ---- Consultas ----
    def todos(self) -> List[Producto]:
        return [self._hidratar(f) for f in self._bd.consultar(_SELECT + " ORDER BY p.codigo")]

    def obtener(self, id_producto: str) -> Optional[Producto]:
        fila = self._bd.uno(_SELECT + " AND p.codigo = ?", (id_producto.strip(),))
        return self._hidratar(fila) if fila else None

    def buscar(self, texto: str = "", categoria: Optional[str] = None) -> List[Producto]:
        """Filtra por texto (código, descripción o categoría) y, opcionalmente, categoría."""
        texto = texto.strip().lower()
        resultado = []
        for p in self.todos():
            if categoria and p.categoria != categoria:
                continue
            if texto and not (texto in p.id.lower() or texto in p.descripcion.lower()
                              or texto in p.categoria.lower()):
                continue
            resultado.append(p)
        return resultado

    def categorias(self) -> List[str]:
        return sorted({p.categoria for p in self.todos()})

    def con_alerta(self) -> int:
        """Cuántos productos están agotados o con stock bajo (misma regla que v_alertas_stock)."""
        fila = self._bd.uno("SELECT COUNT(*) AS n FROM producto "
                            "WHERE estado = 'Activo' AND existencias <= stock_minimo")
        return fila["n"]

    def siguiente_id(self) -> str:
        """Siguiente código libre con el formato P-001, P-002..."""
        numeros = []
        for fila in self._bd.consultar("SELECT codigo FROM producto"):
            m = re.fullmatch(r"P-(\d+)", fila["codigo"])
            if m:
                numeros.append(int(m.group(1)))
        return f"P-{(max(numeros) + 1) if numeros else 1:03d}"

    # ---- Cambios ----
    def guardar(self, producto: Producto, nuevo: bool, id_empleado: int) -> None:
        """Alta (nuevo=True) o edición. Lanza ValueError con un mensaje legible.

        Las existencias nunca se editan "a mano": la diferencia se registra como
        movimiento (Entrada/Salida) a nombre de id_empleado y el trigger de la base
        recalcula el inventario, así el historial siempre cuadra.
        """
        self._validar(producto)
        with self._bd.transaccion() as con:
            id_categoria = self._id_categoria(con, producto.categoria)
            fila = con.execute("SELECT id_producto, existencias FROM producto WHERE codigo = ?",
                               (producto.id,)).fetchone()
            if nuevo:
                if fila:
                    raise ValueError(f"Ya existe un producto con el código {producto.id}.")
                cursor = con.execute(
                    "INSERT INTO producto (codigo, nombre, id_categoria, id_marca, precio,"
                    " existencias, stock_minimo) VALUES (?, ?, ?, NULL, ?, 0, ?)",
                    (producto.id, producto.descripcion, id_categoria, producto.precio,
                     producto.stock_minimo))
                self._registrar_diferencia(con, cursor.lastrowid, 0, producto.existencia,
                                           id_empleado)
            else:
                activo = fila and con.execute(
                    "SELECT 1 FROM producto WHERE id_producto = ? AND estado = 'Activo'",
                    (fila["id_producto"],)).fetchone()
                if not activo:
                    raise ValueError("El producto ya no existe.")
                con.execute("UPDATE producto SET nombre = ?, id_categoria = ?, precio = ? "
                            "WHERE id_producto = ?",
                            (producto.descripcion, id_categoria, producto.precio,
                             fila["id_producto"]))
                self._registrar_diferencia(con, fila["id_producto"], fila["existencias"],
                                           producto.existencia, id_empleado)

    @staticmethod
    def _id_categoria(con, nombre: str) -> int:
        fila = con.execute("SELECT id_categoria FROM categoria WHERE nombre = ? COLLATE NOCASE",
                           (nombre,)).fetchone()
        if fila:
            return fila["id_categoria"]
        return con.execute("INSERT INTO categoria (nombre) VALUES (?)", (nombre,)).lastrowid

    @staticmethod
    def _registrar_diferencia(con, id_producto, antes, despues, id_empleado) -> None:
        diferencia = despues - antes
        if diferencia == 0:
            return
        con.execute("INSERT INTO movimiento (id_producto, id_empleado, tipo, cantidad, origen)"
                    " VALUES (?, ?, ?, ?, 'Manual')",
                    (id_producto, id_empleado, "Entrada" if diferencia > 0 else "Salida",
                     abs(diferencia)))

    @staticmethod
    def _validar(p: Producto) -> None:
        if len(p.id) < 2:
            raise ValueError("Escribe el código del producto (mínimo 2 caracteres).")
        if len(p.descripcion) < 2:
            raise ValueError("Escribe la descripción del producto.")
        if len(p.categoria) < 3:
            raise ValueError("Escribe la categoría del producto (mínimo 3 letras).")
        if not math.isfinite(p.precio) or p.precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")
        if p.existencia < 0:
            raise ValueError("La existencia no puede ser negativa.")
