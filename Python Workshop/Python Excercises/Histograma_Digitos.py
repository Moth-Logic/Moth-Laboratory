def Histograma(num):
    """procedimiento que a partir de un valor entero mayor o igual que cero imprima un histograma en
donde la magnitud de cada barra está en función de cada uno de los dígitos.
    Entrada: Numero Entero Positivo
    Salida: *******"""
    if type(num) != int or num<0:
        raise Exception("Numero debe ser entero positivo.")
    print(f"{num}")
    while num>0:
        numpri = num%10
        numsec = int(numpri)
        num //= 10
        print(f"{numpri}:{'*'* numsec}")

Histograma(123456789)