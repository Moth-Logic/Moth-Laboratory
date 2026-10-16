import math

def es_cuadrado_perfecto(m):
    if m < 0:
        return False

    raiz = int(math.sqrt(m))
    return raiz * raiz == m


# Ejemplo de uso
m = int(input("Ingrese un número entero positivo: "))

if es_cuadrado_perfecto(m):
    print("Sí es un cuadrado perfecto")
else:
    print("No es un cuadrado perfecto")