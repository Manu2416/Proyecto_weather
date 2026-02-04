from flask import Flask, render_template, request, jsonify
# Importamos todas tus funciones
from funciones import (crear_conexion, insertar_paises, insertar_fronteras, 
                       leer_json, insertar_temps, visualizar_temperatura, 
                       ver_fronteras, ver_paises)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insertar_temps', methods=['POST'])
def api_actualizar_temperaturas():
    conexion = crear_conexion()
    if not conexion:
        return jsonify({"status": "error", "message": "No hay conexio con la base de datos"})
    
    paises_json = leer_json()
    
    try:
        insertar_temps(conexion, paises_json)
        conexion.close()
        return jsonify({"status": "success", "message": "Temperaturas actualizadas"})
    except Exception as e:
        if conexion: conexion.close()
        return jsonify({"status": "error", "message": f"Error en la API: {str(e)}"})
    
@app.route('/insertar_paises', methods=['POST'])
def api_paises():
    con = crear_conexion()
    paises_json = leer_json()
    res = insertar_paises(con, paises_json)
    con.close()
    return jsonify(res)

@app.route("/insertar_fronteras",methods=["POST"])
def api_fronteras():
    conexion = crear_conexion()
    fronteras = leer_json()
    res = insertar_fronteras(conexion,fronteras)
    conexion.close()
    return jsonify(res)

@app.route("/ver_paises",methods=["POST"])
def api_verpaises():
    con = crear_conexion()
    cca3 = ver_paises(con) 
    
    lista_paises = []
    for fila in cca3:
        lista_paises.append(fila[0])
    return jsonify({"status":"success","paises":lista_paises})




@app.route('/consultar', methods=['POST'])
def api_consultar():
    pais_buscado = request.form.get('pais').upper() 
    con = crear_conexion()
    
    # Obtener temp principal
    temp_data = visualizar_temperatura(con, pais_buscado)
    if not temp_data:
        con.close()
        return jsonify({"error": "No encontrado"}), 404
    # temp_data es una tupla y le restamos para pasarlo a grados
    temp_valor = round(temp_data[0]-273.15 , 2) if temp_data else "N/A"
    
    # Obtener fronteras
    fronteras_raw = ver_fronteras(con, pais_buscado)
    lista_fronteras = []
    for f in fronteras_raw:
        cca3_f = f[0]
        t_f = visualizar_temperatura(con, cca3_f)
        t_g = round(t_f[0]-273.15,2)
        temp_f_valor = t_g if t_g else "N/A"
        lista_fronteras.append({"nombre": cca3_f, "temp": temp_f_valor})
    
    con.close()
    return jsonify({
        "pais": pais_buscado,
        "temperatura": temp_valor,
        "fronteras": lista_fronteras
    })


if __name__ == '__main__':
    app.run(debug=True)