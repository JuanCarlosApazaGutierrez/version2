from flask import request, jsonify
from app.models.usuario_model import UsuarioModel

def agregar_usuario():
    datos = request.get_json()
    nombre = datos.get("nombre")
    correo = datos.get("correo")
    ci = datos.get('ci')
    tareas = datos.get('tareas')

    if not nombre or not correo:
        return jsonify({"mensaje": "Faltan datos"}), 400

    usuario_id = UsuarioModel.agregar_usuario(nombre, correo, ci, tareas)
    return jsonify({"mensaje": "Usuario agregado con éxito", "id": usuario_id})

def obtener_usuarios():
    usuarios = UsuarioModel.obtener_usuarios()
    return jsonify(usuarios)