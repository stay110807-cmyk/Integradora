"""Conexión a la base de datos SQLite de Ventur (archivo ventur.db).

- En Android el archivo vive en la carpeta de datos privada de la app
  (Flet la expone en la variable FLET_APP_STORAGE_DATA) y sobrevive a las
  actualizaciones. En la computadora se usa ~/.ventur/ si esa variable no existe.
- La primera vez que se abre, crea el archivo con los scripts de models/sql/
  (estructura, datos de prueba y protecciones). Se arma en un archivo temporal y
  se renombra al final, así nunca queda una base a medias.
- SQLite exige activar las llaves foráneas en CADA conexión: aquí se hace siempre.
"""
import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, List, Optional

NOMBRE_BD = "ventur.db"
_CARPETA_SQL = Path(__file__).parent / "sql"
_SCRIPTS = ("01_ddl.sql", "02_dml.sql", "04_seguridad.sql")  # este orden importa


def ruta_base_datos() -> Path:
    """Dónde vive ventur.db. VENTUR_DB permite apuntar a otro archivo (pruebas)."""
    explicita = os.getenv("VENTUR_DB")
    if explicita:
        ruta = Path(explicita)
    else:
        carpeta = os.getenv("FLET_APP_STORAGE_DATA")
        base = Path(carpeta) if carpeta else Path.home() / ".ventur"
        ruta = base / NOMBRE_BD
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


def mensaje_de_error(error: sqlite3.Error) -> str:
    """Texto legible. Los RAISE de los triggers ya vienen en español; el resto se resume."""
    texto = str(error)
    if "existencias" in texto:
        return "No hay existencias suficientes para completar la operación."
    if "constraint failed" in texto or "UNIQUE" in texto or "FOREIGN KEY" in texto:
        return "Los datos no cumplen las reglas de la base de datos."
    if "locked" in texto:
        return "La base de datos está ocupada. Inténtalo de nuevo."
    return texto


class BaseDatos:
    def __init__(self, ruta: Optional[os.PathLike] = None):
        self.ruta = Path(ruta) if ruta else ruta_base_datos()
        self.ruta.parent.mkdir(parents=True, exist_ok=True)   # <- nueva
        self._candado = threading.RLock()
        if not self.ruta.exists():
            self._crear()
        self._con = self._abrir(self.ruta)

    # ---- Apertura y creación ----
    @staticmethod
    def _abrir(ruta: Path) -> sqlite3.Connection:
        con = sqlite3.connect(str(ruta), check_same_thread=False)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def _crear(self) -> None:
        temporal = self.ruta.with_name(self.ruta.name + ".tmp")
        temporal.unlink(missing_ok=True)
        con = sqlite3.connect(str(temporal))
        try:
            for nombre in _SCRIPTS:
                con.executescript((_CARPETA_SQL / nombre).read_text(encoding="utf-8"))
            con.commit()
        except BaseException:
            con.close()
            temporal.unlink(missing_ok=True)
            raise
        con.close()
        os.replace(temporal, self.ruta)

    # ---- Consultas ----
    def consultar(self, sql: str, parametros: Iterable = ()) -> List[sqlite3.Row]:
        with self._candado:
            return self._con.execute(sql, tuple(parametros)).fetchall()

    def uno(self, sql: str, parametros: Iterable = ()) -> Optional[sqlite3.Row]:
        with self._candado:
            return self._con.execute(sql, tuple(parametros)).fetchone()

    @contextmanager
    def transaccion(self):
        """Agrupa escrituras: si algo falla no se guarda nada. Los errores de SQLite
        (triggers, CHECK, llaves) salen como ValueError con un mensaje legible."""
        with self._candado:
            try:
                yield self._con
                self._con.commit()
            except sqlite3.Error as error:
                self._con.rollback()
                raise ValueError(mensaje_de_error(error)) from error
            except BaseException:
                self._con.rollback()
                raise

    def cerrar(self) -> None:
        with self._candado:
            self._con.close()
