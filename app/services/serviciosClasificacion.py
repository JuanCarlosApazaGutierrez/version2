from app.models.clasificacion import Clasificacion
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db

class ServiciosClasificacion():
    def crear(nombre, descripcion):
        clasificacion = Clasificacion(nombre, descripcion)

        db.session.add(clasificacion)
        db.session.commit()

        return True
    
    def obtener_todos():
        clasificaciones = Clasificacion.query.all()

        datos_req = ['id_clasificacion', 'nombre', 'descripcion', 'activo']

        respuesta = SerializadorUniversal.serializar_lista(clasificaciones, datos_req)

        return respuesta 