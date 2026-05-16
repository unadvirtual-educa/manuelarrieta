# ============================================================
# reserva.py - Clase Reserva con manejo completo de excepciones
# Software FJ - Sistema Integral de Gestión
# ============================================================

from datetime import datetime
from entidad import Entidad
from excepciones import (ReservaInvalidaError,
                          OperacionNoPermitidaError,
                          CalculoCostoError,
                          ParametroInvalidoError)

ESTADOS = ["pendiente", "confirmada", "cancelada", "completada"]


class Reserva(Entidad):
    """
    Clase que integra Cliente, Servicio, duración y estado.
    Implementa confirmación, cancelación y procesamiento
    con manejo robusto de excepciones en cada operación.
    """

    def __init__(self, id_reserva: str, cliente, servicio, horas: float,
                 descuento: float = 0.0):
        try:
            super().__init__(id_reserva)
            self._validar_cliente(cliente)
            self._validar_servicio(servicio)
            self._validar_horas(horas, servicio)
            self._validar_descuento(descuento)

            self._cliente = cliente
            self._servicio = servicio
            self._horas = horas
            self._descuento = descuento
            self._estado = "pendiente"
            self._costo_final = None
            self._fecha_confirmacion = None
            self._fecha_cancelacion = None
            self._motivo_cancelacion = ""

        except (ReservaInvalidaError, ParametroInvalidoError):
            raise
        except Exception as e:
            raise ReservaInvalidaError(str(e)) from e

    # ── Validaciones internas ───────────────────────────────

    def _validar_cliente(self, cliente):
        if cliente is None:
            raise ReservaInvalidaError("El cliente no puede ser None")
        if not cliente.validar():
            raise ReservaInvalidaError(f"Cliente inválido: {cliente.id}")
        if not cliente.activo:
            raise ReservaInvalidaError(f"El cliente {cliente.id} está inactivo")

    def _validar_servicio(self, servicio):
        if servicio is None:
            raise ReservaInvalidaError("El servicio no puede ser None")
        servicio.verificar_disponibilidad()

    def _validar_horas(self, horas, servicio):
        if not isinstance(horas, (int, float)):
            raise ParametroInvalidoError("horas", "Debe ser un número")
        if not servicio.validar_parametros(horas=horas):
            raise ParametroInvalidoError(
                "horas",
                f"Fuera del rango permitido para {servicio.nombre}"
            )

    def _validar_descuento(self, descuento):
        if not isinstance(descuento, (int, float)):
            raise ParametroInvalidoError("descuento", "Debe ser numérico")
        if not 0 <= descuento <= 100:
            raise ParametroInvalidoError("descuento", "Debe estar entre 0 y 100")

    # ── Propiedades ─────────────────────────────────────────

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self):
        return self._horas

    @property
    def descuento(self):
        return self._descuento

    @property
    def estado(self):
        return self._estado

    @property
    def costo_final(self):
        return self._costo_final

    # ── Operaciones principales ─────────────────────────────

    def confirmar(self) -> str:
        """
        Confirma la reserva. Solo puede hacerse en estado 'pendiente'.
        Usa try/except/else/finally para manejar el flujo.
        """
        try:
            if self._estado != "pendiente":
                raise OperacionNoPermitidaError("confirmar", self._estado)

            costo = self._servicio.calcular_costo_total(
                self._horas,
                descuento=self._descuento,
                aplicar_iva=True
            )

        except OperacionNoPermitidaError:
            raise
        except CalculoCostoError as e:
            raise ReservaInvalidaError(
                f"No se pudo calcular el costo: {e}"
            ) from e
        except Exception as e:
            raise ReservaInvalidaError(f"Error al confirmar: {e}") from e
        else:
            # Solo se ejecuta si no hubo excepción
            self._estado = "confirmada"
            self._costo_final = costo
            self._fecha_confirmacion = datetime.now()
            self._cliente.agregar_reserva(self)
            return (f"Reserva {self._id} confirmada. "
                    f"Costo total (con IVA): ${costo:,.0f}")
        finally:
            # Siempre se ejecuta
            pass  # Aquí iría limpieza si fuera necesaria

    def cancelar(self, motivo: str = "Sin motivo especificado") -> str:
        """
        Cancela la reserva. No se puede cancelar una reserva completada.
        """
        try:
            if self._estado == "completada":
                raise OperacionNoPermitidaError("cancelar", self._estado)
            if self._estado == "cancelada":
                raise OperacionNoPermitidaError("cancelar (ya cancelada)", self._estado)
            if not motivo or not motivo.strip():
                raise ParametroInvalidoError("motivo", "No puede estar vacío")

        except (OperacionNoPermitidaError, ParametroInvalidoError):
            raise
        except Exception as e:
            raise ReservaInvalidaError(f"Error al cancelar: {e}") from e
        else:
            estado_anterior = self._estado
            self._estado = "cancelada"
            self._fecha_cancelacion = datetime.now()
            self._motivo_cancelacion = motivo
            self._cliente.eliminar_reserva(self._id)
            return (f"Reserva {self._id} cancelada "
                    f"(estaba en estado: {estado_anterior}). Motivo: {motivo}")
        finally:
            pass

    def completar(self) -> str:
        """
        Marca la reserva como completada. Solo si está confirmada.
        """
        try:
            if self._estado != "confirmada":
                raise OperacionNoPermitidaError("completar", self._estado)
        except OperacionNoPermitidaError:
            raise
        else:
            self._estado = "completada"
            return f"Reserva {self._id} marcada como completada."
        finally:
            pass

    # ── Métodos abstractos implementados ───────────────────

    def describir(self) -> str:
        costo_str = f"${self._costo_final:,.0f}" if self._costo_final else "Pendiente"
        return (
            f"Reserva [{self._id}]\n"
            f"  Cliente  : {self._cliente.nombre}\n"
            f"  Servicio : {self._servicio.nombre}\n"
            f"  Horas    : {self._horas}\n"
            f"  Descuento: {self._descuento}%\n"
            f"  Estado   : {self._estado.upper()}\n"
            f"  Costo    : {costo_str}\n"
            f"  Creada   : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
        )

    def validar(self) -> bool:
        try:
            return (
                self._cliente is not None
                and self._servicio is not None
                and self._horas > 0
                and self._estado in ESTADOS
            )
        except Exception:
            return False
