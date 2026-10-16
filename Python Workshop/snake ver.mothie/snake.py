import random
import matrices

matriz = []
filas = 20
cols = 20

# serpiente
jupa_f = 0
jupa_c = 0
cola_howbig = 1
viva = True
direccion = "R"  # UP DOWN RIGHT LEFT
manzanas_comidas = 0

# Valores de celda
MANZANA = -1
MANZANA_DORADA = -2
VENENO = -3
NUM_VENENOS = 10


def poner_manzana():
    f = random.randrange(0, filas)
    c = random.randrange(0, cols)
    while matriz[f][c] != 0:
        f = random.randrange(0, filas)
        c = random.randrange(0, cols)
    numero = random.randrange(0, 100)
    if numero < 5:
        matriz[f][c] = MANZANA_DORADA
    else:
        matriz[f][c] = MANZANA


def poner_veneno():
    f = random.randrange(0, filas)
    c = random.randrange(0, cols)
    while matriz[f][c] != 0:
        f = random.randrange(0, filas)
        c = random.randrange(0, cols)
    matriz[f][c] = VENENO


def siguiente_posicion():
    if direccion == "R":
        return jupa_f, jupa_c + 1
    if direccion == "L":
        return jupa_f, jupa_c - 1
    if direccion == "U":
        return jupa_f - 1, jupa_c
    if direccion == "D":
        return jupa_f + 1, jupa_c


def shediedlol():
    nueva_f, nueva_c = siguiente_posicion()
    if nueva_f < 0 or nueva_f >= filas:
        return True
    if nueva_c < 0 or nueva_c >= cols:
        return True
    return matriz[nueva_f][nueva_c] > 0


def cambiar_direccion(nueva_direccion):
    global direccion
    if nueva_direccion in ("U", "D") and direccion in ("L", "R"):
        direccion = nueva_direccion
    elif nueva_direccion in ("L", "R") and direccion in ("U", "D"):
        direccion = nueva_direccion


def avanzar():
    global viva, cola_howbig, jupa_f, jupa_c, manzanas_comidas
    if viva:
        if shediedlol():
            viva = False
        else:
            nueva_f, nueva_c = siguiente_posicion()
            celda = matriz[nueva_f][nueva_c]

            if celda == MANZANA:
                cola_howbig += 1
                manzanas_comidas += 1
                poner_manzana()
            elif celda == MANZANA_DORADA:
                cola_howbig += 5
                manzanas_comidas += 1
                poner_manzana()
            elif celda == VENENO:
                if cola_howbig <= 2:
                    viva = False
                    return
                else:
                    cola_howbig = cola_howbig // 2
                    # Recortar la cola en la matriz
                    for f in range(filas):
                        for c in range(cols):
                            if matriz[f][c] > cola_howbig:
                                matriz[f][c] = 0
                poner_veneno()

            for f in range(filas):
                for c in range(cols):
                    if matriz[f][c] > 0:
                        matriz[f][c] -= 1

            matriz[nueva_f][nueva_c] = cola_howbig
            jupa_f = nueva_f
            jupa_c = nueva_c


def init():
    global filas, cols, jupa_f, jupa_c, cola_howbig, viva, direccion, matriz, manzanas_comidas
    filas = 50
    cols = 50
    matriz = matrices.crear_matriz(filas, cols, 0)
    jupa_f = filas // 2
    jupa_c = cols // 3
    cola_howbig = 1
    viva = True
    direccion = "R"
    manzanas_comidas = 0
    matriz[jupa_f][jupa_c] = cola_howbig
    poner_manzana()
    for _ in range(NUM_VENENOS):
        poner_veneno()
