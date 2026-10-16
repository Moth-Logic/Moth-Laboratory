import math

def esprimo(num):
    """Programa que lee un numero entero o positivo y imprime todos los numeros primos desde 2 hasta N.
    Entradas y Restricciones:
    - Número entero y positivo.
    Salidas:
    - Retorna True si num es primo, False en caso contrario"""
    if type(num) != int or num < 2:
        raise Exception("Número debe ser Integer Positivo mayor a 2")
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    # Solo revisar numeros impares
    for m in range(3, int(math.sqrt(num)) + 1, 2):
        if num % m == 0:
            return False
    return True

def main():
    try:
        num = int(input("Escriba un numero entero positivo: "))
        if num < 2:
            raise Exception("Número debe ser mayor a 2")
        print(f"Números primos desde 2 hasta {num}:")
        for i in range(2, num + 1):
            if esprimo(i):  # Revisar cada i, no "num"
                print(i)
    except Exception as e:
        print(f"Error: {e}")
main()
