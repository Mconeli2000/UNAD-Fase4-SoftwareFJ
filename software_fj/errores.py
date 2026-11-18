"""Jerarquía de errores de negocio del sistema Software FJ.

Separar errores específicos permite responder de forma controlada,
registrarlos sin exponer datos personales y seguir ejecutando el sistema.
"""


class GestionError(Exception):
    """Error esperado y recuperable del dominio de gestión."""


class DatoInvalidoError(GestionError):
    """Un valor no cumple las reglas de entrada."""


class ParametroFaltanteError(DatoInvalidoError):
    """Se omitió un dato obligatorio."""


class RegistroDuplicadoError(GestionError):
    """Ya existe una entidad con el mismo identificador."""


class EntidadNoEncontradaError(GestionError):
    """No se encuentra el registro solicitado."""


class ServicioNoDisponibleError(GestionError):
    """El recurso o el servicio no está disponible."""


class ReservaInvalidaError(GestionError):
    """La reserva no puede crearse o confirmarse."""


class OperacionNoPermitidaError(GestionError):
    """La transición de estado solicitada no está permitida."""


class CalculoInconsistenteError(GestionError):
    """Los importes o parámetros producen un cálculo inválido."""
