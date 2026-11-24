import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from ejemplos_automatas import obtener_ejemplos
from motor_automatas import (
    construir_tabla_afn_epsilon,
    determinar_afn_a_afd,
    eliminar_epsilon_transiciones,
    evaluar_cadena_afd,
    generar_sugerencias_cadenas,
    mostrar_estado_afd,
    validar_definicion_automata,
)
from visualizador_afd import renderizar_figura_afd


class AplicacionAFD(tk.Tk):
    PRIMARY = "#1565C0"
    PRIMARY_DARK = "#0D47A1"
    ACCENT = "#00C853"
    BG = "#ECEFF1"
    SURFACE = "#FFFFFF"
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#607D8B"
    DIVIDER = "#CFD8DC"

    def __init__(self):
        super().__init__()
        self.title("AFN-ε → AFD (Proyecto A + GUI)")
        self.geometry("1220x800")
        self.minsize(1020, 700)
        self.configure(bg=self.BG)

        self.simbolo_vacio = "e"
        self.ejemplos = obtener_ejemplos()
        self.datos_afd = None
        self.alfabeto_actual = []
        self.canvas_diagrama = None
        self.toolbar_diagrama = None

        self._configurar_estilos()
        self._construir_interfaz()
        self._cargar_ejemplo(1)

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=self.BG)
        style.configure("TLabel", background=self.BG, foreground=self.TEXT_PRIMARY)
        style.configure("TEntry", font=("Segoe UI", 10), padding=6)
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            background="#CFD8DC",
            foreground=self.TEXT_SECONDARY,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.SURFACE)],
            foreground=[("selected", self.PRIMARY)],
        )
        style.configure("Tabla.Treeview", font=("Segoe UI", 10), rowheight=26, background="white")
        style.configure(
            "Tabla.Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=self.PRIMARY,
            foreground="white",
        )

    def _tarjeta(self, parent):
        borde = tk.Frame(parent, bg=self.DIVIDER, padx=1, pady=1)
        contenido = tk.Frame(borde, bg=self.SURFACE)
        contenido.pack(fill="both", expand=True)
        return borde, contenido

    def _construir_interfaz(self):
        barra = tk.Frame(self, bg=self.PRIMARY, height=54)
        barra.pack(fill="x")
        barra.pack_propagate(False)
        tk.Label(
            barra,
            text="  AFN-ε → AFD",
            bg=self.PRIMARY,
            fg="white",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left", padx=12)
        tk.Label(
            barra,
            text="Lenguajes Formales y Autómatas",
            bg=self.PRIMARY,
            fg="#BBDEFB",
            font=("Segoe UI", 10),
        ).pack(side="left")

        cuerpo = tk.Frame(self, bg=self.BG)
        cuerpo.pack(fill="both", expand=True, padx=12, pady=10)

        # Panel izquierdo: ejemplos y captura
        izq = tk.Frame(cuerpo, bg=self.BG, width=340)
        izq.pack(side="left", fill="y", padx=(0, 10))
        izq.pack_propagate(False)

        b1, c1 = self._tarjeta(izq)
        b1.pack(fill="x", pady=(0, 8))
        tk.Label(c1, text="EJEMPLOS RÁPIDOS", bg=self.SURFACE, fg=self.PRIMARY, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=10, pady=(8, 4)
        )
        for num, info in self.ejemplos.items():
            tk.Button(
                c1,
                text=f"Ejemplo {num}: {info['nombre']}",
                bg="#E3F2FD",
                fg=self.PRIMARY_DARK,
                relief="flat",
                cursor="hand2",
                anchor="w",
                padx=10,
                pady=6,
                command=lambda n=num: self._cargar_ejemplo(n),
            ).pack(fill="x", padx=8, pady=2)
        tk.Frame(c1, bg=self.SURFACE, height=6).pack()

        b2, c2 = self._tarjeta(izq)
        b2.pack(fill="x", pady=(0, 8))
        tk.Label(c2, text="DEFINICIÓN DEL AUTÓMATA", bg=self.SURFACE, fg=self.PRIMARY, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=10, pady=(8, 4)
        )

        def crear_campo(etiqueta):
            tk.Label(c2, text=etiqueta, bg=self.SURFACE, fg=self.TEXT_SECONDARY, font=("Segoe UI", 8)).pack(
                anchor="w", padx=12
            )
            entrada = ttk.Entry(c2)
            entrada.pack(fill="x", padx=10, pady=(1, 5))
            return entrada

        self.e_estados = crear_campo("Estados (2 a 10, separados por espacio)")
        self.e_alfabeto = crear_campo("Alfabeto (1 a 4 símbolos, sin 'e')")
        self.e_inicial = crear_campo("Estado inicial (único)")
        self.e_finales = crear_campo("Estados finales (uno o más)")
        tk.Frame(c2, bg=self.SURFACE, height=4).pack()

        b3, c3 = self._tarjeta(izq)
        b3.pack(fill="x", pady=(0, 8))
        tk.Label(c3, text="TRANSICIONES (origen simbolo dest1,dest2)", bg=self.SURFACE, fg=self.PRIMARY, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=10, pady=(8, 2)
        )
        self.txt_trans = scrolledtext.ScrolledText(c3, height=6, font=("Consolas", 9), bg="#F8FAFC", relief="flat")
        self.txt_trans.pack(fill="x", padx=8, pady=(4, 8))

        botones = tk.Frame(izq, bg=self.BG)
        botones.pack(fill="x")
        tk.Button(
            botones,
            text="▶ CONVERTIR",
            bg=self.PRIMARY,
            fg="white",
            activebackground=self.PRIMARY_DARK,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            pady=8,
            command=self._convertir,
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(
            botones,
            text="Limpiar",
            bg="#CFD8DC",
            fg=self.TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=8,
            command=self._limpiar,
        ).pack(side="left")

        # Panel derecho: pestañas
        der = tk.Frame(cuerpo, bg=self.BG)
        der.pack(side="left", fill="both", expand=True)

        self.notebook = ttk.Notebook(der)
        self.notebook.pack(fill="both", expand=True)

        self.pestana_tablas = tk.Frame(self.notebook, bg=self.SURFACE)
        self.notebook.add(self.pestana_tablas, text="  Tablas y ε-clausuras  ")

        self.pestana_cadenas = tk.Frame(self.notebook, bg=self.SURFACE)
        self.notebook.add(self.pestana_cadenas, text="  Validar cadenas  ")

        self.pestana_diagrama = tk.Frame(self.notebook, bg=self.SURFACE)
        self.notebook.add(self.pestana_diagrama, text="  Diagrama AFD  ")

        self._armar_pestana_cadenas()

        self.estado_barra = tk.Label(
            self,
            text="  Listo",
            bg=self.PRIMARY_DARK,
            fg="#BBDEFB",
            font=("Segoe UI", 9),
            anchor="w",
            padx=10,
            pady=5,
        )
        self.estado_barra.pack(fill="x", side="bottom")

    def _armar_pestana_cadenas(self):
        barra_sup = tk.Frame(self.pestana_cadenas, bg=self.SURFACE)
        barra_sup.pack(fill="x", padx=14, pady=12)

        tk.Label(barra_sup, text="Cadena ('e' o vacío para ε):", bg=self.SURFACE, font=("Segoe UI", 9)).pack(side="left")
        self.e_cadena = ttk.Entry(barra_sup, width=24)
        self.e_cadena.pack(side="left", padx=8)

        tk.Button(
            barra_sup,
            text="PROBAR CADENA",
            bg=self.ACCENT,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self._probar_cadena,
        ).pack(side="left")

        self.lbl_sugeridas = tk.Label(self.pestana_cadenas, text="", bg=self.SURFACE, fg=self.TEXT_SECONDARY, font=("Segoe UI", 9))
        self.lbl_sugeridas.pack(anchor="w", padx=14, pady=(0, 6))

        self.txt_cadenas = scrolledtext.ScrolledText(self.pestana_cadenas, font=("Consolas", 10), bg="#F8FAFC", relief="flat")
        self.txt_cadenas.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _cargar_ejemplo(self, numero):
        ej = self.ejemplos[numero]
        self.e_estados.delete(0, "end")
        self.e_estados.insert(0, " ".join(ej["estados"]))

        self.e_alfabeto.delete(0, "end")
        self.e_alfabeto.insert(0, " ".join(ej["alfabeto"]))

        self.e_inicial.delete(0, "end")
        self.e_inicial.insert(0, ej["estado_inicial"])

        self.e_finales.delete(0, "end")
        self.e_finales.insert(0, " ".join(sorted(ej["estado_finales"])))

        lineas = []
        for (origen, sim), dests in ej["transiciones"].items():
            if dests:
                lineas.append(f"{origen} {sim} {','.join(sorted(dests))}")
        self.txt_trans.delete("1.0", "end")
        self.txt_trans.insert("1.0", "\n".join(lineas))

        sugeridas = ej.get("cadenas_sugeridas", [])
        self.lbl_sugeridas.config(text=f"Cadenas sugeridas: {', '.join(sugeridas)}" if sugeridas else "")
        self.estado_barra.config(text=f"  Ejemplo {numero} cargado: {ej['nombre']}")

    def _limpiar(self):
        for campo in (self.e_estados, self.e_alfabeto, self.e_inicial, self.e_finales, self.e_cadena):
            campo.delete(0, "end")
        self.txt_trans.delete("1.0", "end")
        self.txt_cadenas.delete("1.0", "end")
        for w in self.pestana_tablas.winfo_children():
            w.destroy()
        for w in self.pestana_diagrama.winfo_children():
            w.destroy()
        self.datos_afd = None
        self.estado_barra.config(text="  Campos limpiados")

    def _leer_formulario(self):
        estados = self.e_estados.get().strip().split()
        alfabeto = self.e_alfabeto.get().strip().split()
        estado_inicial = self.e_inicial.get().strip()
        estado_finales = set(self.e_finales.get().strip().split())

        validar_definicion_automata(estados, alfabeto, estado_inicial, estado_finales, self.simbolo_vacio)

        transiciones = {(q, s): set() for q in estados for s in alfabeto + [self.simbolo_vacio]}
        for linea in self.txt_trans.get("1.0", "end").strip().splitlines():
            partes = linea.strip().split()
            if not partes:
                continue
            if len(partes) < 2:
                raise ValueError(f"Linea invalida en transiciones: '{linea}'")
            origen, simbolo = partes[0], partes[1]
            if origen not in estados:
                raise ValueError(f"Estado origen '{origen}' no existe.")
            if simbolo not in alfabeto + [self.simbolo_vacio]:
                raise ValueError(f"Simbolo '{simbolo}' no pertenece al alfabeto ni a '{self.simbolo_vacio}'.")
            destinos = partes[2].split(",") if len(partes) > 2 else []
            for d in destinos:
                d = d.strip()
                if not d:
                    continue
                if d not in estados:
                    raise ValueError(f"Estado destino '{d}' no existe.")
                transiciones[(origen, simbolo)].add(d)

        return estados, alfabeto, estado_inicial, estado_finales, transiciones

    def _agregar_treeview(self, parent, titulo, encabezados, filas):
        tk.Label(parent, text=titulo, bg=self.SURFACE, fg=self.PRIMARY, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=12, pady=(10, 4)
        )
        tabla = ttk.Treeview(parent, columns=encabezados, show="headings", height=max(3, min(len(filas), 7)), style="Tabla.Treeview")
        for col in encabezados:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center", width=110)
        for fila in filas:
            tabla.insert("", "end", values=fila)
        tabla.pack(fill="x", padx=12, pady=(0, 8))

    def _convertir(self):
        try:
            estados, alfabeto, inicial, finales, transiciones = self._leer_formulario()
        except ValueError as err:
            messagebox.showerror("Error en los datos", str(err))
            return

        for w in self.pestana_tablas.winfo_children():
            w.destroy()

        enc1, filas1 = construir_tabla_afn_epsilon(estados, alfabeto, transiciones, inicial, finales, self.simbolo_vacio)
        self._agregar_treeview(self.pestana_tablas, "1. AFN-ε Original", enc1, filas1)

        res_afn = eliminar_epsilon_transiciones(estados, alfabeto, transiciones, inicial, finales, self.simbolo_vacio)
        texto_clausuras = "\n".join(
            f"ε-clausura({q}) = {mostrar_estado_afd(res_afn['clausuras'][q])}" for q in estados
        )
        tk.Label(self.pestana_tablas, text="2. ε-Clausuras", bg=self.SURFACE, fg=self.PRIMARY, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=12, pady=(8, 2)
        )
        txt_c = tk.Text(self.pestana_tablas, height=min(len(estados) + 1, 7), font=("Consolas", 9), bg="#F8FAFC", relief="flat")
        txt_c.insert("1.0", texto_clausuras)
        txt_c.config(state="disabled")
        txt_c.pack(fill="x", padx=12, pady=(0, 8))

        self._agregar_treeview(
            self.pestana_tablas,
            f"3. AFN sin '{self.simbolo_vacio}' (Finales: {', '.join(sorted(res_afn['finales_afn'])) or 'ninguno'})",
            res_afn["encabezados"],
            res_afn["filas"],
        )

        res_afd = determinar_afn_a_afd(alfabeto, transiciones, inicial, finales, self.simbolo_vacio)
        finales_afd_txt = ", ".join(mostrar_estado_afd(f) for f in res_afd["estados_finales_afd"]) or "ninguno"
        self._agregar_treeview(
            self.pestana_tablas,
            f"4. AFD Determinista (Inicial: {mostrar_estado_afd(res_afd['estado_inicial_afd'])} | Finales: {finales_afd_txt})",
            res_afd["encabezados"],
            res_afd["filas"],
        )

        sugeridas_dinamicas = generar_sugerencias_cadenas(
            alfabeto=alfabeto,
            estados_afd=res_afd["estados_afd"],
            transiciones_afd=res_afd["transiciones_afd"],
            estado_inicial_afd=res_afd["estado_inicial_afd"],
            estados_finales_afd=res_afd["estados_finales_afd"],
            simbolo_vacio=self.simbolo_vacio,
        )
        if sugeridas_dinamicas:
            self.lbl_sugeridas.config(
                text=f"Cadenas sugeridas (auto): {', '.join(sugeridas_dinamicas)}"
            )
        else:
            self.lbl_sugeridas.config(
                text="Cadenas sugeridas: (no se pudieron generar automáticamente)"
            )

        self.datos_afd = res_afd
        self.alfabeto_actual = alfabeto
        self._actualizar_diagrama(res_afd, alfabeto)
        self.notebook.select(0)
        self.estado_barra.config(text="  Conversión completada · Tablas y diagrama listos")

    def _actualizar_diagrama(self, res_afd, alfabeto):
        for w in self.pestana_diagrama.winfo_children():
            w.destroy()

        figura = renderizar_figura_afd(
            estados_afd=res_afd["estados_afd"],
            alfabeto=alfabeto,
            transiciones_afd=res_afd["transiciones_afd"],
            estado_inicial_afd=res_afd["estado_inicial_afd"],
            estados_finales_afd=res_afd["estados_finales_afd"],
            nombre_archivo="afd_diagrama.png",
            guardar_imagen=True,
            figsize=(8.2, 5.6),
        )

        canvas = FigureCanvasTkAgg(figura, master=self.pestana_diagrama)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self.pestana_diagrama)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _probar_cadena(self):
        if not self.datos_afd:
            messagebox.showinfo("Aviso", "Primero presiona CONVERTIR.")
            return

        raw = self.e_cadena.get().strip()
        cadena = "" if raw in ("", self.simbolo_vacio) else raw
        etiqueta = "ε (cadena vacía)" if cadena == "" else cadena

        aceptada, recorrido, obs = evaluar_cadena_afd(
            cadena,
            self.datos_afd["estado_inicial_afd"],
            self.datos_afd["estados_finales_afd"],
            self.datos_afd["transiciones_afd"],
            self.alfabeto_actual,
        )

        resultado = "ACEPTADA" if aceptada else "RECHAZADA"
        detalle = f"Cadena: {etiqueta}\nRecorrido: {' -> '.join(recorrido)}\n"
        if obs:
            detalle += f"Observación: {obs}\n"
        detalle += f"Resultado: {resultado}\n{'-' * 40}\n"

        self.txt_cadenas.insert("end", detalle)
        self.txt_cadenas.see("end")
        self.notebook.select(1)


if __name__ == "__main__":
    app = AplicacionAFD()
    app.mainloop()