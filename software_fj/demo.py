"""Simulaciones reproducibles: al menos diez operaciones completas.

Cada caso valida su resultado esperado (éxito o error controlado) y
registra INFO/ERROR con un identificador de simulación. No persiste datos.
"""

from datetime import datetime
import logging
from .gestion import SistemaGestion
from .modelos import Sala, Equipo, Asesoria
from .errores import GestionError

LOG = logging.getLogger("software_fj")


def ejecutar_simulaciones() -> tuple[list[dict[str, str]], SistemaGestion]:
    """Realiza 20 pruebas de escenario; sigue incluso ante fallos esperados."""
    sistema = SistemaGestion()
    resultados: list[dict[str, str]] = []

    def probar(numero: int, nombre: str, operacion, error_esperado: bool = False) -> None:
        """try/except/else/finally: controla cada escenario de principio a fin."""
        estado = "NO EJECUTADO"
        observacion = ""
        try:
            valor = operacion()
        except GestionError as error:
            observacion = f"{type(error).__name__}: {error}"
            LOG.error("Simulación %02d [%s] error controlado: %s", numero, nombre, observacion)
            estado = "APROBADA" if error_esperado else "FALLIDA"
        except Exception:
            # Errores inesperados no rompen la batería: quedan registrados con traza.
            LOG.exception("Simulación %02d [%s]: error inesperado", numero, nombre)
            estado = "FALLIDA"
            observacion = "Se produjo un error inesperado (consultar log)."
        else:
            estado = "FALLIDA" if error_esperado else "APROBADA"
            observacion = ("Operación completada" if valor is None else
                           valor.describir() if hasattr(valor, "describir") else str(valor))
            LOG.info("Simulación %02d [%s] completada: %s", numero, nombre, estado)
        finally:
            resultados.append({"numero": str(numero).zfill(2), "caso": nombre,
                               "resultado": estado, "observacion": observacion})
            LOG.info("Simulación %02d finalizada: %s", numero, estado)

    probar(1, "Cliente válido", lambda: sistema.registrar_cliente(
        "C01", "Ana Pérez", "ana@example.com", "3001234567"))
    probar(2, "Correo inválido", lambda: sistema.registrar_cliente(
        "C02", "Luis Soto", "correo_malo", "3001234568"), True)
    probar(3, "Cliente repetido", lambda: sistema.registrar_cliente(
        "C01", "Ana Duplicada", "otra@example.com", "3001234569"), True)
    probar(4, "Teléfono inválido", lambda: sistema.registrar_cliente(
        "C03", "Laura Ruiz", "laura@example.com", "12"), True)
    probar(5, "Segundo cliente válido", lambda: sistema.registrar_cliente(
        "C04", "Juan Ortiz", "juan@example.com", "+573114445555"))
    probar(6, "Sala válida", lambda: sistema.registrar_servicio(
        Sala("S01", "Sala creativa", 80000, 12)))
    probar(7, "Equipo válido", lambda: sistema.registrar_servicio(
        Equipo("E01", "Proyector 4K", 40000, 2)))
    probar(8, "Asesoría válida", lambda: sistema.registrar_servicio(
        Asesoria("A01", "Consultoría en TI", 120000, "Infraestructura", 25000)))
    probar(9, "Servicio con tarifa negativa", lambda: sistema.registrar_servicio(
        Sala("S02", "Tarifa errónea", -100, 2)), True)
    probar(10, "Servicio sin capacidad", lambda: sistema.registrar_servicio(
        Equipo("E02", "Inventario vacío", 45000, 0)), True)
    probar(11, "Reserva de sala exitosa", lambda: sistema.crear_reserva(
        "R01", "C01", "S01", "2026-11-20 09:00", 2))
    probar(12, "Sala ocupada", lambda: sistema.crear_reserva(
        "R02", "C04", "S01", "2026-11-20 10:00", 1), True)
    probar(13, "Reserva de equipo exitosa", lambda: sistema.crear_reserva(
        "R03", "C01", "E01", "2026-11-20 10:00", 3, "0.19", "0.10"))
    probar(14, "Segundo equipo simultáneo", lambda: sistema.crear_reserva(
        "R04", "C04", "E01", "2026-11-20 11:00", 2))
    probar(15, "Inventario de equipo agotado", lambda: sistema.crear_reserva(
        "R05", "C04", "E01", "2026-11-20 11:30", 1), True)
    probar(16, "Duración incorrecta", lambda: sistema.crear_reserva(
        "R06", "C01", "A01", "2026-11-20 09:00", -2), True)
    probar(17, "Asesoría exitosa", lambda: sistema.crear_reserva(
        "R07", "C04", "A01", "2026-11-20 14:00", 2))
    probar(18, "Fecha inválida", lambda: sistema.crear_reserva(
        "R08", "C01", "S01", "2026/11/20 18:00", 1), True)
    probar(19, "Cancelación exitosa", lambda: sistema.cancelar_reserva("R01"))
    probar(20, "Reutilizar sala liberada", lambda: sistema.crear_reserva(
        "R09", "C04", "S01", "2026-11-20 10:00", 1))
    return resultados, sistema


def resumen(resultados: list[dict[str, str]]) -> str:
    aprobadas = sum(c["resultado"] == "APROBADA" for c in resultados)
    return f"Simulaciones superadas: {aprobadas}/{len(resultados)}"
