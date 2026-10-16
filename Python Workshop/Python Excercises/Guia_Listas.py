correos= ['outlook','hotmail','gmail'] #La posición de los elementos empieza respectivamente desde 0 en adelante
print (*correos) #Para desempaquetar se usa un arroba antes de la variable

#Agrega el elemento indicado al final de la lista
correos.append ('yahoo')
print (correos)

#Elimina elementos de la lista
eliminado= correos.pop(2)
print (eliminado)
print (correos)
del correos [1] #Elimina la posición indicada en los paréntesis cuadrados
print (correos)

#Cantidad de elementos en la lista
cantidad= len (correos)
print (cantidad)

#Extiende la lista con otra lista
correo2= ['yahoo','hotmail','gmail']
correos.extend(correo2)
print (correos)

#Elimina la primera coincidencia de la lista
correos.remove ('yahoo')
print (correos)

#Inserta un elemento en la posición indicada
correos.insert (1,'CTPP')
print (correos)

#Indica la posición de un elemento de la lista
posición= correos.index ('yahoo')
print ("El índice de elementos del operador de la lista es de: ",posición)

numeros= [3,2,1]
print (numeros)

#Ordena la lista
numeros.sort()
print (numeros)

#Revierte la lista
lista=[1,2,3]
print (lista)
lista.reverse()
print (lista)

#Indica cuantas veces se repite un número
otralista= [2,5,4,6,5,7,8,1]
rep=otralista.count (5)
print (rep)

#Une las listas
listax1= [1,2,3]
listax2= [4,5,6]
listax3= listax1+listax2

#Quita lo que hay dentro de la lista, solo deja los parénteses
listax3.clear()
print (listax3)

listax3= listax1+listax2
print (listax3)

print (listax3 [1:5]) #Muestra solo los espacios indicados

copia= listax1.copy ()
print (copia)

copia2= listax1
copia2.append (4)
print (copia)
print ("Esto es una copia dos",copia2)
print ("Esta es una copia de lista1",listax1)