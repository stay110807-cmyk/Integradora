"""Modelo: productos y su repositorio (por ahora en memoria).

Cuando tengas base de datos, solo se reemplaza el interior de
RepositorioProductos; las vistas y el controlador no cambian.
"""
import math
from dataclasses import dataclass
from typing import List, Optional

UMBRAL_STOCK_BAJO = 5  # con esta existencia o menos se considera "stock bajo"

DISPONIBLE = "disponible"
STOCK_BAJO = "bajo"
AGOTADO = "agotado"


@dataclass
class Producto:
    id: str
    descripcion: str
    categoria: str
    precio: float
    existencia: int

    @property
    def estado(self) -> str:
        if self.existencia <= 0:
            return AGOTADO
        if self.existencia <= UMBRAL_STOCK_BAJO:
            return STOCK_BAJO
        return DISPONIBLE

    @property
    def con_alerta(self) -> bool:
        return self.estado != DISPONIBLE


class RepositorioProductos:
    def __init__(self):
        self._items = {p.id: p for p in [
            Producto("001", "Camisa Deportiva M", "Ropa", 320.00, 24),
            Producto("002", "Pantalón Mezclilla", "Ropa", 550.00, 12),
            Producto("003", "Tenis Running", "Calzado", 1200.00, 6),
            Producto("004", "Llaveros Batman", "Accesorios", 600.00, 4),
            Producto("005", "Gorra Negra", "Accesorios", 250.00, 0),
        ]}

    # ---- Consultas ----
    def todos(self) -> List[Producto]:
        return list(self._items.values())

    def obtener(self, id_producto: str) -> Optional[Producto]:
        return self._items.get(id_producto.strip())

    def buscar(self, texto: str = "", categoria: Optional[str] = None) -> List[Producto]:
        """Filtra por texto (código, descripción o categoría) y, opcionalmente, categoría."""
        texto = texto.strip().lower()
        resultado = []
        for p in self._items.values():
            if categoria and p.categoria != categoria:
                continue
            if texto and not (texto in p.id.lower() or texto in p.descripcion.lower()
                              or texto in p.categoria.lower()):
                continue
            resultado.append(p)
        return resultado

    def categorias(self) -> List[str]:
        return sorted({p.categoria for p in self._items.values()})

    def con_alerta(self) -> int:
        """Cuántos productos están agotados o con stock bajo."""
        return sum(1 for p in self._items.values() if p.con_alerta)

    def siguiente_id(self) -> str:
        numeros = [int(i) for i in self._items if i.isdigit()]
        return f"{(max(numeros) + 1) if numeros else 1:03d}"

    # ---- Cambios ----
    def guardar(self, producto: Producto, nuevo: bool) -> None:
        """Alta (nuevo=True) o edición. Lanza ValueError con un mensaje legible."""
        self._validar(producto)
        existente = self._items.get(producto.id)
        if nuevo:
            if existente:
                raise ValueError(f"Ya existe un producto con el código {producto.id}.")
            self._items[producto.id] = producto
        else:
            if existente is None:
                raise ValueError("El producto ya no existe.")
            # Se actualiza el mismo objeto para que una venta en curso vea los cambios.
            existente.descripcion = producto.descripcion
            existente.categoria = producto.categoria
            existente.precio = producto.precio
            existente.existencia = producto.existencia

    def descontar(self, id_producto: str, cantidad: int) -> None:
        self._items[id_producto].existencia -= cantidad

    @staticmethod
    def _validar(p: Producto) -> None:
        if not p.id:
            raise ValueError("Escribe el código del producto.")
        if not p.descripcion:
            raise ValueError("Escribe la descripción del producto.")
        if not p.categoria:
            raise ValueError("Escribe la categoría del producto.")
        if not math.isfinite(p.precio) or p.precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")
        if p.existencia < 0:
            raise ValueError("La existencia no puede ser negativa.")
