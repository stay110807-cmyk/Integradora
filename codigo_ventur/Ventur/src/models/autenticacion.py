"""Modelo: cuentas y verificación de contraseñas (funciona sin internet).

Las contraseñas no se comparan en texto plano: se guardan como hash PBKDF2
con una sal propia por cuenta.

IMPORTANTE: la cuenta de la dueña de abajo es de DESARROLLO. Antes de usar el
sistema de verdad, cambia la contraseña (o mueve las cuentas a una base de datos).
"""
import hashlib
import hmac
import os
from typing import Dict, Optional, Tuple

from .usuario import Rol, Usuario

# --- Cuenta inicial de la dueña (cámbiala aquí) ---
USUARIO_DUENA = "admin"
CONTRASENA_DUENA = "admin123"
NOMBRE_DUENA = "Rosa"

_ITERACIONES = 100_000


def _derivar(contrasena: str, sal: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal, _ITERACIONES)


class RepositorioUsuarios:
    def __init__(self):
        self._cuentas: Dict[str, Tuple[Usuario, bytes, bytes]] = {}
        self._registrar(Usuario(USUARIO_DUENA, NOMBRE_DUENA, Rol.DUENA), CONTRASENA_DUENA)
        # Ejemplo para cuando exista el módulo Empleados:
        # self._registrar(Usuario("luis", "Luis", Rol.EMPLEADO, "Atención a clientes"), "luis123")

    def _registrar(self, usuario: Usuario, contrasena: str) -> None:
        sal = os.urandom(16)
        self._cuentas[usuario.usuario.lower()] = (usuario, sal, _derivar(contrasena, sal))

    def autenticar(self, nombre_usuario: str, contrasena: str) -> Optional[Usuario]:
        """Devuelve el Usuario si las credenciales son correctas; si no, None."""
        cuenta = self._cuentas.get(nombre_usuario.strip().lower())
        if cuenta is None:
            _derivar(contrasena, b"\0" * 16)  # tarda lo mismo exista o no el usuario
            return None
        usuario, sal, esperado = cuenta
        return usuario if hmac.compare_digest(_derivar(contrasena, sal), esperado) else None
