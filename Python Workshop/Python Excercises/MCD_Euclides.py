def mcd_euclides(M, N):
    # Asegurar que M sea el mayor
    if M < N:
        M, N = N, M

    while N != 0:
        R = M % N  # residuo
        M = N
        N = R

    return M


# Ejemplo de uso
M = int(input("Ingrese el primer número: "))
N = int(input("Ingrese el segundo número: "))

resultado = mcd_euclides(M, N)

print("El MCD es:", resultado)