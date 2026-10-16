def calcular_tarifa(mensajes, minutos_plenos, minutos_reducidos):
    tarifa_base = 5000
    total = tarifa_base

    # Mensajes (100 incluidos)
    if mensajes > 100:
        total += (mensajes - 100) * 5

    # Minutos plenos (60 incluidos)
    if minutos_plenos > 60:
        total += (minutos_plenos - 60) * 35

    # Minutos reducidos (todos se cobran)
    total += minutos_reducidos * 20

    # IVA 15%
    total_con_iva = total * 1.15

    return total_con_iva


# Ejemplo de uso
mensajes = int(input("Ingrese cantidad de mensajes: "))
plenos = int(input("Ingrese minutos plenos: "))
reducidos = int(input("Ingrese minutos reducidos: "))

monto = calcular_tarifa(mensajes, plenos, reducidos)

print("Monto a pagar:", monto)