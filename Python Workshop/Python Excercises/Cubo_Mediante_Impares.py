"""Moth_Logic:
Este programa solicita un número entero positivo n y calcula su cubo
utilizando la suma de números impares consecutivos. Primero encuentra
el n-ésimo número impar y luego suma los siguientes n números impares
para obtener n^3. Finalmente, imprime el resultado."""

def cubo(n):
    i = 1
    ini = 1
    acu = 0

    # Encontrar el n-ésimo impar
    while i <= n - 1:
        ini = ini + (2 * i)
        i += 1

    acu = ini
    i = 0

    # Sumar los siguientes n-1 impares
    while i < n - 1:
        ini = ini + 2
        acu = acu + ini
        i += 1

    return acu


n = int(input("Indique el numero para elevar al cubo: "))

if n != 0:
    if n != 1:
        res = cubo(n)
        print(f"El cubo de {n} es: {res}")
    else:
        print(n)
else:
    print(n)
