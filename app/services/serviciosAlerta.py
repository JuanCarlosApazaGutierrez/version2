from app.models.alerta import Alerta
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db

class ServiciosAlerta():

    def crear(paciente, alerta, frecuencia, sonido):
        alerta = Alerta(paciente, alerta, frecuencia, sonido)
        db.session.add(alerta)
        db.session.commit()

        return True
    
    def obtener_todos():
        alertas = Alerta.query.all()

        datos_req = ['id_alerta', 'id_paciente', 'fecha', 'alerta', 'frecuencia', 'sonido']

        respuesta = SerializadorUniversal.serializar_lista(alertas, datos_req)

        return respuesta 

    def obtener_por_paciente(paciente):
        alertas = Alerta.query.filter_by(id_paciente = paciente)

        datos_req = ['id_alerta', 'id_paciente', 'fecha', 'alerta', 'frecuencia', 'sonido']

        respuesta = SerializadorUniversal.serializar_lista(alertas, datos_req)

        return respuesta 
    
    def obtener_por_fecha(fecha):
        alertas = Alerta.query.all()

        alertas_mod = []

        for alerta in alertas:
            fecha_reg = alerta.fecha.strftime('%Y-%m-%d')
            if fecha == fecha_reg:
                alertas_mod.append(alerta)

        datos_req = ['id_alerta', 'id_paciente', 'fecha', 'alerta', 'frecuencia', 'sonido']

        respuesta = SerializadorUniversal.serializar_lista(alertas_mod, datos_req)

        return respuesta 
    
    def obtener_por_paciente_fecha(paciente, fecha):
        alertas = Alerta.query.filter_by(id_paciente = paciente, fecha = fecha)

        alertas_mod = []

        for alerta in alertas:
            fecha_reg = alerta.fecha.strftime('%Y-%m-%d')
            if fecha == fecha_reg:
                alertas_mod.append(alerta)

        datos_req = ['id_alerta', 'id_paciente', 'fecha', 'alerta', 'frecuencia', 'sonido']

        respuesta = SerializadorUniversal.serializar_lista(alertas_mod, datos_req)

        return respuesta 