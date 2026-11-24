def obtener_ejemplos():
    """
    Devuelve ejemplos listos para probar sin capturar todo a mano.
    Cada ejemplo cumple con los limites de 2-10 estados y 1-4 simbolos.
    """
    return {
        1: {
            "nombre": "Termina en 'b' (con transicion e)",
            "estados": ["q0", "q1", "q2"],
            "alfabeto": ["a", "b"],
            "estado_inicial": "q0",
            "estado_finales": {"q2"},
            "transiciones": {
                ("q0", "a"): {"q0"},
                ("q0", "b"): {"q0"},
                ("q0", "e"): {"q1"},
                ("q1", "a"): set(),
                ("q1", "b"): {"q2"},
                ("q1", "e"): set(),
                ("q2", "a"): set(),
                ("q2", "b"): set(),
                ("q2", "e"): set(),
            },
            "cadenas_sugeridas": ["b", "ab", "aab", "a", "ba", "e"],
        },
        2: {
            "nombre": "Cadenas ε encadenadas (q0 -> q1 -> q2)",
            "estados": ["q0", "q1", "q2", "q3"],
            "alfabeto": ["a", "b"],
            "estado_inicial": "q0",
            "estado_finales": {"q3"},
            "transiciones": {
                ("q0", "a"): set(),
                ("q0", "b"): set(),
                ("q0", "e"): {"q1"},
                ("q1", "a"): {"q2"},
                ("q1", "b"): set(),
                ("q1", "e"): {"q2"},
                ("q2", "a"): set(),
                ("q2", "b"): {"q3"},
                ("q2", "e"): set(),
                ("q3", "a"): {"q3"},
                ("q3", "b"): {"q3"},
                ("q3", "e"): set(),
            },
            "cadenas_sugeridas": ["b", "ab", "a", "bb", "e"],
        },
        3: {
            "nombre": "Alfabeto binario {0, 1} con estado muerto",
            "estados": ["q0", "q1", "q2"],
            "alfabeto": ["0", "1"],
            "estado_inicial": "q0",
            "estado_finales": {"q2"},
            "transiciones": {
                ("q0", "0"): {"q0"},
                ("q0", "1"): {"q1"},
                ("q0", "e"): set(),
                ("q1", "0"): set(),
                ("q1", "1"): {"q2"},
                ("q1", "e"): set(),
                ("q2", "0"): set(),
                ("q2", "1"): set(),
                ("q2", "e"): set(),
            },
            "cadenas_sugeridas": ["11", "011", "101", "1", "0", "e"],
        },
    }