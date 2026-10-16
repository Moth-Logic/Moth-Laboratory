"""
Moth_Logic:
Este programa solicita un número entero mayor que 0 y aplica la conjetura de Collatz.
Si el número es par, se divide entre 2; si es impar, se multiplica por 3 y se le suma 1.
El proceso continúa hasta que el número llega a 1, imprimiendo cada valor intermedio.
"""

a = int(input("Numero entero mayor que 0: "))

if a > 0:
    if a == 1:
        print(1)
    else:
        while a != 1:
            if a % 2 == 0:
                a = a // 2
            else:
                a = 3 * a + 1

            print(a)
else:
    print("ERROR: Numero debe ser mayor que 0")
