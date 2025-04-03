from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db


class ServiciosPaciente():
    def crear(encargado, nacimiento, tasa, nombre, carnet, diagnostico = None, frecuencias = None):
        paciente = Paciente(encargado, nacimiento, tasa, nombre, carnet, frecuencias, diagnostico) 
        db.session.add(paciente)
        db.session.commit()

        return True
    
    def obtener_todos():
        pacientes = Paciente.query.all()

        datos_req = ['id_paciente', 'id_encargado', 'fecha_nacimiento', 'tasa', 'activo', 'nombre', 'carnet', 'diagnostico']

        respuesta = SerializadorUniversal.serializar_lista(pacientes, datos_req)

        return respuesta
    
    def obtener_activos():
        pacientes = Paciente.query.filter_by(activo = 1)

        datos_req = ['id_paciente', 'id_encargado', 'fecha_nacimiento', 'tasa', 'activo', 'nombre', 'carnet', 'diagnostico']

        respuesta = SerializadorUniversal.serializar_lista(pacientes, datos_req)

        return respuesta

    def obtener_por_carnet(carnet):

        paciente = Paciente.query.filter_by(carnet = carnet).first()

        datos_req = ['id_paciente', 'id_encargado', 'fecha_nacimiento', 'tasa', 'activo', 'nombre', 'carnet', 'diagnostico']

        respuesta = SerializadorUniversal.serializar_unico(paciente, datos_req)

        return respuesta
    
    def obtener_por_id(id):

        paciente = Paciente.query.get(id)

        datos_req = ['id_paciente', 'id_encargado', 'fecha_nacimiento', 'tasa', 'activo', 'nombre', 'carnet', 'diagnostico']

        respuesta = SerializadorUniversal.serializar_unico(paciente, datos_req)

        return respuesta
    
    def modificar(id, encargado = None, nacimiento = None, tasa = None, nombre = None, carnet = None, diagnostico = None, frecuencias = None):
        paciente = Paciente.query.get(id)

        if encargado:
            paciente.id_encargado = encargado
        if nacimiento:
            paciente.fecha_nacimiento = nacimiento
        if tasa:
            paciente.tasa = tasa
        if nombre:
            paciente.nombre = nombre
        if carnet:
            paciente.carnet = carnet
        if diagnostico:
            paciente.diagnostico = diagnostico
        if frecuencias:
            paciente.frecuencias = frecuencias
        
        db.session.commit()

        return True
    
    def activar(id):
        paciente = Paciente.query.get(id)

        paciente.activo = 1

        db.session.commit()

        return True
    
    def desactivar(id):
        paciente = Paciente.query.get(id)

        paciente.activo = 0

        db.session.commit()

        return True


    def obtener_pacientes_con_encargado():
        pacientes = db.session.query(
            Paciente.id_paciente,
            Paciente.fecha_nacimiento,
            Paciente.frecuencias,
            Paciente.tasa,
            Paciente.activo,
            Paciente.nombre,
            Paciente.carnet,
            Paciente.diagnostico,
            Usuario.nombre.label('encargado'),
            Usuario.correo,
            Usuario.telefono,
            Usuario.id_usuario
        ).join(Usuario, Paciente.id_encargado == Usuario.id_usuario).all()

        # Retornar los resultados como lista de diccionarios para facilidad
        resultados = []
        for paciente in pacientes:
            resultados.append({
                'id_paciente': paciente.id_paciente,
                'fecha_nacimiento': paciente.fecha_nacimiento,
                'frecuencias': paciente.frecuencias,
                'tasa': paciente.tasa,
                'activo': paciente.activo,
                'nombre': paciente.nombre,
                'carnet': paciente.carnet,
                'diagnostico': paciente.diagnostico,
                'encargado': paciente.encargado,
                'correo': paciente.correo,
                'telefono': paciente.telefono,
                'id_usuario': paciente.id_usuario
            })

        return resultados
    

        
    def obtener_pacientes_con_encargado_empleado(id_encargado):
        pacientes = db.session.query(
            Paciente.id_paciente,
            Paciente.fecha_nacimiento,
            Paciente.frecuencias,
            Paciente.tasa,
            Paciente.activo,
            Paciente.nombre,
            Paciente.carnet,
            Paciente.diagnostico,
            Usuario.nombre.label('encargado'),
            Usuario.correo,
            Usuario.telefono,
            Usuario.id_usuario
        ).join(Usuario, Paciente.id_encargado == Usuario.id_usuario).filter(Paciente.id_encargado == id_encargado).all()  # Filtrar por id_encargado
    
        resultados = []
        for paciente in pacientes:
            resultados.append({
                'id_paciente': paciente.id_paciente,
                'fecha_nacimiento': paciente.fecha_nacimiento,
                'frecuencias': paciente.frecuencias,
                'tasa': paciente.tasa,
                'activo': paciente.activo,
                'nombre': paciente.nombre,
                'carnet': paciente.carnet,
                'diagnostico': paciente.diagnostico,
                'encargado': paciente.encargado,
                'correo': paciente.correo,
                'telefono': paciente.telefono,
                'id_usuario': paciente.id_usuario
            })

        return resultados
