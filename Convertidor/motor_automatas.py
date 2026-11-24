from tabulate import tabulate


def mostrar_estado_afd(estado_tupla):
    if not estado_tupla:
        return "∅"
    return "{" + ",".join(sorted(list(estado_tupla))) + "}"


def validar_definicion_automata(estados, alfabeto, estado_inicial, estado_finales, simbolo_vacio="e"):
    if not (2 <= len(estados) <= 10):
        raise ValueError("El numero de estados debe ser entre 2 y 10.")
    if len(set(estados)) != len(estados):
        raise ValueError("Los estados no deben repetirse.")
    if not (1 <= len(alfabeto) <= 4):
        raise ValueError("El alfabeto debe tener entre 1 y 4 simbolos.")
    if len(set(alfabeto)) != len(alfabeto):
        raise ValueError("Los simbolos del alfabeto no deben repetirse.")
    if simbolo_vacio in alfabeto or any(s.strip() == "" for s in alfabeto):
        raise ValueError(f"El alfabeto no puede contener vacios ni el simbolo reservado '{simbolo_vacio}'.")
    if estado_inicial not in estados:
        raise ValueError("El estado inicial debe pertenecer al conjunto de estados.")
    if not estado_finales or any(f not in estados for f in estado_finales):
        raise ValueError("Debe existir al menos un estado final valido dentro de los estados.")


def epsilon_clausura(estado_base, transiciones, simbolo_vacio="e"):
    clausura = set(estado_base)
    por_revisar = list(estado_base)

    while por_revisar:
        actual = por_revisar.pop(0)
        salidas_e = transiciones.get((actual, simbolo_vacio), set())
        for siguiente in salidas_e:
            if siguiente not in clausura:
                clausura.add(siguiente)
                por_revisar.append(siguiente)

    return clausura


def construir_tabla_afn_epsilon(estados, alfabeto, transiciones, estado_inicial, estado_finales, simbolo_vacio="e"):
    encabezados = ["Estado"] + list(alfabeto) + [simbolo_vacio]
    filas = []

    for estado in estados:
        marcas = ""
        if estado == estado_inicial:
            marcas += "->"
        if estado in estado_finales:
            marcas += "*"

        fila = [f"{marcas}{estado}"]
        for simbolo in list(alfabeto) + [simbolo_vacio]:
            destinos = transiciones.get((estado, simbolo), set())
            fila.append(mostrar_estado_afd(destinos))
        filas.append(fila)

    return encabezados, filas


def eliminar_epsilon_transiciones(estados, alfabeto, transiciones, estado_inicial, estado_finales, simbolo_vacio="e"):
    clausuras = {}
    for estado in estados:
        clausuras[estado] = epsilon_clausura([estado], transiciones, simbolo_vacio)

    transiciones_afn = {}
    for estado in estados:
        base_e = clausuras[estado]
        for simbolo in alfabeto:
            alcanzables = set()
            for q in base_e:
                alcanzables |= transiciones.get((q, simbolo), set())
            transiciones_afn[(estado, simbolo)] = epsilon_clausura(alcanzables, transiciones, simbolo_vacio)

    finales_afn = set()
    for estado in estados:
        if clausuras[estado] & set(estado_finales):
            finales_afn.add(estado)

    encabezados = ["Estado"] + list(alfabeto)
    filas = []
    for estado in estados:
        marcas = ""
        if estado == estado_inicial:
            marcas += "->"
        if estado in finales_afn:
            marcas += "*"

        fila = [f"{marcas}{estado}"]
        for simbolo in alfabeto:
            destinos = transiciones_afn.get((estado, simbolo), set())
            fila.append(mostrar_estado_afd(destinos))
        filas.append(fila)

    return {
        "clausuras": clausuras,
        "transiciones_afn": transiciones_afn,
        "estado_inicial_afn": estado_inicial,
        "finales_afn": finales_afn,
        "encabezados": encabezados,
        "filas": filas,
    }


def determinar_afn_a_afd(alfabeto, transiciones, estado_inicial, estado_finales, simbolo_vacio="e"):
    estado_inicial_afd = tuple(sorted(epsilon_clausura([estado_inicial], transiciones, simbolo_vacio)))
    estados_afd = [estado_inicial_afd]
    transiciones_afd = {}
    hay_vacio = False

    indice = 0
    while indice < len(estados_afd):
        estado_actual_afd = estados_afd[indice]

        for simbolo in alfabeto:
            if len(estado_actual_afd) == 0:
                transiciones_afd[(estado_actual_afd, simbolo)] = ()
                continue

            destinos_mover = set()
            for q in estado_actual_afd:
                destinos_mover |= transiciones.get((q, simbolo), set())

            estado_siguiente_afd = tuple(sorted(epsilon_clausura(destinos_mover, transiciones, simbolo_vacio)))
            transiciones_afd[(estado_actual_afd, simbolo)] = estado_siguiente_afd

            if len(estado_siguiente_afd) == 0:
                hay_vacio = True
            elif estado_siguiente_afd not in estados_afd:
                estados_afd.append(estado_siguiente_afd)

        indice += 1

    if hay_vacio and () not in estados_afd:
        estados_afd.append(())

    estados_finales_afd = []
    conjunto_finales = set(estado_finales)
    for estado_afd in estados_afd:
        if len(estado_afd) == 0:
            continue
        if any(q in conjunto_finales for q in estado_afd):
            estados_finales_afd.append(estado_afd)

    encabezados = ["Estado AFD"] + list(alfabeto)
    filas = []
    for estado_afd in estados_afd:
        nombre = mostrar_estado_afd(estado_afd)
        marcas = ""
        if estado_afd == estado_inicial_afd:
            marcas += "->"
        if estado_afd in estados_finales_afd:
            marcas += "*"

        fila = [f"{marcas}{nombre}"]
        for simbolo in alfabeto:
            siguiente = transiciones_afd.get((estado_afd, simbolo), ())
            fila.append(mostrar_estado_afd(siguiente))
        filas.append(fila)

    return {
        "estados_afd": estados_afd,
        "transiciones_afd": transiciones_afd,
        "estado_inicial_afd": estado_inicial_afd,
        "estados_finales_afd": estados_finales_afd,
        "encabezados": encabezados,
        "filas": filas,
    }


def evaluar_cadena_afd(cadena, estado_inicial_afd, estados_finales_afd, transiciones_afd, alfabeto):
    for simbolo in cadena:
        if simbolo not in alfabeto:
            return False, [mostrar_estado_afd(estado_inicial_afd)], f"Simbolo '{simbolo}' fuera del alfabeto {list(alfabeto)}"

    actual = estado_inicial_afd
    recorrido = [mostrar_estado_afd(actual)]

    for simbolo in cadena:
        actual = transiciones_afd.get((actual, simbolo), ())
        recorrido.append(mostrar_estado_afd(actual))

    aceptada = actual in estados_finales_afd
    return aceptada, recorrido, None


def formatear_tabla_texto(filas, encabezados):
    return tabulate(filas, headers=encabezados, tablefmt="grid")