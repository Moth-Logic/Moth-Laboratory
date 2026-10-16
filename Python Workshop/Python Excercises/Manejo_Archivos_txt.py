"""
1. Escribir datos en un archivo APPEND.
2. Modo APPEND (agregar): argumento 'a' agregará al final del archivo sin borrar el contenido.
3. Modo WRITE (escritura): argumento 'w' sobreescribirá el contenido existente.
4. Modo read (lectura): argumento 'r' solo se pueden leer los datos del archivo.
"""

with open ('datos.txt','a') as archivo:
    archivo.write ("Holas\n")

archivo= open ('datos.txt','w')
archivo.write ('idk')

archivo.close ()

archivo=open ('datos.txt','r')
contenido= archivo.read ()
archivo.close

print (contenido)