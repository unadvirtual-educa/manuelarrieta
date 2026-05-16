# ============================================================
# entidad.py - Clase abstracta base del sistema
# Software FJ - Sistema Integral de Gestión
# ============================================================

from abc import ABC, abstractmethod
from datetime import datetime


class Entidad(ABC):
    """
    Clase abstracta que representa cualquier entidad del sistema.
    Toda clase concreta del sistema debe heredar de esta.
    """

    def __init__(self, id_entidad: str):
        self._id = id_entidad
        self._fecha_creacion = datetime.now()
        self._activo = True

    @property
    def id(self):
        return self._id

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    @property
    def activo(self):
        return self._activo

    def desactivar(self):
        """Desactiva la entidad del sistema."""
        self._activo = False

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción completa de la entidad."""
        pass

    @abstractmethod
    def validar(self) -> bool:
        """Valida que la entidad tenga datos consistentes."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._id})"
