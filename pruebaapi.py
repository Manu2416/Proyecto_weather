import requests

def obtener_clima(lat, lon, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    parametros = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        #xml
        
    }
    
    respuesta = requests.get(url, params=parametros)
    
    if respuesta.status_code == 200:
        print("hola")
        return respuesta.json()
    else:
        print("error")

api_key = "0bfe1323d65ba70d1453570dbad38e3c"

datos = obtener_clima("49.25","-2.16667",api_key)



print(datos["sys"])
