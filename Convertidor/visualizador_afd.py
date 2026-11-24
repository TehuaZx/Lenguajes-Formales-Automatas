import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch


def _etiqueta_estado(estado_tupla):
    if not estado_tupla:
        return "∅"
    return "{" + ",".join(sorted(list(estado_tupla))) + "}"


def _calcular_posiciones(estados_afd):
    """
    Distribuye los nodos evitando encimamientos en automatas de 1 a 10 estados.
    Usa un layout en dos anillos o elipse ancha cuando hay varios estados.
    """
    n = len(estados_afd)
    posiciones = {}
    if n == 0:
        return posiciones

    if n <= 4:
        # Disposicion horizontal/eliptica suave para pocos estados
        radio_x = max(2.4, 1.35 * (n - 1))
        radio_y = 1.45 if n > 2 else 0.0
        for idx, estado in enumerate(estados_afd):
            angulo = (2 * math.pi * idx) / n + (math.pi / 4 if n == 4 else 0)
            x = radio_x * math.cos(angulo)
            y = radio_y * math.sin(angulo)
            posiciones[estado] = (x, y)
        return posiciones

    # Para 5 a 10 estados, reparte en anillo exterior e interior si supera 6
    if n <= 6:
        rx, ry = 3.6, 2.8
        for idx, estado in enumerate(estados_afd):
            angulo = (2 * math.pi * idx) / n
            posiciones[estado] = (rx * math.cos(angulo), ry * math.sin(angulo))
    else:
        exterior = estados_afd[:6]
        interior = estados_afd[6:]
        for idx, estado in enumerate(exterior):
            angulo = (2 * math.pi * idx) / 6
            posiciones[estado] = (4.2 * math.cos(angulo), 3.3 * math.sin(angulo))
        for idx, estado in enumerate(interior):
            angulo = (2 * math.pi * idx) / len(interior) + (math.pi / len(interior))
            posiciones[estado] = (1.75 * math.cos(angulo), 1.35 * math.sin(angulo))

    return posiciones


def renderizar_figura_afd(
    estados_afd,
    alfabeto,
    transiciones_afd,
    estado_inicial_afd,
    estados_finales_afd,
    nombre_archivo="afd_diagrama.png",
    guardar_imagen=True,
    figsize=(9.5, 6.8),
):
    n = len(estados_afd)
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Diagrama del Automata Finito Determinista (AFD)", fontsize=12, fontweight="bold", pad=14)

    if n == 0:
        ax.text(0, 0, "No hay estados en el AFD para dibujar.", ha="center", va="center")
        return fig

    posiciones = _calcular_posiciones(estados_afd)
    radio_nodo = 0.44 if n <= 6 else 0.38

    aristas_agrupadas = {}
    for estado in estados_afd:
        for simbolo in alfabeto:
            destino = transiciones_afd.get((estado, simbolo), ())
            if destino in posiciones:
                aristas_agrupadas.setdefault((estado, destino), []).append(simbolo)

    for idx_arista, ((origen, destino), simbolos) in enumerate(aristas_agrupadas.items()):
        etiqueta = ", ".join(simbolos)
        x1, y1 = posiciones[origen]
        x2, y2 = posiciones[destino]

        if origen == destino:
            # Orientar el bucle hacia afuera del centro (0,0) para evitar choques entre nodos
            angulo_radial = math.atan2(y1, x1) if math.hypot(x1, y1) > 1e-6 else math.pi / 2
            angulo_inicio = angulo_radial - 0.45
            angulo_fin = angulo_radial + 0.45

            sx = x1 + radio_nodo * math.cos(angulo_inicio)
            sy = y1 + radio_nodo * math.sin(angulo_inicio)
            ex = x1 + radio_nodo * math.cos(angulo_fin)
            ey = y1 + radio_nodo * math.sin(angulo_fin)

            loop = FancyArrowPatch(
                (sx, sy),
                (ex, ey),
                connectionstyle="arc3,rad=1.45",
                arrowstyle="-|>",
                mutation_scale=13,
                linewidth=1.4,
                color="#2b4c7e",
            )
            ax.add_patch(loop)

            lx = x1 + (radio_nodo + 0.85) * math.cos(angulo_radial)
            ly = y1 + (radio_nodo + 0.85) * math.sin(angulo_radial)
            ax.text(
                lx,
                ly,
                etiqueta,
                fontsize=9.5,
                fontweight="bold",
                color="#1a2c47",
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#cbd5e1", alpha=0.92),
            )
        else:
            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            ux, uy = dx / dist, dy / dist

            sx = x1 + ux * radio_nodo
            sy = y1 + uy * radio_nodo
            ex = x2 - ux * radio_nodo
            ey = y2 - uy * radio_nodo

            tiene_inversa = (destino, origen) in aristas_agrupadas
            rad = 0.24 if tiene_inversa else 0.08

            flecha = FancyArrowPatch(
                (sx, sy),
                (ex, ey),
                connectionstyle=f"arc3,rad={rad}",
                arrowstyle="-|>",
                mutation_scale=14,
                linewidth=1.4,
                color="#2b4c7e",
            )
            ax.add_patch(flecha)

            # Desplazamiento perpendicular + leve variacion segun indice para separar etiquetas
            desp = (0.38 if tiene_inversa else 0.24) + (0.08 * (idx_arista % 2))
            mx = (sx + ex) / 2 - uy * desp
            my = (sy + ey) / 2 + ux * desp
            ax.text(
                mx,
                my,
                etiqueta,
                fontsize=9.5,
                fontweight="bold",
                color="#1a2c47",
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#cbd5e1", alpha=0.92),
            )

    for estado in estados_afd:
        x, y = posiciones[estado]
        es_final = estado in estados_finales_afd
        es_inicial = estado == estado_inicial_afd
        es_vacio = len(estado) == 0

        color_relleno = "#f1f5f9" if es_vacio else "#e8f4f8"
        color_borde = "#64748b" if es_vacio else "#1d3557"

        circulo = Circle(
            (x, y),
            radio_nodo,
            facecolor=color_relleno,
            edgecolor=color_borde,
            linewidth=2.0,
            zorder=3,
        )
        ax.add_patch(circulo)

        if es_final:
            circulo_interno = Circle(
                (x, y),
                radio_nodo * 0.80,
                facecolor="none",
                edgecolor=color_borde,
                linewidth=1.8,
                zorder=4,
            )
            ax.add_patch(circulo_interno)

        if es_inicial:
            inicio_x = x - radio_nodo - 0.9
            inicio_y = y
            fin_x = x - radio_nodo
            fin_y = y
            flecha_inicio = FancyArrowPatch(
                (inicio_x, inicio_y),
                (fin_x, fin_y),
                arrowstyle="-|>",
                mutation_scale=15,
                linewidth=2.0,
                color="#c1121f",
                zorder=5,
            )
            ax.add_patch(flecha_inicio)
            ax.text(
                inicio_x - 0.08,
                inicio_y + 0.16,
                "Inicio",
                fontsize=8.5,
                fontweight="bold",
                color="#c1121f",
                ha="right",
                va="bottom",
            )

        ax.text(
            x,
            y,
            _etiqueta_estado(estado),
            fontsize=9,
            fontweight="bold",
            color="#111111",
            ha="center",
            va="center",
            zorder=6,
        )

    xs = [p[0] for p in posiciones.values()]
    ys = [p[1] for p in posiciones.values()]
    margen = radio_nodo + 1.45
    ax.set_xlim(min(xs) - margen - 0.5, max(xs) + margen)
    ax.set_ylim(min(ys) - margen, max(ys) + margen)

    plt.tight_layout()
    if guardar_imagen and nombre_archivo:
        plt.savefig(nombre_archivo, dpi=300, bbox_inches="tight")
    return fig


def dibujar_afd(
    estados_afd,
    alfabeto,
    transiciones_afd,
    estado_inicial_afd,
    estados_finales_afd,
    nombre_archivo="afd_diagrama.png",
    mostrar_ventana=True,
):
    fig = renderizar_figura_afd(
        estados_afd=estados_afd,
        alfabeto=alfabeto,
        transiciones_afd=transiciones_afd,
        estado_inicial_afd=estado_inicial_afd,
        estados_finales_afd=estados_finales_afd,
        nombre_archivo=nombre_archivo,
        guardar_imagen=True,
    )
    if nombre_archivo:
        print(f"\nDiagrama del AFD guardado en '{nombre_archivo}'.")
    if mostrar_ventana:
        plt.show()
    else:
        plt.close(fig)