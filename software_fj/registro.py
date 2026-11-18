"""Auditoría de eventos y errores sin mantener bloqueos de archivo en Windows.

Cada evento abre, escribe y cierra su archivo. Esto evita que una prueba
que use ``TemporaryDirectory`` conserve ``eventos.log`` abierto y falle al
borrar el directorio en Windows (WinError 32). Se conserva la rotación.
"""

import logging
import os
import sys
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path


class ManejadorRotativoSinBloqueo(RotatingFileHandler):
    """RotatingFileHandler que no conserva un descriptor entre eventos.

    Esta variante evita los bloqueos de archivos temporales en Windows y
    reduce problemas con directorios sincronizados (p. ej., OneDrive).
    El candado de ``logging.Handler.handle`` serializa cada emisión dentro
    del proceso; este ejercicio no escribe desde varios procesos a la vez.
    """

    def __init__(self, ruta: str | Path, max_bytes: int = 500_000) -> None:
        # delay=True impide abrir y mantener un stream permanente.
        super().__init__(ruta, maxBytes=max_bytes, backupCount=2,
                         encoding="utf-8", delay=True)

    def emit(self, record: logging.LogRecord) -> None:
        """Escribe y cierra el archivo en cada evento, incluso si hay error."""
        try:
            mensaje = self.format(record) + self.terminator
            if self.maxBytes > 0:
                tamano_nuevo = len(mensaje.encode("utf-8"))
                tamano_actual = (os.path.getsize(self.baseFilename)
                                 if os.path.isfile(self.baseFilename) else 0)
                if tamano_actual + tamano_nuevo >= self.maxBytes and tamano_actual:
                    self.doRollover()
            # El bloque with asegura el cierre antes de regresar.
            with open(self.baseFilename, "a", encoding="utf-8") as archivo:
                archivo.write(mensaje)
        except Exception:
            # La aplicación seguirá activa y logging reportará el fallo.
            self.handleError(record)


def ruta_registro_por_defecto() -> Path:
    """Guarda el log fuera de carpetas sincronizadas en Windows.

    En Windows utiliza el directorio temporal local del usuario (el mismo
    que ``%TEMP%``). En otros sistemas conserva la ruta del proyecto.
    Se puede personalizar con la opción CLI ``--log``.
    """
    if sys.platform == "win32":
        return Path(tempfile.gettempdir()) / "softwarefj_eventos.log"
    return Path("logs/eventos.log")


def configurar_registro(ruta: str | Path | None = None) -> logging.Logger:
    """Configura y verifica el registro rotativo, sin archivos retenidos."""
    destino = Path(ruta) if ruta is not None else ruta_registro_por_defecto()
    destino.parent.mkdir(parents=True, exist_ok=True)

    # Verifica el permiso de escritura al inicio: si no existe, fallo claro.
    # Se cierra de inmediato para no interferir con Windows ni OneDrive.
    with destino.open("a", encoding="utf-8"):
        pass

    logger = logging.getLogger("software_fj")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for manejador in list(logger.handlers):
        logger.removeHandler(manejador)
        manejador.close()

    manejador = ManejadorRotativoSinBloqueo(destino)
    manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(manejador)
    logger.info("Sistema de eventos inicializado")
    return logger
