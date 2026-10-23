Documento = "Hola. este es un ejemplo de texto para contar palabras. Me gusta comer 90 pizzas."

def contar_palabras(texto):
    delimit = [",", ".", ";", ":", "¡", "!", "¿", "?", "_", "-", "/", "(", ")", " "]
    words = 0
    en_palabra = False # el char anterior es parte de una palabra?

    for letra in texto:
        if letra not in delimit:
            if not en_palabra:
                words += 1       # si hay un delimitador = nueva palabra
                en_palabra = True
        else:
            en_palabra = False
            
    return words
            
print(contar_palabras(Documento))
