# ============================================================
# cliente.py - Clase Cliente con validaciones robustas
# Software FJ - Sistema Integral de Gestión
# ============================================================

import re
from entidad import Entidad
from excepciones import ClienteInvalidoError


class Cliente(Entidad):
    """
    Clase que representa un cliente del sistema Software FJ.
    Implementa encapsulación completa de datos personales
    y validaciones robustas en cada campo.
    """

    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        try:
            super().__init__(id_cliente)
            # Cada setter valida antes de asignar
            self.nombre = nombre
            self.email = email
            self.telefono = telefono
            self._reservas_activas = []
        except ClienteInvalidoError:
            raise
        except Exception as e:
            raise ClienteInvalidoError("general", str(e)) from e

    # ── Propiedades con validación ──────────────────────────

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str):
            raise ClienteInvalidoError("nombre", valor)
        valor = valor.strip()
        if len(valor) < 2 or len(valor) > 100:
            raise ClienteInvalidoError("nombre", f"{valor!r} (debe tener entre 2 y 100 caracteres)")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", valor):
            raise ClienteInvalidoError("nombre", f"{valor!r} (solo se permiten letras y espacios)")
        self._nombre = valor

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if not valor or not isinstance(valor, str):
            raise ClienteInvalidoError("email", valor)
        valor = valor.strip().lower()
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron, valor):
            raise ClienteInvalidoError("email", f"{valor!r} (formato inválido)")
        self._email = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor or not isinstance(valor, str):
            raise ClienteInvalidoError("telefono", valor)
        valor = valor.strip().replace(" ", "").replace("-", "")
        if not valor.lstrip("+").isdigit() or len(valor) < 7 or len(valor) > 15:
            raise ClienteInvalidoError("telefono", f"{valor!r} (debe tener entre 7 y 15 dígitos)")
        self._telefono = valor

    @property
    def reservas_activas(self):
        return list(self._reservas_activas)

    def agregar_reserva(self, reserva):
        """Registra una reserva activa para este cliente."""
        self._reservas_activas.append(reserva)

    def eliminar_reserva(self, id_reserva: str):
        """Elimina una reserva de la lista del cliente."""
        self._reservas_activas = [
            r for r in self._reservas_activas if r.id != id_reserva
        ]

    # ── Métodos abstractos implementados ───────────────────

    def describir(self) -> str:
        return (
            f"Cliente [{self._id}]\n"
            f"  Nombre  : {self._nombre}\n"
            f"  Email   : {self._email}\n"
            f"  Teléfono: {self._telefono}\n"
            f"  Reservas activas: {len(self._reservas_activas)}\n"
            f"  Creado  : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
        )

    def validar(self) -> bool:
        try:
            assert self._nombre and len(self._nombre) >= 2
            assert "@" in self._email
            assert len(self._telefono) >= 7
            return True
        except AssertionError:
            return False
