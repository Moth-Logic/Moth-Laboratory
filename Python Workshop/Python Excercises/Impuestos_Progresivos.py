def calcular_impuesto(salario):
    impuesto = 0

    if salario > 1200:
        impuesto += (salario - 1200) * 0.15
        salario = 1200

    if salario > 800:
        impuesto += (salario - 800) * 0.10
        salario = 800

    # De 0 a 800 es exento (no suma nada)

    return impuesto


# Ejemplo de uso
salario = float(input("Ingrese el salario: "))

impuesto = calcular_impuesto(salario)

print("Impuesto a pagar:", impuesto)