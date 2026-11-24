from ejemplos_automatas import obtener_ejemplos
from motor_automatas import (
    construir_tabla_afn_epsilon,
    determinar_afn_a_afd,
    eliminar_epsilon_transiciones,
    evaluar_cadena_afd,
    formatear_tabla_texto,
    mostrar_estado_afd,
    validar_definicion_automata,
)
from visualizador_afd import dibujar_afd

simbolo_vacio = "e"


def capturar_manual():
    estados = []
    alfabeto = []
    estado_finales = set()
    transiciones = {}

    while True:
        print("Ingrese el numero de estados del automata (2 a 10): ")
        entrada = input().strip()
        if not entrada.isdigit():
            print("Ingresa un numero entero valido")
            continue
        numero_estados = int(entrada)
        if numero_estados < 2 or numero_estados > 10:
            print("El numero de estados debe ser entre 2 y 10")
            continue
        break

    for i in range(numero_estados):
        estados.append(f"q{i}")
    print("Estados generados:", estados)

    while True:
        print("Ingrese el numero de simbolos del alfabeto (1 a 4): ")
        entrada = input().strip()
        if not entrada.isdigit():
            print("Ingresa un numero entero valido")
            continue
        numero_simbolos = int(entrada)
        if numero_simbolos < 1 or numero_simbolos > 4:
            print("El numero de simbolos debe ser entre 1 y 4")
            continue
        break

    for i in range(numero_simbolos):
        while True:
            print(f"Ingrese el simbolo {i + 1} (distinto de '{simbolo_vacio}'): ")
            simbolo = input().strip()
            if not simbolo or simbolo == simbolo_vacio or simbolo in alfabeto:
                print("Simbolo invalido, reservado o repetido.")
                continue
            alfabeto.append(simbolo)
            break

    while True:
        print("Ingrese el estado inicial. Estados:", estados)
        estado_inicial = input().strip()
        if estado_inicial in estados:
            break
        print("Estado inicial no valido.")

    while True:
        print("Ingrese el numero de estados finales: ")
        entrada = input().strip()
        if entrada.isdigit() and 1 <= int(entrada) <= numero_estados:
            numero_finales = int(entrada)
            break
        print(f"Ingresa un numero entre 1 y {numero_estados}")

    for i in range(numero_finales):
        while True:
            print(f"Ingrese el estado final {i + 1}. Estados:", estados)
            ef = input().strip()
            if ef in estados and ef not in estado_finales:
                estado_finales.add(ef)
                break
            print("Estado final invalido o repetido.")

    simbolos_totales = alfabeto + [simbolo_vacio]
    disponibles = ", ".join(estados)

    print("\nRegistro de transiciones del AFN-e")
    for estado in estados:
        for simbolo in simbolos_totales:
            while True:
                print(f"Desde '{estado}' con '{simbolo}', cuantos destinos? (0 a {len(estados)}): ")
                cant_txt = input().strip()
                if cant_txt.isdigit() and 0 <= int(cant_txt) <= len(estados):
                    cantidad = int(cant_txt)
                    break
                print(f"Ingresa un numero entre 0 y {len(estados)}")

            destinos = set()
            for i in range(cantidad):
                while True:
                    print(f"Destino {i + 1} desde '{estado}' con '{simbolo}' ({disponibles}): ")
                    dest = input().strip()
                    if dest in estados:
                        destinos.add(dest)
                        break
                    print(f"Estado no valido. Elige de: {disponibles}")
            transiciones[(estado, simbolo)] = destinos

    return estados, alfabeto, estado_inicial, estado_finales, transiciones, []


def ejecutar_cli():
    ejemplos = obtener_ejemplos()
    print("=== CONVERSION AFN-e -> AFD (MODO CONSOLA) ===")
    print("0) Capturar automata manualmente")
    for clave, info in ejemplos.items():
        print(f"{clave}) Ejemplo rapido: {info['nombre']}")

    while True:
        opcion = input("Elige una opcion: ").strip()
        if opcion == "0":
            estados, alfabeto, estado_inicial, estado_finales, transiciones, sugeridas = capturar_manual()
            break
        if opcion.isdigit() and int(opcion) in ejemplos:
            ej = ejemplos[int(opcion)]
            estados = list(ej["estados"])
            alfabeto = list(ej["alfabeto"])
            estado_inicial = ej["estado_inicial"]
            estado_finales = set(ej["estado_finales"])
            transiciones = {k: set(v) for k, v in ej["transiciones"].items()}
            sugeridas = list(ej["cadenas_sugeridas"])
            break
        print("Opcion no valida.")

    validar_definicion_automata(estados, alfabeto, estado_inicial, estado_finales, simbolo_vacio)

    enc_1, filas_1 = construir_tabla_afn_epsilon(estados, alfabeto, transiciones, estado_inicial, estado_finales, simbolo_vacio)
    print("\n1. Tabla de transiciones del AFN-e:")
    print(formatear_tabla_texto(filas_1, enc_1))

    res_afn = eliminar_epsilon_transiciones(estados, alfabeto, transiciones, estado_inicial, estado_finales, simbolo_vacio)
    print("\n2. e-clausuras:")
    for q in estados:
        print(f"- e_clausura({q}) = {mostrar_estado_afd(res_afn['clausuras'][q])}")

    print("\n3. AFN sin transiciones vacias:")
    print("Estado inicial: ->", res_afn["estado_inicial_afn"])
    print("Estados finales:", ", ".join(sorted(res_afn["finales_afn"])) if res_afn["finales_afn"] else "ninguno")
    print(formatear_tabla_texto(res_afn["filas"], res_afn["encabezados"]))

    res_afd = determinar_afn_a_afd(alfabeto, transiciones, estado_inicial, estado_finales, simbolo_vacio)
    print("\n4. AFD determinista:")
    print("Estado inicial del AFD: ->", mostrar_estado_afd(res_afd["estado_inicial_afd"]))
    finales_str = [mostrar_estado_afd(f) for f in res_afd["estados_finales_afd"]]
    print("Estados finales del AFD:", ", ".join(finales_str) if finales_str else "ninguno")
    print(formatear_tabla_texto(res_afd["filas"], res_afd["encabezados"]))

    if sugeridas:
        print("\nCadenas sugeridas para este ejemplo:", ", ".join(sugeridas))

    print("\n=== VALIDACION DE CADENAS ===")
    while True:
        entrada = input("Cadena a validar ('e' o vacio para cadena vacia, 'salir' para terminar): ").strip()
        if entrada.lower() == "salir":
            break
        cadena = "" if entrada in ("", simbolo_vacio) else entrada
        etiqueta = "ε (cadena vacia)" if cadena == "" else cadena
        aceptada, recorrido, obs = evaluar_cadena_afd(
            cadena,
            res_afd["estado_inicial_afd"],
            res_afd["estados_finales_afd"],
            res_afd["transiciones_afd"],
            alfabeto,
        )
        print(f"Cadena: {etiqueta} | Recorrido: {' -> '.join(recorrido)}")
        if obs:
            print("Observacion:", obs)
        print("Resultado:", "ACEPTADA" if aceptada else "RECHAZADA")

    if input("\nGenerar diagrama grafico del AFD? (s/n): ").strip().lower() == "s":
        dibujar_afd(
            estados_afd=res_afd["estados_afd"],
            alfabeto=alfabeto,
            transiciones_afd=res_afd["transiciones_afd"],
            estado_inicial_afd=res_afd["estado_inicial_afd"],
            estados_finales_afd=res_afd["estados_finales_afd"],
            nombre_archivo="afd_diagrama.png",
            mostrar_ventana=True,
        )


if __name__ == "__main__":
    ejecutar_cli()