def factorial(num):
    """Funcion que calcula el factorial de un numero.
    Entradas y restricciones :
    -numero positivo entero
    Salidas:
    Factorial del numero (int)"""
    if type(num) != int or num<0:
        raise Exception("numero debe ser int positivo.")
    fact = 1
    while num>1:
        fact *=num
        num -= 1
    return fact

def main():
    """Programa Principal del factorial"""
    try:
        num = int(input("Escriba un numero entero positivo: "))
        result = factorial(num)
        print(f"{num}! = {result}")
    except Exception as e:
        print (f"ERROR: {e}")

main()
