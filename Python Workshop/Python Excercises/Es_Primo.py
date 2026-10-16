import math
def esprimo(num):
    """Programa que lee un numero entero o positivo y dice si corresponde a un número primo.
Entradas y Restricciones:
- Número entero y positivo.
Salidas:
- Resultado booleano si es primo o no."""
    if type(num) != int or num<0:
        raise Exception("Número debe ser Integer Positivo")
    if num==1
        return False

    for m in range(2, int(math.sqrt(num))+1):
        if num%m == 0:
            return False
    return True

def main():
    try:
        num= int(input("Escriba un numero entero positivo:"))
        result = esprimo(num)
        print(f"Its {result} {num} is a prime number")
    except Exception  as e:
        print(f"Error: {e}")

main()
