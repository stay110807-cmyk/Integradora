"""Modelo: usuario de la sesión y su rol."""
from dataclasses import dataclass
from enum import Enum


class Rol(Enum):
    DUENA = "Dueña"
    EMPLEADO = "Empleado"


@dataclass(frozen=True)
class Usuario:
    usuario: str          # nombre con el que inicia sesión (ej. "admin")
    nombre: str           # nombre para mostrar (ej. "Rosa")
    rol: Rol
    funcion: str = ""     # solo para empleados (ej. "Atención a clientes")

    @property
    def es_duena(self) -> bool:
        return self.rol is Rol.DUENA

    @property
    def descripcion(self) -> str:
        """Línea que aparece bajo el saludo del panel."""
        if self.es_duena:
            return "Propietaria · acceso completo"
        return f"Tu función: {self.funcion or 'sin función asignada'}"
