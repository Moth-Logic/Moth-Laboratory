Persona= {
    'nombre': 'Lorenzo',
    'edad': 30,
    'profesión': 'psicólogo'
}
print (Persona)
print (Persona ['nombre'])
print (Persona ['edad'])
print (Persona ['profesión'])

for elemento in Persona:
    print (elemento)

for llave,valor in Persona.items():
    print ("clave:",llave,"valor:",valor)

print (Persona.get('edad'))

Persona ['altura']= 1.65
print (Persona)

del Persona ['profesión']
print (Persona)

print ('nombre' in Persona)
print ('profesión' in Persona)

#Mañana: escribir en un archivo