"""Modelo: inicio de sesión contra la tabla empleado (funciona sin internet).

Las contraseñas se guardan como hash bcrypt (nunca en texto plano) y la base
rechaza cualquier otro formato (ver 04_seguridad.sql).
Cuentas de prueba (02_dml.sql): rosa / Abc123 (dueña); los demás: Demo-<usuario>.
"""
from typing import Optional

import bcrypt

from .database import BaseDatos
from .usuario import Rol, Usuario

_SQL_LOGIN = """
SELECT e.id_empleado, e.nombre, e.usuario, e.hash_contrasena, r.nombre AS rol,
       (SELECT f.nombre
          FROM asignacion_funcion a
          JOIN funcion_laboral f ON f.id_funcion = a.id_funcion
         WHERE a.id_empleado = e.id_empleado
         ORDER BY a.fecha_cambio DESC LIMIT 1) AS funcion
  FROM empleado e
  JOIN rol r ON r.id_rol = e.id_rol
 WHERE e.usuario = ? COLLATE NOCASE
   AND e.estado = 'Activo'
"""

_hash_falso: Optional[bytes] = None


def _verificar(contrasena: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))
    except ValueError:      # contraseña de más de 72 bytes o hash dañado
        return False


def _gastar_tiempo(contrasena: str) -> None:
    """Para que tarde lo mismo exista o no el usuario."""
    global _hash_falso
    if _hash_falso is None:
        _hash_falso = bcrypt.hashpw(b"no-existe", bcrypt.gensalt(12))
    _verificar(contrasena, _hash_falso.decode("ascii"))


class RepositorioUsuarios:
    def __init__(self, bd: BaseDatos):
        self._bd = bd

    def autenticar(self, nombre_usuario: str, contrasena: str) -> Optional[Usuario]:
        """Devuelve el Usuario si las credenciales son correctas; si no, None."""
        fila = self._bd.uno(_SQL_LOGIN, (nombre_usuario.strip(),))
        if fila is None:
            _gastar_tiempo(contrasena)
            return None
        if not _verificar(contrasena, fila["hash_contrasena"]):
            return None
        return Usuario(usuario=fila["usuario"], nombre=fila["nombre"], rol=Rol(fila["rol"]),
                       funcion=fila["funcion"] or "", id_empleado=fila["id_empleado"])
