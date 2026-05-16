# ============================================================
# sistema.py - Sistema principal con logger y 10 operaciones
# Software FJ - Sistema Integral de Gestión
# ============================================================

import logging
import os
from datetime import datetime

from cliente import Cliente
from servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reserva import Reserva
from excepciones import (SoftwareFJError, ClienteInvalidoError,
                          ServicioNoDisponibleError, ReservaInvalidaError,
                          OperacionNoPermitidaError, ParametroInvalidoError)

# ── Configuración del logger ────────────────────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/eventos.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SoftwareFJ")


def log_evento(mensaje: str, nivel: str = "info"):
    """Registra un evento en el log con el nivel apropiado."""
    niveles = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical
    }
    niveles.get(nivel, logger.info)(mensaje)


class SistemaFJ:
    """
    Sistema central que gestiona clientes, servicios y reservas.
    Mantiene listas internas de cada entidad sin uso de base de datos.
    """

    def __init__(self):
        self._clientes: dict = {}
        self._servicios: dict = {}
        self._reservas: dict = {}
        self._contador_reserva = 1
        log_evento("Sistema Software FJ iniciado correctamente.", "info")

    # ── Gestión de Clientes ─────────────────────────────────

    def registrar_cliente(self, id_c, nombre, email, telefono) -> Cliente | None:
        try:
            if id_c in self._clientes:
                raise ReservaInvalidaError(f"Ya existe un cliente con ID {id_c}")
            cliente = Cliente(id_c, nombre, email, telefono)
            self._clientes[id_c] = cliente
            log_evento(f"Cliente registrado: {id_c} - {nombre}", "info")
            return cliente
        except ClienteInvalidoError as e:
            log_evento(f"Cliente inválido [{id_c}]: {e}", "error")
            return None
        except SoftwareFJError as e:
            log_evento(f"Error de sistema al registrar cliente: {e}", "error")
            return None
        except Exception as e:
            log_evento(f"Error inesperado al registrar cliente: {e}", "critical")
            return None

    def obtener_cliente(self, id_c) -> Cliente | None:
        cliente = self._clientes.get(id_c)
        if not cliente:
            log_evento(f"Cliente no encontrado: {id_c}", "warning")
        return cliente

    # ── Gestión de Servicios ────────────────────────────────

    def registrar_servicio(self, servicio) -> bool:
        try:
            if servicio.id in self._servicios:
                raise SoftwareFJError(f"Ya existe un servicio con ID {servicio.id}")
            self._servicios[servicio.id] = servicio
            log_evento(f"Servicio registrado: {servicio.id} - {servicio.nombre}", "info")
            return True
        except SoftwareFJError as e:
            log_evento(f"Error al registrar servicio: {e}", "error")
            return False
        except Exception as e:
            log_evento(f"Error inesperado al registrar servicio: {e}", "critical")
            return False

    def obtener_servicio(self, id_s):
        return self._servicios.get(id_s)

    def listar_servicios(self) -> list:
        return list(self._servicios.values())

    # ── Gestión de Reservas ─────────────────────────────────

    def crear_reserva(self, id_cliente, id_servicio,
                      horas, descuento=0.0) -> Reserva | None:
        try:
            cliente = self._clientes.get(id_cliente)
            if not cliente:
                raise ReservaInvalidaError(f"Cliente '{id_cliente}' no encontrado")

            servicio = self._servicios.get(id_servicio)
            if not servicio:
                raise ReservaInvalidaError(f"Servicio '{id_servicio}' no encontrado")

            id_reserva = f"RES-{self._contador_reserva:03d}"
            self._contador_reserva += 1

            reserva = Reserva(id_reserva, cliente, servicio, horas, descuento)
            self._reservas[id_reserva] = reserva
            log_evento(f"Reserva creada: {id_reserva} | {cliente.nombre} | {servicio.nombre}", "info")
            return reserva

        except (ReservaInvalidaError, ParametroInvalidoError,
                ServicioNoDisponibleError) as e:
            log_evento(f"Reserva fallida: {e}", "error")
            return None
        except Exception as e:
            log_evento(f"Error inesperado al crear reserva: {e}", "critical")
            return None

    def confirmar_reserva(self, id_reserva) -> str:
        try:
            reserva = self._reservas.get(id_reserva)
            if not reserva:
                raise ReservaInvalidaError(f"Reserva '{id_reserva}' no encontrada")
            resultado = reserva.confirmar()
            log_evento(f"Reserva confirmada: {id_reserva}", "info")
            return resultado
        except (ReservaInvalidaError, OperacionNoPermitidaError) as e:
            log_evento(f"Error al confirmar {id_reserva}: {e}", "error")
            return str(e)
        except Exception as e:
            log_evento(f"Error inesperado al confirmar: {e}", "critical")
            return str(e)

    def cancelar_reserva(self, id_reserva, motivo) -> str:
        try:
            reserva = self._reservas.get(id_reserva)
            if not reserva:
                raise ReservaInvalidaError(f"Reserva '{id_reserva}' no encontrada")
            resultado = reserva.cancelar(motivo)
            log_evento(f"Reserva cancelada: {id_reserva}. {motivo}", "warning")
            return resultado
        except (ReservaInvalidaError, OperacionNoPermitidaError) as e:
            log_evento(f"Error al cancelar {id_reserva}: {e}", "error")
            return str(e)

    def listar_reservas(self) -> list:
        return list(self._reservas.values())

    def listar_clientes(self) -> list:
        return list(self._clientes.values())


# ════════════════════════════════════════════════════════════
#  10 OPERACIONES DE DEMOSTRACIÓN
# ════════════════════════════════════════════════════════════

def ejecutar_demo(sistema: SistemaFJ) -> list:
    """
    Ejecuta 10 operaciones completas (válidas e inválidas)
    y retorna una lista de resultados para mostrar en la UI.
    """
    resultados = []

    def reg(titulo, descripcion, tipo="info"):
        resultados.append({"titulo": titulo, "descripcion": descripcion, "tipo": tipo})
        log_evento(f"[DEMO] {titulo}: {descripcion}", tipo)

    separador = "─" * 55

    # ── Registrar servicios disponibles ────────────────────
    sala1 = ReservaSala("SRV-001", "Sala Innovación", capacidad=10)
    equipo1 = AlquilerEquipo("SRV-002", "Laptop Gamer", tipo_equipo="alta_gama")
    asesoria1 = AsesoriaEspecializada("SRV-003", "Asesoría Python", area="Programación", nivel_asesor="senior")
    sala_inactiva = ReservaSala("SRV-004", "Sala Mantenimiento", capacidad=5, disponible=False)

    for srv in [sala1, equipo1, asesoria1, sala_inactiva]:
        sistema.registrar_servicio(srv)

    # ══ OPERACIÓN 1: Cliente válido ═════════════════════════
    c1 = sistema.registrar_cliente("CLI-001", "Ana Torres", "ana.torres@email.com", "3001234567")
    if c1:
        reg("OP1 - Cliente válido registrado", c1.describir(), "info")
    else:
        reg("OP1 - Error", "No se pudo registrar el cliente", "error")

    # ══ OPERACIÓN 2: Cliente con email inválido ═════════════
    c2 = sistema.registrar_cliente("CLI-002", "Luis Gómez", "email_invalido", "3009876543")
    if c2:
        reg("OP2 - Debería haber fallado", "Email inválido aceptado", "error")
    else:
        reg("OP2 - Email inválido rechazado", "ClienteInvalidoError capturada correctamente", "warning")

    # ══ OPERACIÓN 3: Cliente con nombre inválido ════════════
    c3 = sistema.registrar_cliente("CLI-003", "123 Nombre", "valido@email.com", "3112223333")
    if c3:
        reg("OP3 - Debería haber fallado", "Nombre con números aceptado", "error")
    else:
        reg("OP3 - Nombre inválido rechazado", "ClienteInvalidoError capturada correctamente", "warning")

    # ══ OPERACIÓN 4: Segundo cliente válido ═════════════════
    c4 = sistema.registrar_cliente("CLI-004", "María Rodríguez", "maria.r@empresa.co", "6017654321")
    if c4:
        reg("OP4 - Cliente válido registrado", c4.describir(), "info")

    # ══ OPERACIÓN 5: Reserva válida de sala ═════════════════
    r1 = sistema.crear_reserva("CLI-001", "SRV-001", horas=3, descuento=10)
    if r1:
        resultado_conf = sistema.confirmar_reserva(r1.id)
        reg("OP5 - Reserva sala confirmada", resultado_conf, "info")
    else:
        reg("OP5 - Error al crear reserva de sala", "Fallo inesperado", "error")

    # ══ OPERACIÓN 6: Reserva con servicio no disponible ═════
    r2 = sistema.crear_reserva("CLI-004", "SRV-004", horas=2)
    if r2:
        reg("OP6 - Debería haber fallado", "Servicio inactivo aceptado", "error")
    else:
        reg("OP6 - Servicio no disponible rechazado", "ServicioNoDisponibleError capturada", "warning")

    # ══ OPERACIÓN 7: Reserva con horas fuera de rango ═══════
    r3 = sistema.crear_reserva("CLI-001", "SRV-003", horas=15)  # Asesoría máx 8h
    if r3:
        reg("OP7 - Debería haber fallado", "Horas inválidas aceptadas", "error")
    else:
        reg("OP7 - Horas inválidas rechazadas", "ParametroInvalidoError capturada (máx 8h para asesoría)", "warning")

    # ══ OPERACIÓN 8: Cancelar reserva válida ════════════════
    r4 = sistema.crear_reserva("CLI-004", "SRV-002", horas=5, descuento=0)
    if r4:
        sistema.confirmar_reserva(r4.id)
        resultado_cancel = sistema.cancelar_reserva(r4.id, "Cliente canceló por agenda")
        reg("OP8 - Reserva cancelada correctamente", resultado_cancel, "warning")

    # ══ OPERACIÓN 9: Doble cancelación (error esperado) ═════
    if r4:
        resultado_doble = sistema.cancelar_reserva(r4.id, "Intento de doble cancelación")
        reg("OP9 - Doble cancelación rechazada", f"OperacionNoPermitidaError: {resultado_doble}", "warning")

    # ══ OPERACIÓN 10: Cálculo de costos con variantes ═══════
    try:
        costo_base = sala1.calcular_costo(4)
        costo_iva = sala1.calcular_costo_con_iva(4)
        costo_desc = sala1.calcular_costo_con_descuento(4, 15)
        costo_total = sala1.calcular_costo_total(4, descuento=15, aplicar_iva=True)
        detalle = (
            f"Sala Innovación – 4 horas\n"
            f"  Base            : ${costo_base:,.0f}\n"
            f"  Con IVA (19%)   : ${costo_iva:,.0f}\n"
            f"  Con 15% descuento: ${costo_desc:,.0f}\n"
            f"  Total (desc+IVA): ${costo_total:,.0f}"
        )
        reg("OP10 - Métodos sobrecargados de costo", detalle, "info")
    except Exception as e:
        reg("OP10 - Error en cálculo", str(e), "error")

    return resultados
