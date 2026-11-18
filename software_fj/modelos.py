"""Modelos orientados a objetos: abstracción, herencia y polimorfismo.

Los importes se procesan con Decimal, para evitar errores de coma flotante.
Los registros residen únicamente en memoria; los archivos son solo para logs.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from typing import overload

from .errores import (
    CalculoInconsistenteError, DatoInvalidoError,
    OperacionNoPermitidaError, ParametroFaltanteError,
    ReservaInvalidaError, ServicioNoDisponibleError,
)

CENTAVO = Decimal("0.01")
PATRON_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def texto_obligatorio(valor: object, campo: str, maximo: int = 100) -> str:
    """Normaliza texto y rechaza entradas ausentes o demasiado largas."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ParametroFaltanteError(f"Falta el dato obligatorio: {campo}.")
    if not isinstance(valor, str):
        raise DatoInvalidoError(f"{campo} debe ser texto.")
    resultado = valor.strip()
    if len(resultado) > maximo:
        raise DatoInvalidoError(f"{campo} supera {maximo} caracteres.")
    return resultado


def numero_decimal(valor: object, campo: str, minimo: Decimal = Decimal("0")) -> Decimal:
    """Convierte con encadenamiento de excepciones y comprueba finitud."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ParametroFaltanteError(f"Falta el dato obligatorio: {campo}.")
    if isinstance(valor, bool):
        raise DatoInvalidoError(f"{campo} no admite booleanos.")
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise DatoInvalidoError(f"{campo} debe ser un número válido.") from error
    if not numero.is_finite() or numero < minimo:
        raise DatoInvalidoError(f"{campo} debe ser finito y mayor o igual que {minimo}.")
    return numero


def numero_entero(valor: object, campo: str, minimo: int = 1) -> int:
    """Exige enteros reales, sin redondeos silenciosos."""
    if valor is None or valor == "":
        raise ParametroFaltanteError(f"Falta el dato obligatorio: {campo}.")
    if isinstance(valor, bool):
        raise DatoInvalidoError(f"{campo} debe ser un entero.")
    try:
        resultado = int(valor)
    except (ValueError, TypeError, OverflowError) as error:
        raise DatoInvalidoError(f"{campo} debe ser un entero.") from error
    if isinstance(valor, (float, Decimal)) and (not Decimal(str(valor)).is_finite() or Decimal(str(valor)) != resultado):
        raise DatoInvalidoError(f"{campo} debe ser un entero sin decimales.")
    if isinstance(valor, str) and not re.fullmatch(r"[+-]?\d+", valor.strip()):
        raise DatoInvalidoError(f"{campo} debe ser un entero sin decimales.")
    if resultado < minimo:
        raise DatoInvalidoError(f"{campo} debe ser mayor o igual que {minimo}.")
    return resultado


class Entidad(ABC):
    """Clase abstracta raíz para objetos identificables."""

    def __init__(self, identificador: str):
        self._identificador = texto_obligatorio(identificador, "identificador", 40)

    @property
    def identificador(self) -> str:
        return self._identificador

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""


class Cliente(Entidad):
    """Cliente con datos personales encapsulados y validados."""

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)
        self._nombre = texto_obligatorio(nombre, "nombre", 100)
        self._correo = ""
        self._telefono = ""
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        email = texto_obligatorio(valor, "correo electrónico", 254)
        if not PATRON_CORREO.fullmatch(email):
            raise DatoInvalidoError("El correo electrónico tiene un formato inválido.")
        self._correo = email.lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        telefono = texto_obligatorio(valor, "teléfono", 20)
        if not re.fullmatch(r"\+?\d{7,15}", telefono):
            raise DatoInvalidoError("El teléfono debe tener entre 7 y 15 dígitos; '+' es opcional.")
        self._telefono = telefono

    def describir(self) -> str:
        return f"Cliente {self.identificador}: {self.nombre}"

    def __repr__(self) -> str:
        # Nunca incluimos correo ni teléfono en repr ni en los logs.
        return f"Cliente(id={self.identificador!r}, nombre={self.nombre!r})"


class Servicio(Entidad, ABC):
    """Servicio abstracto con cálculo polimórfico y validación de disponibilidad."""

    def __init__(self, identificador: str, nombre: str, tarifa_hora: object, disponible: bool = True):
        super().__init__(identificador)
        self._nombre = texto_obligatorio(nombre, "nombre del servicio")
        self._tarifa_hora = numero_decimal(tarifa_hora, "tarifa/hora", Decimal("0.01"))
        if not isinstance(disponible, bool):
            raise DatoInvalidoError("La disponibilidad debe ser verdadera o falsa.")
        self._disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, disponible: bool) -> None:
        if not isinstance(disponible, bool):
            raise DatoInvalidoError("La disponibilidad debe ser booleana.")
        self._disponible = disponible

    @abstractmethod
    def validar_parametros(self, duracion: object) -> int:
        """Valida la duración de acuerdo con la clase especializada."""

    @abstractmethod
    def _subtotal(self, duracion: int) -> Decimal:
        """Costo específico del tipo de servicio sin ajustes."""

    @overload
    def calcular_costo(self, duracion: object) -> Decimal: ...

    @overload
    def calcular_costo(self, duracion: object, impuesto: object, descuento: object = 0) -> Decimal: ...

    def calcular_costo(self, duracion: object, impuesto: object = 0, descuento: object = 0) -> Decimal:
        """Variantes con parámetros opcionales y firmas @overload.

        `impuesto` y `descuento` se expresan como proporciones (p. ej., 0.19, 0.10).
        `@overload` documenta las firmas; esta es la implementación ejecutable.
        """
        horas = self.validar_parametros(duracion)
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El servicio {self.identificador} está inactivo.")
        tasa = numero_decimal(impuesto, "impuesto")
        rebaja = numero_decimal(descuento, "descuento")
        if tasa > 1 or rebaja > 1:
            raise CalculoInconsistenteError("Impuesto y descuento deben estar entre 0 y 1.")
        subtotal = self._subtotal(horas)
        total = subtotal * (Decimal("1") - rebaja) * (Decimal("1") + tasa)
        if not total.is_finite() or total < 0:
            raise CalculoInconsistenteError("El costo final es inconsistente.")
        return total.quantize(CENTAVO, rounding=ROUND_HALF_UP)

    @abstractmethod
    def describir(self) -> str:
        """Describe la modalidad del servicio."""


class Sala(Servicio):
    """Reserva de una sala con capacidad física definida."""

    def __init__(self, identificador: str, nombre: str, tarifa_hora: object,
                 capacidad: object, disponible: bool = True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        self.capacidad = numero_entero(capacidad, "capacidad")

    def validar_parametros(self, duracion: object) -> int:
        horas = numero_entero(duracion, "duración")
        if horas > 12:
            raise ReservaInvalidaError("Una sala admite máximo 12 horas por reserva.")
        return horas

    def _subtotal(self, duracion: int) -> Decimal:
        return self._tarifa_hora * duracion

    def describir(self) -> str:
        return f"Sala {self.nombre} (capacidad {self.capacidad}; tarifa ${self._tarifa_hora}/h)"


class Equipo(Servicio):
    """Alquiler de equipos con unidades de inventario disponibles."""

    def __init__(self, identificador: str, nombre: str, tarifa_hora: object,
                 unidades: object, disponible: bool = True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        self.unidades = numero_entero(unidades, "unidades")

    def validar_parametros(self, duracion: object) -> int:
        horas = numero_entero(duracion, "duración")
        if horas > 72:
            raise ReservaInvalidaError("Un equipo admite máximo 72 horas de alquiler.")
        return horas

    def _subtotal(self, duracion: int) -> Decimal:
        return self._tarifa_hora * duracion

    def describir(self) -> str:
        return f"Equipo {self.nombre} ({self.unidades} unidades; tarifa ${self._tarifa_hora}/h)"


class Asesoria(Servicio):
    """Asesoría especializada: duración limitada y cargo fijo por preparación."""

    def __init__(self, identificador: str, nombre: str, tarifa_hora: object,
                 especialidad: str, cargo_preparacion: object = 0, disponible: bool = True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        self.especialidad = texto_obligatorio(especialidad, "especialidad")
        self._cargo_preparacion = numero_decimal(cargo_preparacion, "cargo preparación")

    def validar_parametros(self, duracion: object) -> int:
        horas = numero_entero(duracion, "duración")
        if horas > 8:
            raise ReservaInvalidaError("Una asesoría admite máximo 8 horas por sesión.")
        return horas

    def _subtotal(self, duracion: int) -> Decimal:
        return self._tarifa_hora * duracion + self._cargo_preparacion

    def describir(self) -> str:
        return f"Asesoría {self.nombre} ({self.especialidad}; tarifa ${self._tarifa_hora}/h)"


class Reserva(Entidad):
    """Reserva con estados PENDIENTE, CONFIRMADA y CANCELADA."""

    def __init__(self, identificador: str, cliente: Cliente, servicio: Servicio,
                 inicio: datetime, duracion: object, costo: Decimal):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un cliente y un servicio válidos.")
        if not isinstance(inicio, datetime) or inicio.tzinfo is not None:
            raise ReservaInvalidaError("La fecha debe ser datetime local sin zona horaria.")
        self._cliente = cliente
        self._servicio = servicio
        self._inicio = inicio
        self._duracion = servicio.validar_parametros(duracion)
        self._costo = costo
        self._estado = "PENDIENTE"

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def inicio(self) -> datetime:
        return self._inicio

    @property
    def fin(self) -> datetime:
        return self._inicio + timedelta(hours=self._duracion)

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo(self) -> Decimal:
        return self._costo

    @property
    def duracion(self) -> int:
        return self._duracion

    def confirmar(self) -> None:
        if self.estado != "PENDIENTE":
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva {self.estado}.")
        self._estado = "CONFIRMADA"

    def cancelar(self) -> None:
        if self.estado == "CANCELADA":
            raise OperacionNoPermitidaError("No se puede cancelar dos veces una reserva.")
        self._estado = "CANCELADA"

    def describir(self) -> str:
        return (f"Reserva {self.identificador}: cliente {self.cliente.identificador}, "
                f"servicio {self.servicio.identificador}, {self.inicio:%Y-%m-%d %H:%M}, "
                f"{self.duracion} h, estado {self.estado}, costo ${self.costo}")
