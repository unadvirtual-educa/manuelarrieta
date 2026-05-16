# ============================================================
# main.py - Punto de entrada con interfaz Tkinter
# Software FJ - Sistema Integral de Gestión
# Estudiante: Manuel Arrieta
# Código: 
# Grupo Nº: 
# Fecha: Mayo de 2026
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from cliente import Cliente
from servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reserva import Reserva
from sistema import SistemaFJ, ejecutar_demo
from excepciones import (ClienteInvalidoError, ReservaInvalidaError,
                          ParametroInvalidoError, ServicioNoDisponibleError,
                          OperacionNoPermitidaError)

# ── Paleta de colores ────────────────────────────────────────
C_BG      = "#f5f5f5"   # Fondo general: gris muy claro
C_PANEL   = "#e0e0e0"   # Paneles y sidebar: gris claro
C_ACCENT  = "#424242"   # Botones principales: gris oscuro
C_ACCENT2 = "#616161"   # Botones secundarios: gris medio
C_SUCCESS = "#388e3c"   # Confirmaciones: verde oscuro sobrio
C_WARNING = "#5d4037"   # Advertencias: café oscuro
C_ERROR   = "#b71c1c"   # Errores: rojo oscuro sobrio
C_TEXT    = "#212121"   # Texto principal: casi negro
# C_MUTED   = "#757575"   # Texto secundario: gris medio
C_MUTED   = "#e0e0e0"   # Texto secundario: gris medio
C_WHITE   = "#ffffff"   # Blanco puro


class AppSoftwareFJ:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Software FJ – Sistema Integral de Gestión")
        self.root.geometry("1050x700")
        self.root.configure(bg=C_ACCENT2)
        self.root.resizable(True, True)

        self.sistema = SistemaFJ()
        self._inicializar_datos_demo()
        self._construir_ui()

    def _inicializar_datos_demo(self):
        """Carga datos de ejemplo para que la app no empiece vacía."""
        s1 = ReservaSala("SRV-001", "Sala Innovation", capacidad=10)
        s2 = AlquilerEquipo("SRV-002", "Laptop Pro", tipo_equipo="alta_gama")
        s3 = AsesoriaEspecializada("SRV-003", "Asesoría Python",
                                    area="Programación", nivel_asesor="senior")
        s4 = ReservaSala("SRV-004", "Sala Pequeña", capacidad=5)
        s5 = AlquilerEquipo("SRV-005", "Proyector HD", tipo_equipo="intermedio")
        for s in [s1, s2, s3, s4, s5]:
            self.sistema.registrar_servicio(s)

        self.sistema.registrar_cliente(
            "CLI-001", "Ana Torres", "ana.torres@email.com", "3001234567")
        self.sistema.registrar_cliente(
            "CLI-002", "Carlos Díaz", "carlos.diaz@empresa.co", "3112223344")

    # ════════════════════════════════════════════════════════
    #  UI PRINCIPAL
    # ════════════════════════════════════════════════════════

    def _construir_ui(self):
        # Barra lateral izquierda
        sidebar = tk.Frame(self.root, bg=C_PANEL, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Software FJ", bg=C_PANEL,
                 fg=C_ACCENT2, font=("Arial", 14, "bold")).pack(pady=(20, 5))
        tk.Label(sidebar, text="Sistema de Gestión", bg=C_PANEL,
                 fg=C_ACCENT2, font=("Arial", 9)).pack(pady=(0, 20))

        self.contenido = tk.Frame(self.root, bg=C_BG)
        self.contenido.pack(side="right", fill="both", expand=True)

        botones_nav = [
            ("Inicio / Demo",    self._mostrar_demo),
            ("Clientes",         self._mostrar_clientes),
            ("Servicios",        self._mostrar_servicios),
            ("Reservas",         self._mostrar_reservas),
            ("Nueva Reserva",    self._mostrar_nueva_reserva),
            ("Log de Eventos",   self._mostrar_log),
        ]

        for texto, comando in botones_nav:
            btn = tk.Button(
                sidebar, text=texto, bg=C_PANEL, fg=C_TEXT,
                font=("Arial", 10), bd=0, pady=12, anchor="w", padx=16,
                activebackground=C_ACCENT2, activeforeground=C_WHITE,
                cursor="hand2", command=comando
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#A0A0A0"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=C_PANEL))

       
        # Nombre del autor en la parte inferior del sidebar
        tk.Label(sidebar, text="by Manuel Arrieta", bg=C_PANEL,
                 fg=C_ACCENT, font=("Arial", 8, "italic")).pack(
                 side="bottom", pady=10)

        self._mostrar_demo()
    

    def _limpiar_contenido(self):
        for w in self.contenido.winfo_children():
            w.destroy()

    def _titulo(self, parent, texto):
        tk.Label(parent, text=texto, bg=C_BG, fg=C_ACCENT2,
                 font=("Arial", 15, "bold")).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Frame(parent, bg=C_ACCENT, height=2).pack(fill="x", padx=24, pady=(0, 16))

    # ════════════════════════════════════════════════════════
    #  PANTALLA: DEMO (10 OPERACIONES)
    # ════════════════════════════════════════════════════════

    def _mostrar_demo(self):
        self._limpiar_contenido()
        self._titulo(self.contenido, "Demostración – 10 Operaciones del Sistema")
        

        info = tk.Label(self.contenido,
            text="Presiona el botón para ejecutar las 10 operaciones de prueba (válidas e inválidas).",
            bg=C_BG, fg=C_ACCENT2, font=("Arial", 10))
        info.pack(anchor="w", padx=24, pady=(0, 10))

        btn = tk.Button(self.contenido, text="Ejecutar Demo",
                        bg=C_ACCENT, fg=C_WHITE, font=("Arial", 11, "bold"),
                        padx=20, pady=8, bd=0, cursor="hand2",
                        command=self._correr_demo)
        btn.pack(anchor="w", padx=24, pady=(0, 16))

        self.frame_demo_resultados = tk.Frame(self.contenido, bg=C_BG)
        self.frame_demo_resultados.pack(fill="both", expand=True, padx=24)

    def _correr_demo(self):
        for w in self.frame_demo_resultados.winfo_children():
            w.destroy()

        sistema_demo = SistemaFJ()
        resultados = ejecutar_demo(sistema_demo)

        canvas = tk.Canvas(self.frame_demo_resultados, bg=C_BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self.frame_demo_resultados, orient="vertical", command=canvas.yview)
        frame_scroll = tk.Frame(canvas, bg=C_BG)

        frame_scroll.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        colores = {"info": C_SUCCESS, "warning": C_WARNING,
                   "error": C_ERROR, "critical": C_ERROR}

        for r in resultados:
            color = colores.get(r["tipo"], C_TEXT)
            card = tk.Frame(frame_scroll, bg=C_PANEL, pady=8, padx=12)
            card.pack(fill="x", pady=4)
            tk.Label(card, text=r["titulo"], bg=C_PANEL,
                     fg=color, font=("Arial", 10, "bold"),
                     anchor="w").pack(fill="x")
            tk.Label(card, text=r["descripcion"], bg=C_PANEL,
                     fg=C_MUTED, font=("Courier", 9),
                     anchor="w", justify="left",
                     wraplength=750).pack(fill="x")

    # ════════════════════════════════════════════════════════
    #  PANTALLA: CLIENTES
    # ════════════════════════════════════════════════════════

    def _mostrar_clientes(self):
        self._limpiar_contenido()
        self._titulo(self.contenido, "Gestión de Clientes")

        # Formulario
        form = tk.Frame(self.contenido, bg=C_PANEL, padx=16, pady=12)
        form.pack(fill="x", padx=24, pady=(0, 14))

        campos = [("ID Cliente:", "id"), ("Nombre:", "nombre"),
                  ("Email:", "email"), ("Teléfono:", "tel")]
        self._entries_cli = {}

        for i, (label, key) in enumerate(campos):
            tk.Label(form, text=label, bg=C_PANEL, fg=C_TEXT,
                     font=("Arial", 10)).grid(row=0, column=i*2, padx=(0,4), sticky="w")
            e = tk.Entry(form, width=16, bg=C_BG, fg=C_TEXT,
                         insertbackground=C_WHITE, relief="flat")
            e.grid(row=0, column=i*2+1, padx=(0,12))
            self._entries_cli[key] = e

        tk.Button(form, text="Registrar Cliente", bg=C_ACCENT, fg=C_WHITE,
                  font=("Arial", 10, "bold"), bd=0, padx=12, pady=4,
                  cursor="hand2",
                  command=self._registrar_cliente_ui).grid(row=1, column=0,
                  columnspan=8, pady=(10, 0), sticky="w")

        # Tabla
        cols = ("ID", "Nombre", "Email", "Teléfono", "Reservas")
        self.tabla_cli = ttk.Treeview(self.contenido, columns=cols,
                                       show="headings", height=12)
        for c in cols:
            self.tabla_cli.heading(c, text=c)
            self.tabla_cli.column(c, width=160)
        self.tabla_cli.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        self._actualizar_tabla_clientes()

    def _registrar_cliente_ui(self):
        e = self._entries_cli
        try:
            cli = self.sistema.registrar_cliente(
                e["id"].get().strip(),
                e["nombre"].get().strip(),
                e["email"].get().strip(),
                e["tel"].get().strip()
            )
            if cli:
                messagebox.showinfo("Éxito", f"Cliente {cli.nombre} registrado correctamente.")
                for entry in e.values():
                    entry.delete(0, tk.END)
                self._actualizar_tabla_clientes()
            else:
                messagebox.showerror("Error", "Datos inválidos. Revisa el log de eventos.")
        except Exception as ex:
            messagebox.showerror("Error inesperado", str(ex))

    def _actualizar_tabla_clientes(self):
        if not hasattr(self, "tabla_cli"):
            return
        for row in self.tabla_cli.get_children():
            self.tabla_cli.delete(row)
        for c in self.sistema.listar_clientes():
            self.tabla_cli.insert("", "end", values=(
                c.id, c.nombre, c.email, c.telefono,
                len(c.reservas_activas)
            ))

    # ════════════════════════════════════════════════════════
    #  PANTALLA: SERVICIOS
    # ════════════════════════════════════════════════════════

    def _mostrar_servicios(self):
        self._limpiar_contenido()
        self._titulo(self.contenido, "Servicios Disponibles")

        cols = ("ID", "Nombre", "Tipo", "Tarifa Base", "Estado")
        tabla = ttk.Treeview(self.contenido, columns=cols,
                              show="headings", height=16)
        for c in cols:
            tabla.heading(c, text=c)
            tabla.column(c, width=170)
        tabla.pack(fill="both", expand=True, padx=24, pady=16)

        tipos = {
            "ReservaSala": "Reserva de Sala",
            "AlquilerEquipo": "Alquiler de Equipo",
            "AsesoriaEspecializada": "Asesoría Especializada"
        }
        for s in self.sistema.listar_servicios():
            tipo = tipos.get(type(s).__name__, type(s).__name__)
            estado = "Disponible" if s.disponible else "No disponible"
            tabla.insert("", "end", values=(
                s.id, s.nombre, tipo,
                f"${s.tarifa_base:,.0f}/hr", estado
            ))

    # ════════════════════════════════════════════════════════
    #  PANTALLA: RESERVAS
    # ════════════════════════════════════════════════════════

    def _mostrar_reservas(self):
        self._limpiar_contenido()
        self._titulo(self.contenido, "Reservas del Sistema")

        cols = ("ID", "Cliente", "Servicio", "Horas", "Descuento", "Estado", "Costo")
        self.tabla_res = ttk.Treeview(self.contenido, columns=cols,
                                       show="headings", height=14)
        for c in cols:
            self.tabla_res.heading(c, text=c)
            self.tabla_res.column(c, width=120)
        self.tabla_res.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        btns = tk.Frame(self.contenido, bg=C_BG)
        btns.pack(padx=24, pady=(0, 16), anchor="w")

        tk.Button(btns, text="Confirmar seleccionada", bg=C_SUCCESS,
                  fg=C_WHITE, bd=0, padx=10, pady=6, cursor="hand2",
                  command=self._confirmar_sel).pack(side="left", padx=(0, 10))
        tk.Button(btns, text="Cancelar seleccionada", bg=C_ERROR,
                  fg=C_WHITE, bd=0, padx=10, pady=6, cursor="hand2",
                  command=self._cancelar_sel).pack(side="left")

        self._actualizar_tabla_reservas()

    def _actualizar_tabla_reservas(self):
        if not hasattr(self, "tabla_res"):
            return
        for row in self.tabla_res.get_children():
            self.tabla_res.delete(row)
        for r in self.sistema.listar_reservas():
            costo = f"${r.costo_final:,.0f}" if r.costo_final else "-"
            self.tabla_res.insert("", "end", iid=r.id, values=(
                r.id, r.cliente.nombre, r.servicio.nombre,
                r.horas, f"{r.descuento}%", r.estado.upper(), costo
            ))

    def _confirmar_sel(self):
        sel = self.tabla_res.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una reserva.")
            return
        msg = self.sistema.confirmar_reserva(sel[0])
        messagebox.showinfo("Resultado", msg)
        self._actualizar_tabla_reservas()

    def _cancelar_sel(self):
        sel = self.tabla_res.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una reserva.")
            return
        msg = self.sistema.cancelar_reserva(sel[0], "Cancelación manual por usuario")
        messagebox.showinfo("Resultado", msg)
        self._actualizar_tabla_reservas()

    # ════════════════════════════════════════════════════════
    #  PANTALLA: NUEVA RESERVA
    # ════════════════════════════════════════════════════════

    def _mostrar_nueva_reserva(self):
        self._limpiar_contenido()
        self._titulo(self.contenido, "Crear Nueva Reserva")

        form = tk.Frame(self.contenido, bg=C_PANEL, padx=20, pady=16)
        form.pack(fill="x", padx=24, pady=(0, 16))

        clientes = [f"{c.id} – {c.nombre}" for c in self.sistema.listar_clientes()]
        servicios = [f"{s.id} – {s.nombre}" for s in self.sistema.listar_servicios()]

        tk.Label(form, text="Cliente:", bg=C_PANEL, fg=C_TEXT).grid(
            row=0, column=0, sticky="w", pady=6)
        self.cb_cli = ttk.Combobox(form, values=clientes, width=30, state="readonly")
        self.cb_cli.grid(row=0, column=1, padx=10, pady=6, sticky="w")

        tk.Label(form, text="Servicio:", bg=C_PANEL, fg=C_TEXT).grid(
            row=1, column=0, sticky="w", pady=6)
        self.cb_srv = ttk.Combobox(form, values=servicios, width=30, state="readonly")
        self.cb_srv.grid(row=1, column=1, padx=10, pady=6, sticky="w")

        tk.Label(form, text="Horas:", bg=C_PANEL, fg=C_TEXT).grid(
            row=2, column=0, sticky="w", pady=6)
        self.entry_horas = tk.Entry(form, width=10, bg=C_BG, fg=C_TEXT,
                                     insertbackground=C_WHITE, relief="flat")
        self.entry_horas.grid(row=2, column=1, padx=10, pady=6, sticky="w")

        tk.Label(form, text="Descuento (%):", bg=C_PANEL, fg=C_TEXT).grid(
            row=3, column=0, sticky="w", pady=6)
        self.entry_desc = tk.Entry(form, width=10, bg=C_BG, fg=C_TEXT,
                                    insertbackground=C_WHITE, relief="flat")
        self.entry_desc.insert(0, "0")
        self.entry_desc.grid(row=3, column=1, padx=10, pady=6, sticky="w")

        tk.Button(form, text="Crear Reserva", bg=C_ACCENT, fg=C_WHITE,
                  font=("Arial", 11, "bold"), bd=0, padx=16, pady=8,
                  cursor="hand2",
                  command=self._crear_reserva_ui).grid(
                  row=4, column=0, columnspan=2, pady=(14, 0), sticky="w")

    def _crear_reserva_ui(self):
        try:
            cli_sel = self.cb_cli.get()
            srv_sel = self.cb_srv.get()
            if not cli_sel or not srv_sel:
                messagebox.showwarning("Aviso", "Selecciona cliente y servicio.")
                return

            id_cli = cli_sel.split(" – ")[0]
            id_srv = srv_sel.split(" – ")[0]
            horas = float(self.entry_horas.get())
            descuento = float(self.entry_desc.get())

            reserva = self.sistema.crear_reserva(id_cli, id_srv, horas, descuento)
            if reserva:
                res = self.sistema.confirmar_reserva(reserva.id)
                messagebox.showinfo("Reserva Creada", res)
                self._actualizar_tabla_clientes()
                self._actualizar_tabla_reservas()
            else:
                messagebox.showerror("Error", "No se pudo crear la reserva. Revisa el log.")
        except ValueError:
            messagebox.showerror("Error", "Horas y descuento deben ser números.")
        except Exception as ex:
            messagebox.showerror("Error inesperado", str(ex))

    # ════════════════════════════════════════════════════════
    #  PANTALLA: LOG DE EVENTOS
    # ════════════════════════════════════════════════════════

    def _mostrar_log(self):
        self._limpiar_contenido()
        self._titulo(self.contenido, "Log de Eventos del Sistema")

        txt = scrolledtext.ScrolledText(self.contenido, bg=C_TEXT, fg=C_BG,
                                         font=("Courier", 9), state="normal",
                                         wrap="word")
        txt.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        try:
            with open("logs/eventos.log", "r", encoding="utf-8") as f:
                contenido = f.read()
            txt.insert("1.0", contenido if contenido else "(Log vacío aún)")
        except FileNotFoundError:
            txt.insert("1.0", "(Archivo de log no encontrado aún)")

        txt.config(state="disabled")
        txt.see("end")

        tk.Button(self.contenido, text="Actualizar Log", bg=C_ACCENT2,
                  fg=C_WHITE, bd=0, padx=12, pady=6, cursor="hand2",
                  command=self._mostrar_log).pack(anchor="w", padx=24, pady=(0, 16))


# ── Punto de entrada ────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = AppSoftwareFJ(root)
    root.mainloop()
