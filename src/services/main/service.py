import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request
from datetime import datetime, timedelta

load_dotenv()
DB_URL = os.getenv("DB_URL")
usuarios_bp = Blueprint("usuarios_bp", __name__)
eventos_bp = Blueprint("eventos_bp", __name__)

client = pymongo.MongoClient(DB_URL)
db = client.kalendas
usuarios = db.usuarios
contactos = db.contactos   
eventos = db.eventos


#GET /usuarios/

@usuarios_bp.route("/", methods = ['GET'])
def get_usuarios():
    try:
        nombre = request.args.get("nombre")
        query = {}
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400
    
    try:
        if nombre:
            query["nombre"] = {"$regex": nombre, "$options": "i"}
    except Exception as e:
        return jsonify({"error": f"Error al convertir los ID: {str(e)}"}), 400
    try: 
        print("GET ALL USUARIOS")
        resultado = usuarios.find(query)
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /usuarios/<id>

@usuarios_bp.route("/<id>", methods = ["GET"])
def get_usuarios_by_id(id):
    try:
        resultado = usuarios.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if resultado:
        print("Busqueda de usuario por id")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener el mensaje con id {id}")
        return jsonify({"error":"Mensaje con id especificado no encontrada"}), 404

#POST /usuarios/

@usuarios_bp.route("/", methods = ['POST'])
def create_usuario():
    datos = request.json

    if not datos or not datos["email"] or not datos["nombre"]:
        print("Error: Parametros de entrada inválidos")

    nombre = datos["nombre"]
    email = datos["email"]
    usuario_existente = usuarios.find_one({"email":email})

    if usuario_existente:
        return jsonify({"error": f"Usuario con email {email} ya existe"}), 404
    else:
        usuarios.insert_one(datos)
        return jsonify({"response": f"Usuario con email {email} y nombre {nombre} creado correctamente"}), 201

#PUT /usuarios/<id>

@usuarios_bp.route("/<id>", methods=["PUT"])
def update_usuario(id):
    data = request.json
    dataFormateada = {"$set":data}
    respuesta = usuarios.find_one_and_update({"_id":ObjectId(id)}, dataFormateada, return_document=True)
    print(respuesta)

    if respuesta is None:
        return jsonify({"error":f"Error al actualizar el usuario con id {id}"}), 404
    else:
        nombre = respuesta["nombre"]
        return jsonify({"response":f"Usuario con nombre {nombre} actualizado correctamente"}), 200

#DELETE /usuarios/<id>

@usuarios_bp.route("/<id>", methods=['DELETE'])
def delete_usuario(id):

    try:
        usuario = usuarios.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"El usuario {id} no existe, por lo tanto no se puede borrar (no encontrado)", 404

    try:
        borrado = usuarios.delete_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"Error al borrar el usuario con id {id}", 400
    if borrado.deleted_count == 0:
        return f"El usuario {id} no existe, por lo tanto no se puede borrar", 200

    return "El usuario ha sido borrado con exito", 200

#CRUD DE LOS CONTACTOS DEL USUARIO

#GET /usuarios/<id>/contactos

@usuarios_bp.route("/<email>/contactos", methods = ['GET'])
def get_contactos(email):
    try: 
        print(f"GET ALL CONTACTOS FROM {email}")
        resultado = contactos.find({"email":email})
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#POST /usuarios/

@usuarios_bp.route("/<email>/contactos", methods = ['POST'])
def create_contacto(email):
    datos = request.json
    datos["email"] = email

    contactos.insert_one(datos)
    return jsonify({"response":"Contacto insertado correctamente"}), 200

#DELETE /usuarios/<id>

@usuarios_bp.route("/<email>/contactos/<emailContacto>", methods=['DELETE'])
def delete_contacto(email, emailContacto):
    try:
        contacto = contactos.find_one({"email":email,"emailContacto":emailContacto})
    except Exception as e:
        return f"El contacto {emailContacto} no existe, por lo tanto no se puede borrar (no encontrado)", 404

    try:
        borrado = contactos.delete_one({"email":email,"emailContacto":emailContacto})
    except Exception as e:
        return f"Error al borrar el contacto con email {emailContacto}", 400
    if borrado.deleted_count == 0:
        return f"El contacto {emailContacto} no existe, por lo tanto no se puede borrar", 200

    return "El contacto ha sido borrado con exito", 200

#CRUD DE LOS EVENTOS

@eventos_bp.route("/", methods = ['GET'])
def get_eventos():
    try:
        print("GET ALL EVENTOS")
        resultado = eventos.find()
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

@eventos_bp.route("/<id>", methods = ["GET"])
def get_eventos_by_id(id):
    try:
        resultado = eventos.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if resultado:
        print("Busqueda de evento por id")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener el evento con id {id}")
        return jsonify({"error":"Evento con id especificado no encontrada"}), 404

#POST /eventos/

@eventos_bp.route("/", methods=['POST'])
def create_evento():
    try:
        datos = request.json

        if "anfitrion" not in datos:
            return jsonify({"error": "Falta el anfitrion"}), 400
        if "descripcion" not in datos:
            return jsonify({"error": "Falta la descripcion"}), 400
        if "inicio" not in datos:
            return jsonify({"error": "Falta el inicio"}), 400
        if "duracion" not in datos:
            return jsonify({"error": "Falta la duracion"}), 400
        if "invitados" not in datos:
            return jsonify({"error": "Falta el invitados"}), 400

        if len(datos["descripcion"]) > 50:
            return jsonify({"error": "La descripcion no puede tener mas de 50 caracteres"}), 400

        for invitado in datos["invitados"]:
            if "email" not in invitado:
                return jsonify({"error": "Falta el email del invitado"}), 400
            if "estado" not in invitado:
                return jsonify({"error": "Falta el estado del invitado"}), 400
            if invitado["estado"] not in ["pendiente", "aceptada"]:
                return jsonify({"error": "El estado del invitado debe ser pendiente, aceptada"}), 400

            contacto = contactos.find_one({"email": datos["anfitrion"], "emailContacto": invitado["email"]})
            if not contacto:
                email = invitado["email"]
                return jsonify({"error": f"El invitado {email} no es un contacto del anfitrion"}), 400

        inicioDateTime = datetime.strptime(datos["inicio"], "%Y-%m-%dT%H:%M:%SZ")
        if inicioDateTime.minute % 15 != 0:
            return jsonify({"error": "El inicio del evento debe ser un multiplo de 15 minutos"}), 400

        if int(datos["duracion"]) % 15 != 0:
            return jsonify({"error": "La duracion del evento debe ser un multiplo de 15 minutos"}), 400

        eventos.insert_one(datos)
        return jsonify({"response": "Evento insertado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al insertar el evento {e}"}), 400
    
@eventos_bp.route("/<id>", methods=["PUT"])
def update_evento(id):
    datos = request.json

    if "anfitrion" in datos:
        #Comprobamos que anfitrion sea un usuario
        usuario = usuarios.find_one({"email": datos["anfitrion"]})
        if not usuario:
            return jsonify({"error": "El anfitrion no es un usuario"}), 400
        
    if "descripcion" in datos:
        if len(datos["descripcion"]) > 50:
            return jsonify({"error": "La descripcion no puede tener mas de 50 caracteres"}), 400

    if "inicio" in datos:
        inicioDateTime = datetime.strptime(datos["inicio"], "%Y-%m-%dT%H:%M:%SZ")
        if inicioDateTime.minute % 15 != 0:
            return jsonify({"error": "El inicio del evento debe ser un multiplo de 15 minutos"}), 400

    if "duracion" in datos:
        if int(datos["duracion"]) % 15 != 0:
            return jsonify({"error": "La duracion del evento debe ser un multiplo de 15 minutos"}), 400
    
    if "invitados" in datos:
        for invitado in datos["invitados"]:
            if "email" not in invitado:
                return jsonify({"error": "Falta el email del invitado"}), 400
            if "estado" not in invitado:
                return jsonify({"error": "Falta el estado del invitado"}), 400
            if invitado["estado"] not in ["pendiente", "aceptada"]:
                return jsonify({"error": "El estado del invitado debe ser pendiente, aceptada"}), 400

            contacto = contactos.find_one({"email": datos["anfitrion"], "emailContacto": invitado["email"]})
            if not contacto:
                email = invitado["email"]
                return jsonify({"error": f"El invitado {email} no es un contacto del anfitrion"}), 400

    dataFormateada = {"$set":datos}
    respuesta = eventos.find_one_and_update({"_id":ObjectId(id)}, dataFormateada, return_document=True)
    print(respuesta)

    if respuesta is None:
        return jsonify({"error":f"Error al actualizar el evento con id {id}"}), 404
    else:
        descripcion = respuesta["descripcion"]
        return jsonify({"response":f"Evento con descripcion {descripcion} actualizado correctamente"}), 200
    
@eventos_bp.route("/<id>", methods=['DELETE'])
def delete_evento(id):
    try:
        evento = eventos.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"El evento {id} no existe, por lo tanto no se puede borrar (no encontrado)", 404

    try:
        borrado = eventos.delete_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"Error al borrar el evento con id {id}", 400
    if borrado.deleted_count == 0:
        return f"El evento {id} no existe, por lo tanto no se puede borrar", 200

    return "El evento ha sido borrado con exito", 200

#FUNCIONES ADICIONALES

#Buscar entre los contactos de un usuario, identificado por su email, a partir de una cadena con parte del nombre
#del contacto, devolviendo una lista de contactos (emails y nombres).

@usuarios_bp.route("/<email>/contactos/buscar", methods = ['GET'])
def buscar_contactos(email):
    try:
        nombre = request.args.get("nombre")
        query = {}
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400
    
    try:
        if nombre:
            query["nombre"] = {"$regex": nombre, "$options": "i"}
    except Exception as e:
        return jsonify({"error": f"Error al convertir los ID: {str(e)}"}), 400
    try: 
        print(f"GET ALL CONTACTOS FROM {email} WITH NAME {nombre}")
        resultado = contactos.find({"email":email, "nombreContacto": query["nombre"]})
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#Invitar a un evento a un contacto de un usuario, identificado por su email. El contacto invitado se incluirá en la
#lista de invitados del evento, con la invitación en estado pendiente

@eventos_bp.route("/<id>/invitar", methods = ['POST'])
def invitar_contacto(id):
    try:
        datos = request.json
        email = datos["email"]
        estado = "pendiente"
        invitado = {"email": email, "estado": estado}
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400

    try:
        evento = eventos.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    try:
        contacto = contactos.find_one({"email": evento["anfitrion"], "emailContacto": email})
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    if not contacto:
        return jsonify({"error": "El contacto no es un contacto del anfitrion"}), 404
    
    #Comprobar que el contacto no esté ya invitado
    for invitado in evento["invitados"]:
        if invitado["email"] == email:
            return jsonify({"error": "El contacto ya ha sido invitado"}), 404
        
    try:
        eventos.update_one({"_id":ObjectId(id)}, {"$push": {"invitados": invitado}})
    except Exception as e:
        return jsonify({"error": "Error al insertar el contacto en la lista de invitados"}), 404

    return jsonify({"response": f"Contacto con email {email} invitado correctamente"}), 200

#Aceptar una invitación a un evento. El estado de la invitación pasará a aceptada.
@eventos_bp.route("/<id>/aceptar", methods = ['POST'])
def aceptar_invitacion(id):
    try:
        datos = request.json
        email = datos["email"]
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400

    try:
        evento = eventos.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    try:
        eventos.update_one({"_id":ObjectId(id), "invitados.email": email}, {"$set": {"invitados.$.estado": "aceptada"}})
    except Exception as e:
        return jsonify({"error": "Error al actualizar el estado de la invitacion"}), 404

    return jsonify({"response": f"Invitacion aceptada correctamente"}), 200

#Reprogramar un evento ya pasado, indicando cuánto tiempo se desplaza (un número de días determinado, una
#semana, un mes, o un año). Se creará un nuevo evento, con la nueva fecha y el resto de valores iguales a los del
#evento reprogramado.

@eventos_bp.route("/<id>/reprogramar", methods = ['POST'])

def reprogramar_evento(id):
    try:
        datos = request.json
        dias = datos["dias"]
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400

    try:
        evento = eventos.find_one({"_id":ObjectId(id)})
        del(evento["_id"])
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    try:
        inicioDateTime = datetime.strptime(evento["inicio"], "%Y-%m-%dT%H:%M:%SZ")
        nuevoInicio = inicioDateTime + timedelta(days=(int(dias)))
        nuevoInicioString = nuevoInicio.strftime("%Y-%m-%dT%H:%M:%SZ")
        evento["inicio"] = nuevoInicioString
        eventos.insert_one(evento)
    except Exception as e:
        return jsonify({"error": f"Error al reprogramar el evento {e}"}), 404

    return jsonify({"response": f"Evento reprogramado correctamente"}), 200

#Obtener la agenda de un usuario, representada por una lista de eventos, tanto propios como invitados, por orden
#ascendente de inicio

@usuarios_bp.route("/<email>/agenda", methods = ['GET'])

def get_agenda(email):
    try:
        query = {"$or": [{"anfitrion": email}, {"invitados.email": email}]}
        resultado = eventos.find(query).sort("inicio", pymongo.ASCENDING)
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400