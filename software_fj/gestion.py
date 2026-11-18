"""Coordinación de clientes, servicios y reservas almacenados en listas."""

from datetime import datetime
import logging

from .errores import (
    DatoInvalidoError, EntidadNoEncontradaError, RegistroDuplicadoError,
    ReservaInvalidaError, ServicioNoDisponibleError,
)
from .modelos import Cliente, Servicio, Equipo, Reserva, texto_obligatorio

LOG = logging.getLogger("software_fj")


class SistemaGestion:
    """Orquesta las operaciones sin emplear bases de datos."""

    def __init__(self) -> None:
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []

    @property
    def clientes(self) -> tuple[Cliente, ...]:
        return tuple(self._clientes)

    @property
    def servicios(self) -> tuple[Servicio, ...]:
        return tuple(self._servicios)

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        return tuple(self._reservas)

    def registrar_cliente(self, identificador: str, nombre: str, correo: str, telefono: str) -> Cliente:
        # Comprobar duplicados antes de modificar la lista evita estados parciales.
        cliente = Cliente(identificador, nombre, correo, telefono)
        if any(c.identificador == cliente.identificador for c in self._clientes):
            raise RegistroDuplicadoError("Ya existe un cliente con ese identificador.")
        self._clientes.append(cliente)
        LOG.info("Cliente registrado: %s", cliente.identificador)
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Debe proporcionarse un Servicio válido.")
        if any(s.identificador == servicio.identificador for s in self._servicios):
            raise RegistroDuplicadoError("Ya existe un servicio con ese identificador.")
        self._servicios.append(servicio)
        LOG.info("Servicio registrado: %s (%s)", servicio.identificador, type(servicio).__name__)
        return servicio

    def buscar_cliente(self, identificador: str) -> Cliente:
        buscado = texto_obligatorio(identificador, "identificador cliente", 40)
        for cliente in self._clientes:
            if cliente.identificador == buscado:
                return cliente
        raise EntidadNoEncontradaError(f"No existe el cliente {buscado}.")

    def buscar_servicio(self, identificador: str) -> Servicio:
        buscado = texto_obligatorio(identificador, "identificador servicio", 40)
        for servicio in self._servicios:
            if servicio.identificador == buscado:
                return servicio
        raise EntidadNoEncontradaError(f"No existe el servicio {buscado}.")

    def buscar_reserva(self, identificador: str) -> Reserva:
        buscado = texto_obligatorio(identificador, "identificador reserva", 40)
        for reserva in self._reservas:
            if reserva.identificador == buscado:
                return reserva
        raise EntidadNoEncontradaError(f"No existe la reserva {buscado}.")

    def _validar_disponibilidad(self, servicio: Servicio, inicio: datetime,
                                fin: datetime) -> None:
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio {servicio.identificador} está fuera de servicio.")
        # Intervalos semiabiertos: [inicio, fin). Reservas consecutivas sí son posibles.
        simultaneas = [r for r in self._reservas if r.estado == "CONFIRMADA"
                       and r.servicio.identificador == servicio.identificador
                       and inicio < r.fin and r.inicio < fin]
        limite = servicio.unidades if isinstance(servicio, Equipo) else 1
        # Barrido temporal: contar sólo solapamientos SIMULTÁNEOS, no la cantidad
        # total de reservas que tocan el intervalo solicitado.
        eventos = []
        for reserva in simultaneas:
            eventos.append((max(inicio, reserva.inicio), 1))
            eventos.append((min(fin, reserva.fin), -1))
        activas = 0
        for _, variacion in sorted(eventos, key=lambda item: (item[0], item[1])):
            activas += variacion
            if activas >= limite:
                raise ServicioNoDisponibleError("No hay capacidad para el horario solicitado.")

    def crear_reserva(self, identificador: str, cliente_id: str, servicio_id: str,
                      inicio: str | datetime, duracion: object,
                      impuesto: object = 0, descuento: object = 0) -> Reserva:
        """Valida, calcula, confirma y agrega una reserva de forma atómica."""
        numero = texto_obligatorio(identificador, "identificador reserva", 40)
        if any(r.identificador == numero for r in self._reservas):
            raise RegistroDuplicadoError(f"Ya existe la reserva {numero}.")
        cliente = self.buscar_cliente(cliente_id)
        servicio = self.buscar_servicio(servicio_id)
        if isinstance(inicio, str):
            try:
                fecha = datetime.strptime(inicio, "%Y-%m-%d %H:%M")
            except ValueError as error:
                raise ReservaInvalidaError("Fecha inválida; use AAAA-MM-DD HH:MM.") from error
        elif isinstance(inicio, datetime):
            fecha = inicio
        else:
            raise ReservaInvalidaError("La fecha debe ser texto o datetime.")
        if fecha.tzinfo is not None:
            raise ReservaInvalidaError("Se requieren fechas locales sin zona horaria.")
        # El ejercicio es una simulación: se admiten fechas históricas para las pruebas.
        costo = servicio.calcular_costo(duracion, impuesto, descuento)
        reserva = Reserva(numero, cliente, servicio, fecha, duracion, costo)
        self._validar_disponibilidad(servicio, fecha, reserva.fin)
        reserva.confirmar()
        self._reservas.append(reserva)
        LOG.info("Reserva confirmada: %s | cliente=%s | servicio=%s | costo=%s",
                 numero, cliente.identificador, servicio.identificador, costo)
        return reserva

    def cancelar_reserva(self, identificador: str) -> Reserva:
        reserva = self.buscar_reserva(identificador)
        reserva.cancelar()
        LOG.info("Reserva cancelada: %s", reserva.identificador)
        return reserva
