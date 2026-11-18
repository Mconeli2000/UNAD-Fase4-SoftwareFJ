"""Pruebas automáticas con unittest (biblioteca estándar de Python)."""

from datetime import datetime
from decimal import Decimal
import logging
from pathlib import Path
import tempfile
import unittest

from software_fj.demo import ejecutar_simulaciones
from software_fj.errores import (
    CalculoInconsistenteError, DatoInvalidoError, EntidadNoEncontradaError,
    OperacionNoPermitidaError, ParametroFaltanteError, RegistroDuplicadoError,
    ReservaInvalidaError, ServicioNoDisponibleError,
)
from software_fj.gestion import SistemaGestion
from software_fj.modelos import Sala, Equipo, Asesoria, Cliente, numero_entero
from software_fj.registro import configurar_registro


class TestSistemaGestion(unittest.TestCase):
    """Cada prueba comienza con un catálogo independiente en memoria."""

    def setUp(self) -> None:
        self.sistema = SistemaGestion()
        self.sistema.registrar_cliente("C1", "Ana", "ANA@example.com", "3001234567")
        self.sistema.registrar_cliente("C2", "Luis", "luis@example.com", "+573111234567")
        self.sistema.registrar_servicio(Sala("S1", "Sala", 100000, 10))
        self.sistema.registrar_servicio(Equipo("E1", "Equipo", 40000, 2))
        self.sistema.registrar_servicio(Asesoria("A1", "Asesoría", 50000, "Programación", 10000))

    def test_registro_cliente_exitoso(self):
        cliente = self.sistema.registrar_cliente("C3", "Marta", "marta@example.com", "3004567890")
        self.assertEqual(cliente.nombre, "Marta")

    def test_correo_normalizado(self):
        self.assertEqual(self.sistema.buscar_cliente("C1").correo, "ana@example.com")

    def test_correo_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            Cliente("X", "X", "sin_arroba", "3001234567")

    def test_telefono_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            Cliente("X", "X", "x@example.com", "11")

    def test_nombre_faltante(self):
        with self.assertRaises(ParametroFaltanteError):
            Cliente("X", "", "x@example.com", "3001234567")

    def test_id_cliente_duplicado(self):
        with self.assertRaises(RegistroDuplicadoError):
            self.sistema.registrar_cliente("C1", "Otra", "otra@example.com", "3009876543")

    def test_no_expone_telefono_en_repr(self):
        self.assertNotIn("3001234567", repr(self.sistema.buscar_cliente("C1")))

    def test_registro_servicio_duplicado(self):
        with self.assertRaises(RegistroDuplicadoError):
            self.sistema.registrar_servicio(Sala("S1", "Otra", 50000, 5))

    def test_tarifa_negativa(self):
        with self.assertRaises(DatoInvalidoError):
            Sala("X", "Sala", -1, 10)

    def test_tarifa_no_numerica_encadenada(self):
        with self.assertRaises(DatoInvalidoError) as contexto:
            Sala("X", "Sala", "abc", 10)
        self.assertIsNotNone(contexto.exception.__cause__)

    def test_tarifa_infinita(self):
        with self.assertRaises(DatoInvalidoError):
            Sala("X", "Sala", "Infinity", 10)

    def test_capacidad_cero(self):
        with self.assertRaises(DatoInvalidoError):
            Sala("X", "Sala", 20000, 0)

    def test_unidades_cero(self):
        with self.assertRaises(DatoInvalidoError):
            Equipo("X", "Equipo", 20000, 0)

    def test_costo_sala(self):
        self.assertEqual(self.sistema.buscar_servicio("S1").calcular_costo(2), Decimal("200000.00"))

    def test_costo_sala_impuesto_descuento(self):
        self.assertEqual(self.sistema.buscar_servicio("S1").calcular_costo(2, ".19", ".10"), Decimal("214200.00"))

    def test_polimorfismo_asesoria(self):
        self.assertEqual(self.sistema.buscar_servicio("A1").calcular_costo(2), Decimal("110000.00"))

    def test_porcentaje_mayor_uno(self):
        with self.assertRaises(CalculoInconsistenteError):
            self.sistema.buscar_servicio("S1").calcular_costo(1, "1.5", 0)

    def test_duracion_negativa(self):
        with self.assertRaises(DatoInvalidoError):
            self.sistema.buscar_servicio("S1").calcular_costo(-1)

    def test_duracion_fraccionaria(self):
        with self.assertRaises(DatoInvalidoError):
            numero_entero(Decimal("1.5"), "duración")

    def test_exceso_horas_sala(self):
        with self.assertRaises(ReservaInvalidaError):
            self.sistema.buscar_servicio("S1").calcular_costo(13)

    def test_exceso_horas_equipo(self):
        with self.assertRaises(ReservaInvalidaError):
            self.sistema.buscar_servicio("E1").calcular_costo(73)

    def test_exceso_horas_asesoria(self):
        with self.assertRaises(ReservaInvalidaError):
            self.sistema.buscar_servicio("A1").calcular_costo(9)

    def test_servicio_no_disponible(self):
        servicio = self.sistema.buscar_servicio("S1")
        servicio.cambiar_disponibilidad(False)
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 09:00", 1)

    def test_cliente_inexistente(self):
        with self.assertRaises(EntidadNoEncontradaError):
            self.sistema.crear_reserva("R1", "C99", "S1", "2026-11-20 09:00", 1)

    def test_servicio_inexistente(self):
        with self.assertRaises(EntidadNoEncontradaError):
            self.sistema.crear_reserva("R1", "C1", "S99", "2026-11-20 09:00", 1)

    def test_reserva_correcta(self):
        reserva = self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 09:00", 2)
        self.assertEqual(reserva.estado, "CONFIRMADA")
        self.assertEqual(reserva.costo, Decimal("200000.00"))

    def test_conflicto_sala(self):
        self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 09:00", 2)
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva("R2", "C2", "S1", "2026-11-20 10:00", 1)
        self.assertEqual(len(self.sistema.reservas), 1)

    def test_reservas_consecutivas(self):
        self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 09:00", 2)
        segunda = self.sistema.crear_reserva("R2", "C2", "S1", "2026-11-20 11:00", 1)
        self.assertEqual(segunda.estado, "CONFIRMADA")

    def test_inventario_dos_unidades(self):
        for n in (1, 2):
            self.sistema.crear_reserva(f"R{n}", "C1", "E1", "2026-11-20 10:00", 2)
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva("R3", "C2", "E1", "2026-11-20 10:00", 2)

    def test_equipo_solapamientos_no_simultaneos(self):
        """Dos alquileres separados no deben bloquear una franja amplia con dos equipos."""
        self.sistema.crear_reserva("R1", "C1", "E1", "2026-11-20 09:00", 1)
        self.sistema.crear_reserva("R2", "C2", "E1", "2026-11-20 11:00", 1)
        nueva = self.sistema.crear_reserva("R3", "C2", "E1", "2026-11-20 09:00", 3)
        self.assertEqual(nueva.estado, "CONFIRMADA")

    def test_cancelacion_libera_cupo(self):
        self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 10:00", 2)
        self.sistema.cancelar_reserva("R1")
        nueva = self.sistema.crear_reserva("R2", "C2", "S1", "2026-11-20 10:00", 2)
        self.assertEqual(nueva.estado, "CONFIRMADA")

    def test_doble_cancelacion_invalida(self):
        self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 10:00", 2)
        self.sistema.cancelar_reserva("R1")
        with self.assertRaises(OperacionNoPermitidaError):
            self.sistema.cancelar_reserva("R1")

    def test_doble_confirmacion_invalida(self):
        reserva = self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 10:00", 1)
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.confirmar()

    def test_reserva_repetida(self):
        self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 10:00", 1)
        with self.assertRaises(RegistroDuplicadoError):
            self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-21 10:00", 1)

    def test_fecha_invalida_con_causa(self):
        with self.assertRaises(ReservaInvalidaError) as contexto:
            self.sistema.crear_reserva("R1", "C1", "S1", "20/11/2026", 1)
        self.assertIsNotNone(contexto.exception.__cause__)

    def test_fecha_zona_horaria_no_permitida(self):
        from datetime import timezone
        with self.assertRaises(ReservaInvalidaError):
            self.sistema.crear_reserva("R1", "C1", "S1", datetime.now(timezone.utc), 1)

    def test_no_crea_reserva_si_falla_costeo(self):
        with self.assertRaises(CalculoInconsistenteError):
            self.sistema.crear_reserva("R1", "C1", "S1", "2026-11-20 10:00", 2, 0, 2)
        self.assertEqual(len(self.sistema.reservas), 0)

    def test_listas_solo_lectura(self):
        self.assertIsInstance(self.sistema.clientes, tuple)
        with self.assertRaises(AttributeError):
            self.sistema.clientes.append("otro")


class TestSimulacionesYLog(unittest.TestCase):
    def test_veinte_simulaciones_completadas(self):
        logger = logging.getLogger("software_fj")
        try:
            with tempfile.TemporaryDirectory() as carpeta:
                ruta = Path(carpeta) / "eventos.log"
                configurar_registro(ruta)
                casos, sistema = ejecutar_simulaciones()
                self.assertEqual(len(casos), 20)
                self.assertTrue(all(c["resultado"] == "APROBADA" for c in casos))
                self.assertTrue(any(r.estado == "CANCELADA" for r in sistema.reservas))
                for h in logger.handlers:
                    h.flush()
                log = ruta.read_text(encoding="utf-8")
                self.assertIn("ERROR", log)
                self.assertIn("INFO", log)
                self.assertIn("Simulación 20", log)
                self.assertNotIn("ana@example.com", log)
                # Ningún descriptor debe bloquear Windows al eliminar la carpeta.
                self.assertTrue(all(getattr(h, "stream", None) is None
                                    for h in logger.handlers))
        finally:
            # Evita que las pruebas siguientes escriban en una ruta ya borrada.
            for h in list(logger.handlers):
                logger.removeHandler(h)
                h.close()


if __name__ == "__main__":
    unittest.main()
