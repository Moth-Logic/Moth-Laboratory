import pygame
import random
import matrices

matriz = []
filas = 20
cols = 20

#serpiente
jupa_f = 0
jupa_c = 0
cola_howbig = 1
viva = True
direccion = "R" #UP DOWN RIGHT LEFT
MANZANA = -1

def poner_manzana():
    manzana_f = random.randrange(0, filas)
    manzana_c = random.randrange(0, cols)
    while matriz[manzana_f][manzana_c] != 0:
        manzana_f = random.randrange(0, filas)
        manzana_c = random.randrange(0, cols)
    matriz[manzana_f][manzana_c] = MANZANA

def siguiente_posicion():
    if direccion == "R":
        return jupa_f, jupa_c+1
    if direccion == "L":
        return jupa_f, jupa_c-1
    if direccion == "U":
        return jupa_f-1, jupa_c
    if direccion == "D":
        return jupa_f+1, jupa_c

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
    global viva, cola_howbig, jupa_f, jupa_c
    if viva:
        if shediedlol():
            viva = False
        else:
            nueva_f, nueva_c = siguiente_posicion()
            if matriz[nueva_f][nueva_c] == MANZANA:
                cola_howbig += 1
                poner_manzana()
            for f in range(filas):
                for c in range(cols):
                    if matriz[f][c] > 0:
                        matriz[f][c] -= 1
            matriz[nueva_f][nueva_c] = cola_howbig
            jupa_f = nueva_f
            jupa_c = nueva_c

def init():
    global filas, cols, jupa_f, jupa_c, cola_howbig, viva, direccion, matriz
    filas = 50
    cols = 50
    matriz = matrices.crear_matriz(filas, cols, 0)
    jupa_f = filas // 2
    jupa_c = cols // 3
    cola_howbig = 1
    viva = True
    direccion = "R"
    matriz[jupa_f][jupa_c] = cola_howbig
    poner_manzana()
