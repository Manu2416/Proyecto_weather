from funciones import crear_conexion , insertar_paises ,insertar_fronteras, leer_json, insertar_temps,visualizar_temperatura,ver_fronteras,ver_paises


opcion = int(input("Que quieres hacer"))

if opcion == 1:
    paises = leer_json()
    conexion = crear_conexion()
    insertar_paises(conexion,paises)
    print("paises insertados correctamente ")

elif opcion == 2:
    paises = leer_json()
    conexion = crear_conexion()
    insertar_fronteras(conexion,paises)
    print("paises fronteras correctamente ")

elif opcion == 3:
    paises = leer_json()
    conexion = crear_conexion()
    insertar_temps(conexion,paises)
    print("temperaturas insertadas correctamente ")

elif opcion == 4:
    pais = input("dame un pais ")
    conexion = crear_conexion()
    print( "Esta es la mas reciente",visualizar_temperatura(conexion,pais))
    fronteras = ver_fronteras(conexion,pais)
    for i in range (len(fronteras)):
        print(f"Frontera {pais} y su temperatura mas reciente {visualizar_temperatura(conexion,fronteras[i][0])}")
elif opcion == 5:
    conexion = crear_conexion()
    lista_paises = ver_paises(conexion)
    print(lista_paises)
