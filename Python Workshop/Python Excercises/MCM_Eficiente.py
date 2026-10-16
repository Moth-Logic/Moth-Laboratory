def mcd(A, B):
    while B != 0:
        A, B = B, A % B
    return A

def mcm(A, B):
    D = mcd(A, B)  # paso 1
    return (A * B) // D  # paso 2


# Ejemplo de uso
A = int(input("Ingrese el primer número: "))
B = int(input("Ingrese el segundo número: "))

resultado = mcm(A, B)

print("El MCM es:", resultado)