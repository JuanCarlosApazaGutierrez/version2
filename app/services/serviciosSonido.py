from app.models.sonido import Sonido
from app.models.frecuencia import Frecuencia
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db
from sqlalchemy import func

class ServiciosSonido():
    def crear(paciente, sonido):
        registro = Sonido(paciente, sonido)

        db.session.add(registro)
        db.session.commit()
        if registro:
            return registro
        else:
            return None
    
    def obtener_todos():
        registros = Sonido.query.all()

        datos_req = ['id', 'id_paciente', 'fecha', 'sonido']

        respuesta = SerializadorUniversal.serializar_lista(registros, datos_req)

        return respuesta
    
    def obtener_por_paciente(paciente):
        registros = Sonido.query.filter_by(id_paciente = paciente)

        datos_req = ['id', 'id_paciente', 'fecha', 'sonido']

        respuesta = SerializadorUniversal.serializar_lista(registros, datos_req)

        return respuesta
    
    def obtener_por_fecha(fecha):
        registros = Sonido.query.filter_by(fecha = fecha)

        respuestas_mod = []

        for fila in registros:
            fecha_reg = fila.fecha.strftime('%Y-%m-%d')
            if fecha == fecha_reg:
                respuestas_mod.append(fila)

 
        datos_req = ['id', 'id_paciente', 'fecha', 'sonido']

        respuesta = SerializadorUniversal.serializar_lista(registros, datos_req)

        return respuesta
    
    def obtener_por_paciente_fecha(paciente, fecha):
        registros = Sonido.query.filter_by(id_paciente = paciente, fecha = fecha)

        respuestas_mod = []

        for fila in registros:
            fecha_reg = fila.fecha.strftime('%Y-%m-%d')
            if fecha == fecha_reg:
                respuestas_mod.append(fila)

 
        datos_req = ['id', 'id_paciente', 'fecha', 'sonido']

        respuesta = SerializadorUniversal.serializar_lista(registros, datos_req)

        return respuesta


    def buscar_registro_cercano(fecha_dada, id_paciente):

        registro = db.session.query(Frecuencia).filter(
            Frecuencia.id_paciente == id_paciente,  # Filtro por rol
            Frecuencia.fecha < fecha_dada    # Filtro para que la fecha sea menor que la fecha dada
        )
        '''.order_by(
            func.abs(func.julianday(Frecuencia.fecha) - func.julianday(fecha_dada))  # Ordenar por la diferencia absoluta con la fecha dada
        )'''

        registro = SerializadorUniversal.serializar_lista(registro, ['id_frecuencia', 'id_clasificacion'])
        
        if registro:
            registro = registro[len(registro)-1]
        else:
            registro = None  # Seleccionamos el primer registro más cercano

        return registro