from app.models.sonido import Sonido
from app.models.frecuencia import Frecuencia
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db
from sqlalchemy import func, desc
from datetime import datetime

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
        fecha = str(fecha)
        #fecha = datetime.strptime(fecha, '%Y-%m-%d')
        registros = Sonido.query.filter(Sonido.id_paciente == paciente).filter(func.date(Sonido.fecha) == func.date(fecha))

        print(fecha)
        print(int(paciente))
        print("imprimiendo registros: ")
        print(registros)

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
        ).order_by(desc(Frecuencia.fecha)).first()
        '''.order_by(
            func.abs(func.julianday(Frecuencia.fecha) - func.julianday(fecha_dada))  # Ordenar por la diferencia absoluta con la fecha dada
        )'''

        registro = SerializadorUniversal.serializar_unico(registro, ['id_frecuencia', 'id_clasificacion', 'valor'])
        
        if registro:
            registro = registro#[len(registro)-1]
        else:
            registro = None  # Seleccionamos el primer registro más cercano

        return registro
    
    def buscar_ultimo_registro(id_paciente):
        frecuencias = Frecuencia.query.filter(Frecuencia.id_paciente == id_paciente).order_by(Frecuencia.fecha.desc()).first()
        if frecuencias:
            return frecuencias
        else:
            return None
