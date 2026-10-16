def monto_exacto(monto):
    denominaciones = [50000, 20000, 10000, 5000, 2000, 1000, 500, 100, 50, 25, 10, 5]

    resultado = []

    for d in denominaciones:
        cantidad = monto // d
        monto = monto % d
        resultado.append((d, cantidad))

    return resultado, monto


# Ejemplo de uso
monto = int(input("Ingrese el monto: "))

resultado, sobrante = monto_exacto(monto)

for d, c in resultado:
    print(f"{c} x {d}")

print("Sobran", sobrante, "colones")