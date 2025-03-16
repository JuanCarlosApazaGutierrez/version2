from app.models.Rol import Rol
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db

class ServiciosRol():

    def crear(nombre):
        rol = Rol(nombre)
        db.session.add(rol)
        db.session.commit()

        return True
    
    def obtener_todos():
        roles = Rol.query.all()

        datos_req = ['id_rol', 'nombre']

        respuesta = SerializadorUniversal.serializar_lista(roles, datos_req)

        return respuesta