"""Modelo: módulos del panel de control y qué rol puede verlos.

El orden de la lista es el orden en pantalla (izquierda a derecha, arriba abajo).
"""
from dataclasses import dataclass
from typing import List

from .usuario import Rol


@dataclass(frozen=True)
class Modulo:
    id: str                 # también es el nombre del PNG en assets/iconos/
    titulo: str
    descripcion: str
    solo_duena: bool = False


class RepositorioModulos:
    _MODULOS = [
        Modulo("productos", "Productos", "Catálogo, precios y existencias."),
        Modulo("caja", "Caja", "Punto de venta y cobro."),
        Modulo("movimientos", "Movimientos", "Registro de entradas y salidas de inventario."),
        Modulo("alertas", "Alertas de stock", "Productos agotados o con stock bajo.", True),
        Modulo("empleados", "Empleados", "Altas, bajas y funciones del personal.", True),
        Modulo("historial", "Historial", "Consulta de ventas y movimientos anteriores.", True),
        Modulo("respaldo", "Respaldo y restauración", "Copias de seguridad de tu información.", True),
        Modulo("reporte", "Reporte de existencias", "Existencias actuales de todos los productos.", True),
    ]

    def para_rol(self, rol: Rol) -> List[Modulo]:
        """La dueña ve todo; el empleado solo lo que no es exclusivo de la dueña."""
        return [m for m in self._MODULOS if rol is Rol.DUENA or not m.solo_duena]
