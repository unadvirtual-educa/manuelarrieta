# ============================================================
# excepciones.py - Excepciones personalizadas del sistema
# Software FJ - Sistema Integral de Gestión
# ============================================================

class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje, codigo=None):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje

    def __str__(self):
        if self.codigo:
            return f"[Error {self.codigo}] {self.mensaje}"
        return self.mensaje


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente son inválidos."""
    def __init__(self, campo, valor):
        mensaje = f"Dato inválido en campo '{campo}': '{valor}'"
        super().__init__(mensaje, codigo="CLI-001")
        self.campo = campo
        self.valor = valor


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio no está disponible."""
    def __init__(self, nombre_servicio):
        mensaje = f"El servicio '{nombre_servicio}' no está disponible"
        super().__init__(mensaje, codigo="SRV-001")


class ParametroInvalidoError(SoftwareFJError):
    """Se lanza cuando un parámetro no cumple las restricciones."""
    def __init__(self, parametro, razon):
        mensaje = f"Parámetro inválido '{parametro}': {razon}"
        super().__init__(mensaje, codigo="PRM-001")


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no puede crearse o procesarse."""
    def __init__(self, razon):
        mensaje = f"Reserva inválida: {razon}"
        super().__init__(mensaje, codigo="RSV-001")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una operación no permitida."""
    def __init__(self, operacion, estado_actual):
        mensaje = f"Operación '{operacion}' no permitida en estado '{estado_actual}'"
        super().__init__(mensaje, codigo="OPR-001")


class CalculoCostoError(SoftwareFJError):
    """Se lanza cuando hay una inconsistencia en el cálculo de costos."""
    def __init__(self, detalle):
        mensaje = f"Error en cálculo de costo: {detalle}"
        super().__init__(mensaje, codigo="CST-001")
