from app.models.frecuencia import Frecuencia
from app.models.clasificacion import Clasificacion
from app.models.paciente import Paciente
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db
from datetime import datetime
from sqlalchemy import func, extract, desc, case

class ServiciosFrecuencia():
    def crear(paciente, ritmo, clasificacion, valor, estado=None):
        frecuencia = Frecuencia(paciente, ritmo, clasificacion, valor, estado)

        db.session.add(frecuencia)
        db.session.commit()

        return True
    
    def modificar(id, clasificacion):
        frecuencia = Frecuencia.query.get(id)
        frecuencia.id_clasificacion = clasificacion
        db.session.commit()
        return frecuencia
    
    def obtener_todos():

        frecuencias = Frecuencia.query.all()

        datos_req = ['id_frecuencia','id_paciente', 'ritmo', 'id_clasificacion', 'valor', 'id_estado', 'activo', 'fecha']

        respuesta = SerializadorUniversal.serializar_lista(frecuencias, datos_req)

        return respuesta
    
    def obtener_por_paciente(paciente):
        frecuencias = Frecuencia.query.filter_by(id_paciente = paciente)

        datos_req = ['id_frecuencia','id_paciente', 'ritmo', 'id_clasificacion', 'valor', 'id_estado', 'activo', 'fecha']

        respuesta = SerializadorUniversal.serializar_lista(frecuencias, datos_req)

        return respuesta
    
    def obtener_por_fecha(fecha):
        frecuencias = Frecuencia.query.filter_by(fecha = fecha)

        respuestas_mod = []

        for fila in frecuencias:
            fecha_reg = fila.fecha.strftime('%Y-%m-%d')
            if fecha == fecha_reg:
                respuestas_mod.append(fila)

        datos_req = ['id_frecuencia','id_paciente', 'ritmo', 'id_clasificacion', 'valor', 'id_estado', 'activo', 'fecha']

        respuesta = SerializadorUniversal.serializar_lista(respuestas_mod, datos_req)

        return respuesta
    
    def obtener_por_paciente_fecha(paciente, fecha):
        frecuencias = Frecuencia.query.filter_by(id_paciente = paciente, fecha = fecha)
        
        respuestas_mod = []

        for fila in frecuencias:
            fecha_reg = fila.fecha.strftime('%Y-%m-%d')
            if fecha == fecha_reg:
                respuestas_mod.append(fila)

        datos_req = ['id_frecuencia','id_paciente', 'ritmo', 'id_clasificacion', 'valor', 'id_estado', 'activo', 'fecha']

        respuesta = SerializadorUniversal.serializar_lista(respuestas_mod, datos_req)

        return respuesta

    def obtener_frecuencias_por_paciente_y_fecha(id_paciente, fecha):
        # Convertir la fecha a formato datetime si no lo es
        fecha = str(fecha)
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')  # Suponiendo que la fecha es un string con formato YYYY-MM-DD

        # Realizar la consulta
        frecuencias = db.session.query(
            Frecuencia.id_frecuencia,
            Frecuencia.ritmo,
            Frecuencia.valor,
            Frecuencia.fecha,
            Clasificacion.nombre.label('clasificacion')
        ).join(Clasificacion, Frecuencia.id_clasificacion == Clasificacion.id_clasificacion) \
        .filter(Frecuencia.id_paciente == id_paciente) \
        .filter(func.date(Frecuencia.fecha) == func.date(fecha_obj)) \
        .order_by(Frecuencia.fecha).all()

        # Retornar los resultados como lista de diccionarios para facilidad
        resultados = []
        for frecuencia in frecuencias:
            resultados.append({
                'id_frecuencia': frecuencia.id_frecuencia,
                'ritmo': frecuencia.ritmo,
                'valor': frecuencia.valor,
                'fecha': frecuencia.fecha,
                'clasificacion': frecuencia.clasificacion
            })

        return resultados
    

    def obtener_frecuencias_por_paciente_mes_actual(id_paciente):
        current_year_month = datetime.now().strftime('%Y-%m') 
        frecuencias = db.session.query(
            Frecuencia.id_frecuencia,
            Frecuencia.ritmo,
            Frecuencia.valor,
            Frecuencia.fecha,
            Clasificacion.nombre,
            Clasificacion.id_clasificacion
        ).join(Clasificacion, Frecuencia.id_clasificacion == Clasificacion.id_clasificacion) \
        .filter(Frecuencia.id_paciente == id_paciente) \
        .filter(extract('year', Frecuencia.fecha) == datetime.now().year) \
        .filter(extract('month', Frecuencia.fecha) == datetime.now().month) \
        .all()

        resultados = []
        for frecuencia in frecuencias:
            resultados.append({
                'id_frecuencia': frecuencia.id_frecuencia,
                'ritmo': frecuencia.ritmo,
                'valor': frecuencia.valor,
                'fecha': frecuencia.fecha,
                'clasificacion': frecuencia.nombre,
                'id_clasificacion': frecuencia.id_clasificacion
            })

        return resultados
    

    def obtener_frecuencias_por_paciente_dia_especifico(id_paciente, fecha_dia):
        if isinstance(fecha_dia, str):
            fecha_dia = datetime.strptime(fecha_dia, "%Y-%m-%d")  

        frecuencias = db.session.query(
            Frecuencia.id_frecuencia,
            Frecuencia.ritmo,
            Frecuencia.valor,
            Frecuencia.fecha,
            Clasificacion.nombre,
            Clasificacion.id_clasificacion
        ).join(Clasificacion, Frecuencia.id_clasificacion == Clasificacion.id_clasificacion) \
        .filter(Frecuencia.id_paciente == id_paciente) \
        .filter(extract('year', Frecuencia.fecha) == fecha_dia.year) \
        .filter(extract('month', Frecuencia.fecha) == fecha_dia.month) \
        .filter(extract('day', Frecuencia.fecha) == fecha_dia.day) \
        .all()

        resultados = []
        for frecuencia in frecuencias:
            resultados.append({
                'id_frecuencia': frecuencia.id_frecuencia,
                'ritmo': frecuencia.ritmo,
                'valor': frecuencia.valor,
                'fecha': frecuencia.fecha,
                'clasificacion': frecuencia.nombre,
                'id_clasificacion': frecuencia.id_clasificacion
            })

        return resultados
  

    def obtener_frecuencias_lista(id_paciente):
        frecuencias = db.session.query(
            Frecuencia.id_frecuencia,
            Frecuencia.ritmo,
            Frecuencia.valor,
            Frecuencia.fecha,
            Clasificacion.nombre,
            Clasificacion.id_clasificacion
        ).join(Clasificacion, Frecuencia.id_clasificacion == Clasificacion.id_clasificacion) \
        .filter(Frecuencia.id_paciente == id_paciente) \
        .order_by(desc(Frecuencia.fecha)) 
 
      
        resultados = []
        for frecuencia in frecuencias:
            resultados.append({
                'id_frecuencia': frecuencia.id_frecuencia,
                'ritmo': frecuencia.ritmo,
                'valor': frecuencia.valor,
                'fecha': frecuencia.fecha,
                'clasificacion': frecuencia.nombre,
                'id_clasificacion': frecuencia.id_clasificacion
            })
 
        return resultados
    
    def obtener_lista_fechas_recientes(id_paciente):
        paciente = Paciente.query.get(id_paciente)

        id_pac = paciente.id_paciente

        resultados = db.session.query(Frecuencia.fecha, func.count(Frecuencia.id_frecuencia).label('cantidad_registros'), func.sum(case((Frecuencia.id_clasificacion == 10, 1), else_=0)).label('cantidad_normal')).group_by(func.date(Frecuencia.fecha)).order_by(func.date(Frecuencia.fecha).desc()).all()

        datos_req = ['fecha', 'cantidad_registros', 'cantidad_normal']

        resultado = SerializadorUniversal.serializar_lista(datos=resultados, campos_requeridos=datos_req)

        for fila in resultado:
            cant_tot = int(fila['cantidad_registros'])
            cant_nrm = int(fila['cantidad_normal'])
            cant_alr = cant_tot - cant_nrm

            porcentaje_alr = (cant_alr / cant_tot) * 100

            porcentaje_alr = "{:.2f}".format(porcentaje_alr)

            fila['porcentaje_alertas'] = porcentaje_alr

            fila['fecha_m'] = fila['fecha'].strftime("%d/%m/%Y")
            fila['fecha_v'] = fila['fecha'].strftime("%Y-%m-%d")



        return resultado
