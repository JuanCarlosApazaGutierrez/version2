from app.models.usuario import Usuario
from app.models.Rol import Rol
from app.serializer.serializadorUniversal import SerializadorUniversal
from app.config.extensiones import db
from werkzeug.security import generate_password_hash, check_password_hash

class ServiciosUsuario():
    def crear(nombre, correo, carnet, telefono, password, rol):
        usuario = Usuario(nombre, correo, carnet, telefono, generate_password_hash(password), rol)

        db.session.add(usuario)
        db.session.commit()

        return True 
    
    def obtener_todos():
        registros = Usuario.query.all()

        datos_req = ['id_usuario', 'nombre', 'correo', 'carnet', 'telefono', 'password', 'id_rol', 'activo']

        respuesta = SerializadorUniversal.serializar_lista(registros, datos_req)

        return respuesta
    
    def obtener_todos_padres():
        registros = Usuario.query.filter_by(id_rol=2).all()
        datos_req = ['id_usuario', 'nombre', 'correo', 'carnet', 'telefono', 'password', 'id_rol', 'activo']
        respuesta = SerializadorUniversal.serializar_lista(registros, datos_req)
        return respuesta


    def obtener_activos():
        registros = Usuario.query.filter_by(activo=1)

        datos_req = ['id_usuario', 'nombre', 'correo', 'carnet', 'telefono', 'password', 'id_rol', 'activo']

        respuesta = SerializadorUniversal.serializar_lista(registros, datos_req)

        return respuesta
    
    def obtener_id(id):
        registros = Usuario.query.get(id)

        datos_req = ['id_usuario', 'nombre', 'correo', 'carnet', 'telefono', 'password', 'id_rol', 'activo', 'token']

        respuesta = SerializadorUniversal.serializar_unico(registros, datos_req)

        return respuesta
    
    
    def obtener_por_carnet(carnet):
        registros = Usuario.query.filter_by(carnet = carnet).first()

        datos_req = ['id_usuario', 'nombre', 'correo', 'carnet', 'telefono', 'password', 'id_rol', 'activo']

        respuesta = SerializadorUniversal.serializar_unico(registros, datos_req)

        return respuesta
    
    def obtener_encargado(id_encargado):
        registros = Usuario.query.filter_by(id_usuario = id_encargado).first()

        datos_req = ['id_usuario', 'nombre', 'correo', 'carnet', 'telefono', 'password', 'id_rol', 'activo']

        respuesta = SerializadorUniversal.serializar_unico(registros, datos_req)

        return respuesta
    
    def obtener_por_correo(correo):
        registros = Usuario.query.filter_by(correo = correo).first()

        datos_req = ['id_usuario', 'nombre', 'correo', 'carnet', 'telefono', 'password', 'id_rol', 'activo']

        respuesta = SerializadorUniversal.serializar_unico(registros, datos_req)

        return respuesta
    
    def modificar(id, nombre = None, correo = None, carnet = None, telefono = None, rol = None):
        paciente = Usuario.query.get(id)

        if nombre:
            paciente.nombre = nombre
        if correo:
            paciente.correo = correo
        if carnet:
            paciente.carnet = carnet
        if telefono:
            paciente.telefono = telefono
        if rol:
            paciente.id_rol = rol

        
        db.session.commit()

        return True
    
    def modificar_contrasena(id, password):
        paciente = Usuario.query.get(id)

        paciente.password = generate_password_hash(password)

        
        db.session.commit()

        return True
    
    def activar(id):
        paciente = Usuario.query.get(id)

        paciente.activo = 1

        db.session.commit()

        return True
    
    def desactivar(id):
        paciente = Usuario.query.get(id)

        paciente.activo = 0

        db.session.commit()

        return True
    
    def obtener_usuarios_con_rol(rol_id):
        usuarios = db.session.query(Usuario, Rol).join(Rol).filter(Rol.id_rol == rol_id).all()
        
        resultados = []
        for usuario, rol in usuarios:
            resultados.append({
                'id_usuario': usuario.id_usuario,
                'nombre': usuario.nombre,
                'correo': usuario.correo,
                'carnet': usuario.carnet,
                'telefono': usuario.telefono,
                'rol': rol.nombre
            })
        
        return resultados
    
    def insertar_token(id, token):
        usuario = Usuario.query.get(id)
        if usuario:
            usuario.token = token
            db.session.commit()
            return True
        else:
            return False