def convertir_imperial(unidad, valor):
    # Factores de conversión a centímetros
    conversiones = {
        "in": 2.54,
        "ft": 30.48,
        "yd": 91.44,
        "mi": 160934,
        "nm": 185200
    }

    if unidad not in conversiones:
        return "Error: unidad no válida"

    # Convertir a centímetros
    cm = valor * conversiones[unidad]

    # Convertir a metros y kilómetros
    m = cm / 100
    km = cm / 100000

    return cm, m, km


# Ejemplo de uso
unidad = input("Ingrese la unidad (in, ft, yd, mi, nm): ").lower()
valor = float(input("Ingrese el valor a convertir: "))

resultado = convertir_imperial(unidad, valor)

if isinstance(resultado, str):
    print(resultado)
else:
    cm, m, km = resultado
    print("Centímetros:", cm)
    print("Metros:", m)
    print("Kilómetros:", km)