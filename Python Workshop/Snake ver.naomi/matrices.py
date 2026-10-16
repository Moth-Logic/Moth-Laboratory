def crear_matriz(filas, cols, valor):
    M = []
    for f in range(filas):
        fila = []
        for c in range(cols):
            fila.append(valor)
        M.append(fila)
    return M
