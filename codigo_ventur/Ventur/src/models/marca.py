"""Modelo: datos de la marca (nombre y eslogan)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Marca:
    nombre: str
    eslogan: str


VENTUR = Marca(
    nombre="Ventur",
    eslogan="Control, ventas y automatización en la nube",
)
