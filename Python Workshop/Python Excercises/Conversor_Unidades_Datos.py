def convertir(valor, origen, destino):
    factores = {
        "B": 2**0,
        "K": 2**10,
        "M": 2**20,
        "G": 2**30,
        "T": 2**40,
        "P": 2**50,
        "E": 2**60,
        "Z": 2**70,
        "Y": 2**80
    }

    origen = origen.upper()
    destino = destino.upper()

    return valor * factores[origen] / factores[destino]


# Uso
v = int(input("Valor: "))
o = input("Unidad origen (B,K,M,G,T,P,E,Z,Y): ")
d = input("Unidad destino (B,K,M,G,T,P,E,Z,Y): ")

print("Resultado:", convertir(v, o, d))