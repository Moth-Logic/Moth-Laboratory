"""Moth_Logic:
Este programa recibe un número entero n y un dígito d. Recorre cada
dígito de n y construye un nuevo número eliminando todas las apariciones
del dígito d. Mantiene el orden original de los dígitos restantes."""

def elimina(n, d):
    res = 0
    fac = 1

    while n > 0:
        dig = n % 10
        n = n // 10

        if dig != d:
            res = res + dig * fac
            fac = fac * 10

    return res


n = int(input("Ingrese el número: "))
d = int(input("Ingrese el dígito a eliminar: "))

resultado = elimina(n, d)
print(resultado)
