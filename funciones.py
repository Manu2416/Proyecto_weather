import mysql.connector
import json   
import requests
from datetime import datetime
import xml.etree.ElementTree as ET


def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="temperaturas"
        )
        return conexion
    
    except mysql.connector.Error as err:
        print("No se puede hacer conexión:", err)
        return None

def insertar_paises(conexion, lista_paises):
    cursor = conexion.cursor()
    
    try:
        # Miramos a ver si hay paises ya 
        cursor.execute("SELECT COUNT(*) FROM paises")
        cantidad = cursor.fetchone()[0]

        if cantidad > 0:
            cursor.close()
            return {"status": "warning", "message": "Los países ya están en la base de datos."}
           

        # Si la tabla está vacía, preparamos la inserción
        consulta = """
            INSERT INTO paises (cca2, cca3, nombre, capital, region, subregion, miembroUE, latitud, longitud) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for pais in lista_paises:
            # Extracción segura de datos 
            nombre = pais.get("name", {}).get("common", "Desconocido")
            
        
            capitales = pais.get("capital", [])
            capital = capitales[0] if capitales else "Sin capital"
            
            latlng = pais.get("latlng", [None, None])
            latitud = latlng[0]
            longitud = latlng[1]

            valores = (
                pais.get("cca2"),
                pais.get("cca3"),
                nombre,
                capital,
                pais.get("region"),
                pais.get("subregion"),
                pais.get("unMember"),
                latitud,
                longitud
            )

            cursor.execute(consulta, valores)
        conexion.commit()
        cursor.close()
        return {"status": "success", "message": f"Se han insertado {len(lista_paises)} países correctamente."}

    except Exception as e:
        # Si algo falla devolvemos el error al Front
        return {"status": "error", "message": f"Error crítico al insertar países: {str(e)}"}

def insertar_fronteras(conexion, lista_paises):
    cursor = conexion.cursor()
    
    # Comprobamos si ya existen datos
    cursor.execute("SELECT COUNT(*) FROM fronteras")
    cantidad = cursor.fetchone()[0]

    if cantidad > 0:
        cursor.close()
        # Devolvemos un mensaje y un booleano para que el front sepa qué color poner
        return {"status": "warning", "message": "Los países ya estaban insertados previamente."}

    try:
        for pais in lista_paises:
            cursor.execute("SELECT idpais FROM paises WHERE cca3 = %s", (pais.get('cca3'),))
            resultado = cursor.fetchone()
            
            if resultado:
                id_pais_principal = resultado[0]
                lista_fronteras = pais.get("borders", []) 
                for frontera_cca3 in lista_fronteras:
                    cursor.execute("INSERT INTO fronteras (idpais, cca3_frontera) VALUES (%s, %s)", 
                                 (id_pais_principal, frontera_cca3))

        conexion.commit()
        cursor.close()
        return {"status": "success", "message": "¡Éxito! Fronteras insertadas correctamente."}
    
    except Exception as e:
        return {"status": "error", "message": f"Error al insertar: {str(e)}"}
    

def leer_json():
    with open("paises_europa.json", "r", encoding="utf-8") as archivo:
         paises = json.load(archivo)
         return paises
    
def visualizar_temperatura(conexion, pais):
    cursor = conexion.cursor()
    # Buscamos el id del país
    cursor.execute("SELECT idpais FROM paises WHERE cca3 = %s", [pais])
    resultado = cursor.fetchone()
 
    if resultado is None:
        cursor.close()
        return None  # Devolvemos None para que el servidor sepa que no hay datos
    
    id_pais = resultado[0]
    
    # 2. Buscamos la temperatura más reciente
    cursor.execute("SELECT temperatura FROM temperaturas WHERE idpais = %s ORDER BY timestamp DESC LIMIT 1", [id_pais])
    temperatura = cursor.fetchone()
    
    cursor.close()
    return temperatura # Devuelve una tupla (25.5,) o None si no hay temperaturas

def ver_fronteras(conexion,pais):
    #selecciono el id del pais
    cursor = conexion.cursor()
    cursor.execute("SELECT idpais FROM paises where cca3 = %s",[pais])
    resultado = cursor.fetchone()
    id_pais = resultado[0]
    #busco sus fronteras
    cursor.execute("Select cca3_frontera from fronteras where idpais = %s AND cca3_frontera IN (SELECT cca3 FROM paises)",[id_pais])
    fronteras = cursor.fetchall()

    return fronteras

def ver_paises(conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT cca3 FROM paises")
    resultado = cursor.fetchall()

    return resultado

def insertar_temps(conexion, paises):
    api_key = "0bfe1323d65ba70d1453570dbad38e3c"
    cursor = conexion.cursor()
    
    for i, pais in enumerate(paises):
        cursor.execute("SELECT idpais, latitud, longitud FROM paises WHERE cca3 = %s", (pais.get('cca3'),))
        resultado = cursor.fetchone()
        
        if not resultado:
            continue
            
        id_pais, latitud, longitud = resultado

   
        if i % 2 == 0:
    
            datos = obtener_clima(latitud, longitud, api_key) 
            if datos:
                temp = datos["main"].get("temp")
                feels_like = datos["main"].get("feels_like")
                temp_min = datos["main"].get("temp_min")
                temp_max = datos["main"].get("temp_max")
                humidity = datos["main"].get("humidity")
                fecha_medicion = datetime.fromtimestamp(datos.get("dt")).strftime('%Y-%m-%d %H:%M:%S')
                amanecer = datetime.fromtimestamp(datos["sys"].get("sunrise")).strftime('%Y-%m-%d %H:%M:%S')
                atardecer = datetime.fromtimestamp(datos["sys"].get("sunset")).strftime('%Y-%m-%d %H:%M:%S')
        else:
           # USAR XML
            xml_raw = obtener_clima_xml(latitud, longitud, api_key) #
            if xml_raw:
                root = ET.fromstring(xml_raw)
                temp = root.find('temperature').get('value')
                feels_like = root.find('feels_like').get('value')
                temp_min = root.find('temperature').get('min')
                temp_max = root.find('temperature').get('max')
                humidity = root.find('humidity').get('value')
                
                # Fechas en el XML de OpenWeather ya vienen en formato texto ISO
                # Las limpiamos un poco para MySQL
                fecha_medicion = root.find('lastupdate').get('value').replace('T', ' ')
                amanecer = root.find('city/sun').get('rise').replace('T', ' ')
                atardecer = root.find('city/sun').get('set').replace('T', ' ')

        valores = (id_pais, fecha_medicion, temp, feels_like, temp_min, temp_max, humidity, amanecer, atardecer)
        consulta = """INSERT INTO temperaturas(idpais, timestamp, temperatura, sensacion, minima, maxima, humedad, amanecer, atardecer) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(consulta, valores)

    conexion.commit()
    cursor.close()

def obtener_clima(lat, lon, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    #https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}
    parametros = {"lat": lat, "lon": lon, "appid": api_key}
    respuesta = requests.get(url, params=parametros)
    
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        
        return None
def obtener_clima_xml(lat, lon, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    # Añadimos el parámetro 'mode': 'xml'
    parametros = {"lat": lat, "lon": lon, "appid": api_key, "mode": "xml"}
    respuesta = requests.get(url, params=parametros)
    
    if respuesta.status_code == 200:
        # Devolvemos el texto plano del XML para procesarlo luego
        return respuesta.text 
    else:
        return None