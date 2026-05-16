# ============================================================
# servicio.py - Clase abstracta Servicio y servicios especializados
# Software FJ - Sistema Integral de Gestión
# ============================================================

from abc import abstractmethod
from entidad import Entidad
from excepciones import (ServicioNoDisponibleError,
                          ParametroInvalidoError,
                          CalculoCostoError)

IVA = 0.19  # Impuesto aplicable en Colombia


class Servicio(Entidad):
    """
    Clase abstracta que representa cualquier servicio ofrecido
    por Software FJ. Define la interfaz común para todos los servicios.
    """

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_servicio)
        if tarifa_base < 0:
            raise ParametroInvalidoError("tarifa_base", "no puede ser negativa")
        self._nombre = nombre
        self._tarifa_base = tarifa_base
        self._disponible = disponible

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool):
        self._disponible = valor

    def verificar_disponibilidad(self):
        """Lanza excepción si el servicio no está disponible."""
        if not self._disponible:
            raise ServicioNoDisponibleError(self._nombre)

    # ── Métodos sobrecargados (variantes de cálculo de costo) ──

    def calcular_costo(self, horas: float) -> float:
        """Costo base sin impuestos ni descuentos."""
        return self._calcular_base(horas)

    def calcular_costo_con_iva(self, horas: float) -> float:
        """Costo con IVA incluido."""
        base = self._calcular_base(horas)
        return round(base * (1 + IVA), 2)

    def calcular_costo_con_descuento(self, horas: float, descuento: float) -> float:
        """Costo con descuento porcentual aplicado (antes de IVA)."""
        if not 0 <= descuento <= 100:
            raise CalculoCostoError(f"Descuento {descuento}% fuera de rango (0-100)")
        base = self._calcular_base(horas)
        return round(base * (1 - descuento / 100), 2)

    def calcular_costo_total(self, horas: float, descuento: float = 0.0, aplicar_iva: bool = True) -> float:
        """
        Método sobrecargado completo:
        Costo con descuento opcional e IVA opcional.
        """
        if horas <= 0:
            raise CalculoCostoError(f"Las horas deben ser positivas, recibido: {horas}")
        base = self._calcular_base(horas)
        if descuento:
            if not 0 <= descuento <= 100:
                raise CalculoCostoError(f"Descuento inválido: {descuento}%")
            base = base * (1 - descuento / 100)
        if aplicar_iva:
            base = base * (1 + IVA)
        return round(base, 2)

    def _calcular_base(self, horas: float) -> float:
        """Cálculo base que puede ser sobreescrito por subclases."""
        if horas <= 0:
            raise CalculoCostoError(f"Horas inválidas: {horas}")
        return self._tarifa_base * horas

    # ── Métodos abstractos ──────────────────────────────────

    @abstractmethod
    def calcular_costo(self, horas: float) -> float:
        pass

    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        pass

    def validar(self) -> bool:
        return self._tarifa_base >= 0 and bool(self._nombre)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Servicio [{self._id}] - {self._nombre}\n"
            f"  Tarifa base : ${self._tarifa_base:,.0f}/hora\n"
            f"  Estado      : {estado}"
        )


# ════════════════════════════════════════════════════════════
#  SERVICIO 1: Reserva de Sala
# ════════════════════════════════════════════════════════════

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de estudio o reunión.
    La tarifa varía según la capacidad de la sala.
    """

    CAPACIDADES_VALIDAS = [5, 10, 20, 50]

    def __init__(self, id_servicio: str, nombre: str, capacidad: int, disponible: bool = True):
        if capacidad not in self.CAPACIDADES_VALIDAS:
            raise ParametroInvalidoError(
                "capacidad",
                f"Debe ser una de: {self.CAPACIDADES_VALIDAS}"
            )
        # La tarifa base depende de la capacidad
        tarifa = 15000 + (capacidad * 500)
        super().__init__(id_servicio, nombre, tarifa, disponible)
        self._capacidad = capacidad

    @property
    def capacidad(self):
        return self._capacidad

    def calcular_costo(self, horas: float) -> float:
        """Costo por horas reservadas."""
        self.verificar_disponibilidad()
        if horas <= 0 or horas > 12:
            raise ParametroInvalidoError("horas", "Debe estar entre 0 y 12 horas")
        return round(self._tarifa_base * horas, 2)

    def validar_parametros(self, **kwargs) -> bool:
        horas = kwargs.get("horas", 0)
        return 0 < horas <= 12

    def describir(self) -> str:
        base = super().describir()
        return base + f"\n  Tipo        : Reserva de Sala\n  Capacidad   : {self._capacidad} personas"


# ════════════════════════════════════════════════════════════
#  SERVICIO 2: Alquiler de Equipos
# ════════════════════════════════════════════════════════════

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    Incluye recargo por equipos de alta gama.
    """

    TIPOS_EQUIPO = {
        "basico": 1.0,
        "intermedio": 1.5,
        "alta_gama": 2.5
    }

    def __init__(self, id_servicio: str, nombre: str, tipo_equipo: str, disponible: bool = True):
        tipo = tipo_equipo.lower()
        if tipo not in self.TIPOS_EQUIPO:
            raise ParametroInvalidoError(
                "tipo_equipo",
                f"Debe ser uno de: {list(self.TIPOS_EQUIPO.keys())}"
            )
        tarifa_base = 20000
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        self._tipo_equipo = tipo
        self._multiplicador = self.TIPOS_EQUIPO[tipo]

    @property
    def tipo_equipo(self):
        return self._tipo_equipo

    def calcular_costo(self, horas: float) -> float:
        """Costo con recargo según tipo de equipo."""
        self.verificar_disponibilidad()
        if horas <= 0 or horas > 72:
            raise ParametroInvalidoError("horas", "Debe estar entre 0 y 72 horas")
        return round(self._tarifa_base * self._multiplicador * horas, 2)

    def validar_parametros(self, **kwargs) -> bool:
        horas = kwargs.get("horas", 0)
        return 0 < horas <= 72

    def describir(self) -> str:
        base = super().describir()
        return (
            base
            + f"\n  Tipo        : Alquiler de Equipo"
            + f"\n  Categoría   : {self._tipo_equipo} (x{self._multiplicador})"
        )


# ════════════════════════════════════════════════════════════
#  SERVICIO 3: Asesoría Especializada
# ════════════════════════════════════════════════════════════

class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría especializada en distintas áreas.
    El costo varía según el nivel del asesor.
    """

    NIVELES = {
        "junior": 50000,
        "senior": 100000,
        "experto": 180000
    }

    def __init__(self, id_servicio: str, nombre: str, area: str,
                 nivel_asesor: str, disponible: bool = True):
        nivel = nivel_asesor.lower()
        if nivel not in self.NIVELES:
            raise ParametroInvalidoError(
                "nivel_asesor",
                f"Debe ser uno de: {list(self.NIVELES.keys())}"
            )
        tarifa = self.NIVELES[nivel]
        super().__init__(id_servicio, nombre, tarifa, disponible)
        self._area = area
        self._nivel_asesor = nivel

    @property
    def area(self):
        return self._area

    @property
    def nivel_asesor(self):
        return self._nivel_asesor

    def calcular_costo(self, horas: float) -> float:
        """Costo según horas y nivel del asesor."""
        self.verificar_disponibilidad()
        if horas <= 0 or horas > 8:
            raise ParametroInvalidoError("horas", "Asesorías máximo 8 horas por sesión")
        return round(self._tarifa_base * horas, 2)

    def validar_parametros(self, **kwargs) -> bool:
        horas = kwargs.get("horas", 0)
        return 0 < horas <= 8

    def describir(self) -> str:
        base = super().describir()
        return (
            base
            + f"\n  Tipo        : Asesoría Especializada"
            + f"\n  Área        : {self._area}"
            + f"\n  Nivel asesor: {self._nivel_asesor}"
        )
