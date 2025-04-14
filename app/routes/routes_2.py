#SERVICIOS
from app.services.serviciosAlerta import ServiciosAlerta
from app.services.serviciosClasificacion import ServiciosClasificacion
from app.services.serviciosFrecuencia import ServiciosFrecuencia
from app.services.serviciosPaciente import ServiciosPaciente
from app.services.serviciosRol import ServiciosRol
from app.services.serviciosSonido import ServiciosSonido
from app.services.serviciosUsuario import ServiciosUsuario
from datetime import datetime
from flask import jsonify, request
from datetime import datetime
from collections import defaultdict

from flask import Blueprint, render_template, request, jsonify, make_response
 
#from app.routes.conexion import db, cursor
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
 
from flask import session
from flask import jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import re
routes = Blueprint("routes", __name__)

from functools import wraps
from flask import redirect, url_for, session, send_file
import requests
import os
import firebase_admin
from google.oauth2 import service_account
import google.auth.transport.requests


#services_account_file = os.path.join(os.getcwd(), 'app', 'routes', "freqcard-firebase-adminsdk-fbsvc-9423d81a63.json")
services_account_file = os.path.join('var', 'www', 'sistema_cardiaco', 'app', 'routes', "freqcard-firebase-adminsdk-fbsvc-9423d81a63.json")
#credentials = service_account.Credentials.from_service_account_file(services_account_file, scopes="https://www.googleapis.com/auth/cloud-plataform") # https://www.googleapis.com/auth/firebase.messaging
#default_app = firebase_admin.initialize_app()

def _get_access_token():

    credentials = service_account.Credentials.from_service_account_file(services_account_file, scopes=["https://www.googleapis.com/auth/firebase.messaging"])
    
    request = google.auth.transport.requests.Request()
 
    credentials.refresh(request)
    return credentials.token

FCM_URL = "https://fcm.googleapis.com/v1/projects/freqcard/messages:send"

def send_fcm_notification(device_token, title, body, frecuencia = 0, normal=True):
    headers = {
        "Authorization": 'Bearer ' + _get_access_token(),
        "Content-Type": "application/json"
    }
    # Se arma el mensaje base con el token
    message = {"token": device_token}
     
    if normal:
         # Enviar mensaje data-only para actualización en tiempo real
         message["data"] = {
             "heart_rate": str(frecuencia)
         }
    else:
         # Enviar mensaje con notificación para alerta (frecuencia anormal)
         message["notification"] = {
             "title": title,
             "body": body
         }
         # Si se desea, se puede incluir además el dato en el campo data
         message["data"] = {
             "heart_rate": str(frecuencia)
         }
    payload = {"message": message}
     
     
    '''payload = {
         "message": {
             "token" : device_token,
             "notification": {
                 "title": title,
                 "body": body
             }#,
             #"data": data or {}
         }
    }'''
    try:
         response = requests.post(FCM_URL, headers=headers, json=payload)
         print('/*/*'*100)
         print(response)
         print(response.json())
         return response.json()
    except requests.exceptions.RequestException as e:
         # Captura cualquier error relacionado con la solicitud (como problemas de red o problemas con la URL)
         print(f"Error en la solicitud: {e}")
         return {"error": "Error en la solicitud"}
 
    except ValueError as e:
         # Captura cualquier error relacionado con la conversión de la respuesta a JSON
         print(f"Error al convertir la respuesta a JSON: {e}")
         return {"error": "Error al procesar la respuesta JSON"}
 
    except Exception as e:
         # Captura cualquier otro error no esperado
         print(f"Ha ocurrido un error inesperado: {e}")
         return {"error": "Error inesperado"}
    
 

from flask import Flask, session, redirect, url_for, jsonify
def login_requerido(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if "usuario_id" not in session:  
            return redirect(url_for("routes.login"))  
        return f(*args, **kwargs)   
    return check_login

def obtener_estadisticas():
    pacientes = ServiciosFrecuencia.obtener_todos()  # Obtenemos la lista de pacientes (diccionarios)
    total_pacientes = len(pacientes) if pacientes else 0  # Número de pacientes
    print(pacientes)
    
    # Inicializamos los contadores
    normal = 0
    ladridos = 0
    bocinas = 0
    petardos = 0

    if pacientes:

        for paciente in pacientes:  # Iteramos sobre la lista de pacientes (diccionarios)
            if 'id_clasificacion' in paciente:  # Comprobamos si la clave 'id_clasificacion' existe
                frecuencia = paciente['id_clasificacion']  # Accedemos al valor de id_clasificacion
                # Comprobamos el valor de la clasificación y asignamos a los contadores
                if frecuencia in [6, 4, 5]:
                    ladridos += 1
                elif frecuencia in [1, 2, 3]:
                    bocinas += 1
                elif frecuencia in [9, 8, 7]:
                    petardos += 1
                else:
                    normal += 1

    # Calculamos los porcentajes
    porcentaje_normal = (normal / total_pacientes) * 100 if total_pacientes else 0
    porcentaje_ladridos = (ladridos / total_pacientes) * 100 if total_pacientes else 0
    porcentaje_bocinas = (bocinas / total_pacientes) * 100 if total_pacientes else 0
    porcentaje_petardos = (petardos / total_pacientes) * 100 if total_pacientes else 0

    return {
        'porcentaje_normal': round(porcentaje_normal, 2),
        'porcentaje_ladridos': round(porcentaje_ladridos, 2),
        'porcentaje_bocinas': round(porcentaje_bocinas, 2),
        'porcentaje_petardos': round(porcentaje_petardos, 2),
        'total_usuarios': len(ServiciosUsuario.obtener_todos()),  # Suponiendo que la cantidad de usuarios se obtiene así
        'total_pacientes': total_pacientes,
    }




@routes.route("/dashboard")
@login_requerido
def inicio():
    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    rol_usuario = session.get('rol')
    print('sssssss')
    print(nombre_usuario)
    total_pacientes = ServiciosPaciente.obtener_todos()
      
    ultimos_pacientes = total_pacientes[-5:] if total_pacientes else []
    total_padres = ServiciosUsuario.obtener_todos_padres()
    
    total_pacientes = len(total_pacientes) if total_pacientes else 0
    
    total_usuarios = ServiciosUsuario.obtener_todos()
    total_usuarios = len(total_usuarios) if total_usuarios else 0

    ultimos_padres = total_padres[-5:] if total_padres else []

    session['total_pacientes'] = total_pacientes
    session['total_usuarios'] = total_usuarios
    total_encargados = len(total_padres) if total_padres else 0
    estadisticas = obtener_estadisticas()
    print(estadisticas)
    if rol_usuario ==1:
        return render_template("index.html", nombre_usuario=nombre_usuario, total_usuarios=total_usuarios, total_pacientes=total_pacientes,
                                porcentaje_normal=estadisticas['porcentaje_normal'],
                                porcentaje_ladridos=estadisticas['porcentaje_ladridos'],
                                porcentaje_bocinas=estadisticas['porcentaje_bocinas'],
                                porcentaje_petardos=estadisticas['porcentaje_petardos'],
                                pacientes=ultimos_pacientes, 
                                padres=ultimos_padres,
                                total_encargados=total_encargados 
                                )
    else:
        return render_template("index_empleado.html", nombre_usuario=nombre_usuario, total_usuarios=total_usuarios, total_pacientes=total_pacientes,
                                porcentaje_normal=estadisticas['porcentaje_normal'],
                                porcentaje_ladridos=estadisticas['porcentaje_ladridos'],
                                porcentaje_bocinas=estadisticas['porcentaje_bocinas'],
                                porcentaje_petardos=estadisticas['porcentaje_petardos'],
                                pacientes=ultimos_pacientes, 
                                padres=ultimos_padres,
                                total_encargados=total_encargados 
                                )

@routes.route("/")
def pagina_inicio():
    return render_template("inicio.html")

@routes.route("/login", methods=["GET"])
def login():
    
    return render_template("login.html") 

 



 

@routes.route("/cerrar_sesion", methods=["POST"])
def cerrar_sesion():
    try:
        session.pop("usuario_id", None)
        return jsonify({"mensaje": "Cierre de sesión exitoso", "redirect": "/login"}), 200

    except Exception as e:
        return jsonify({"mensaje": f"Error en el cierre de sesión: {str(e)}"}), 500


from werkzeug.security import check_password_hash

@routes.route("/verificar_login", methods=["POST"])
def verificar_login():
    try:
        datos = request.get_json()
        correo = datos.get("correo")
        password = datos.get("password")
        print(correo)
        print(password)
        if not correo or not password:
            return jsonify({"mensaje": "Faltan datos"}), 400

        usuario = ServiciosUsuario.obtener_por_correo(correo)

        if not usuario or not check_password_hash(usuario['password'], password):
            return jsonify({"mensaje": "Correo o contraseña incorrectos"}), 401
        
        session['nombre'] = usuario['nombre']  
        session['usuario_id'] = usuario['id_usuario'] 
        session['correo'] = usuario['correo'] 
        session['rol'] = usuario['id_rol']  
        inicio_rol = usuario['id_rol']  
        
        if inicio_rol == 1:
            return jsonify({"mensaje": "Inicio de sesión exitoso", "redirect": "/dashboard"}), 200
        else:
            return jsonify({"mensaje": "Inicio de sesión exitoso", "redirect": "/pacientes_empleado"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"mensaje": f"Error en el inicio de sesión: {str(e)}"}), 500



# ------------------- USUARIOS -------------------
@routes.route("/usuarios")
@login_requerido
def usuarios():

    usuarios = ServiciosUsuario.obtener_todos()
    print(usuarios)

    '''cursor.execute("SELECT u.id_usuario, u.nombre, u.correo, u.activo, u.carnet, u.telefono, r.nombre AS rol FROM usuario u JOIN roles r ON u.id_rol = r.id_rol ")
    usuarios = cursor.fetchall()'''

    roles = ServiciosRol.obtener_todos()


    '''cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()'''


    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    total_pacientes = session.get('total_pacientes')
    total_usuarios = session.get('total_usuarios')
    return render_template("usuario.html", usuarios=usuarios, roles=roles,nombre_usuario=nombre_usuario, total_pacientes= total_pacientes, total_usuarios= total_usuarios)

 
@routes.route("/agregar_usuario", methods=["POST"])
@login_requerido
def agregar_usuario():
    import re
    datos = request.get_json()
    
    nombre = datos.get("nombre")
    correo = datos.get("correo")
    carnet = datos.get("carnet")
    telefono = datos.get("telefono")
    password = datos.get("password")
    id_rol = datos.get("rol")

    # Validar formato de correo
    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        return jsonify({"mensaje": "Correo electrónico inválido"}), 400

    # Validar si el correo ya existe
    usuario_existente_correo = ServiciosUsuario.obtener_por_correo(correo)
    if usuario_existente_correo:
        return jsonify({"mensaje": "Ya existe un usuario registrado con ese correo"}), 400

    # Validar si el carnet ya existe
    usuario_existente_carnet = ServiciosUsuario.obtener_por_carnet(carnet)
    if usuario_existente_carnet:
        return jsonify({"mensaje": "Ya existe un usuario registrado con ese carnet"}), 400

    # Si todo está bien, crear el nuevo usuario
    usuario_nuevo = ServiciosUsuario.crear(nombre, correo, carnet, telefono, password, id_rol)
    if usuario_nuevo:
        return jsonify({"mensaje": "Usuario agregado con éxito", "redirect": "/usuarios"}), 200
    else:
        return jsonify({"mensaje": "Error al agregar usuario"}), 500

        
@routes.route("/user/crear_usuario", methods=["POST"])
def crear_usuario_app():
    
        datos = request.get_json()

     
        
        carnet = datos.get("id")
        nombre = datos.get("name")
        edad = datos.get("age")
        nombreTutor = datos.get("rate")
        carnetTutor = datos.get("nombreTutor")
        telefonoTutor = datos.get("carnetTutor")
        correoTutor = datos.get("telefonoTutor")
        contrasena = datos.get("correoTutor")
        rate = datos.get("contrasena")

        hoy = datetime.today()

        # Restar los años de la edad a la fecha de hoy
        #fecha_nacimiento = hoy.replace(year=hoy.year - edad)

        # Verificar si ya pasó el cumpleaños este año
        # Si la fecha de nacimiento es después de la fecha actual, restamos un año adicional
        #if hoy.month < fecha_nacimiento.month or (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
        #    fecha_nacimiento = fecha_nacimiento.replace(year=hoy.year - edad - 1)

        #fecha_nacimiento = fecha_nacimiento.strftime('%Y-%m-%d')

        #paciente = ServiciosPaciente.crear(1, fecha_nacimiento, 0, nombre, carnet)

        fecha_nacimiento = datetime.strptime(edad, "%d/%m/%Y")
        fecha_nacimiento = fecha_nacimiento.strftime("%Y-%m-%d")
 
        print(nombreTutor)
        print(correoTutor)
        print(carnetTutor)
        print(telefonoTutor)
        print(contrasena)
         
 
        usuario_nuevo = ServiciosUsuario.crear(nombreTutor, correoTutor, carnetTutor, telefonoTutor, contrasena, 2)
 
        usuario_tutor = ServiciosUsuario.obtener_por_carnet(carnetTutor)
 
        id_usuario = usuario_tutor['id_usuario']
 
        paciente = ServiciosPaciente.crear(id_usuario, fecha_nacimiento, 0, nombre, carnet)

        

        if paciente:

            return jsonify({"mensaje": "Usuario agregado con éxito", "redirect": "/usuarios"}), 200
        else:
            return jsonify({"mensaje": "Error al agregar usuario"}), 500





@routes.route("/editar_usuario", methods=["POST"])
@login_requerido
def editar_usuario():
    datos = request.get_json()
    id_usuario = datos.get("id")
    nombre = datos.get("nombre")
    correo = datos.get("correo")
    carnet = datos.get("carnet")
    telefono = datos.get("telefono")
    
    if not all([id_usuario, nombre, correo, carnet, telefono]):
        return jsonify({"mensaje": "Faltan datos"}), 400
    
    usuario_editado = ServiciosUsuario.modificar(id_usuario, nombre=nombre, correo=correo, carnet=carnet, telefono=telefono)

     
    '''cursor.execute("""
        UPDATE usuario
        SET nombre = %s, correo = %s, carnet = %s, telefono = %s
        WHERE id_usuario = %s
    """, (nombre, correo, carnet, telefono, id_usuario))

    db.commit()'''

    return jsonify({"mensaje": "Usuario actualizado con éxito", "redirect": "/usuarios"})


@routes.route("/eliminar_usuario/<int:id_usuario>", methods=["POST"])
@login_requerido
def eliminar_usuario(id_usuario):

    usuario = ServiciosUsuario.obtener_id(id_usuario)

    '''cursor.execute("SELECT activo FROM usuario WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()'''

    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    
    estado_actual = usuario['activo']

    if estado_actual == 1:
        usuario_m = ServiciosUsuario.desactivar(id_usuario)
        mensaje = "Usuario desactivado con éxito"
    else:
        usuario_m = ServiciosUsuario.activar(id_usuario)
        mensaje = "Usuario activado con éxito"
    


    '''estado_actual = usuario['activo']
    nuevo_estado = 0 if estado_actual == 1 else 1   
    cursor.execute("UPDATE usuario SET activo = %s WHERE id_usuario = %s", (nuevo_estado, id_usuario))
    db.commit()'''

    '''if nuevo_estado == 0:
        mensaje = "Usuario desactivado con éxito"
    else:
        mensaje = "Usuario activado con éxito"'''

    return jsonify({"mensaje": mensaje, "redirect": "/usuarios"})

# ------------------- PACIENTES -------------------


@routes.route("/pacientes")
@login_requerido
def pacientes():
    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    pacientes_lista = ServiciosPaciente.obtener_pacientes_con_encargado()
    encargados_lista = ServiciosUsuario.obtener_usuarios_con_rol(2)
    pacientes_con_edad = []
    today = datetime.today()

    frecuencias = ServiciosFrecuencia.obtener_todos()
    frecuencias_por_paciente = {}

  
    for frecuencia in frecuencias:
        paciente_id = frecuencia['id_paciente']
        fecha_frecuencia = frecuencia['fecha']

        if paciente_id not in frecuencias_por_paciente or fecha_frecuencia > frecuencias_por_paciente[paciente_id]['fecha']:
            frecuencias_por_paciente[paciente_id] = frecuencia

    for paciente in pacientes_lista:
        fecha_nacimiento = paciente['fecha_nacimiento']
        edad = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        paciente['edad'] = edad

        # Añadir la última frecuencia registrada para el paciente
        paciente_id = paciente['id_paciente']
        ultima_frecuencia = frecuencias_por_paciente.get(paciente_id, None)

        if ultima_frecuencia:
            paciente['ultima_frecuencia'] = {
                'ritmo': ultima_frecuencia['ritmo'],
                'clasificacion': ultima_frecuencia['id_clasificacion'],
                'valor': ultima_frecuencia['valor'],
                'fecha': ultima_frecuencia['fecha']
            }
        else:
            paciente['ultima_frecuencia'] = None

        pacientes_con_edad.append(paciente)

    total_pacientes = session.get('total_pacientes')
    total_usuarios = session.get('total_usuarios')
    username = session.get('username', 'Usuario Invitado')

    return render_template("pacientes.html", 
                           nombre_usuario=nombre_usuario, 
                           pacientes=pacientes_con_edad, 
                           encargados=encargados_lista,
                           username=username, 
                           total_pacientes=total_pacientes, 
                           total_usuarios=total_usuarios)


@routes.route("/pacientes_empleado")
@login_requerido
def pacientes_empleado():
    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    id_encargado = session.get('usuario_id')
    pacientes_lista = ServiciosPaciente.obtener_pacientes_con_encargado_empleado(id_encargado)
    
    encargados_lista = ServiciosUsuario.obtener_usuarios_con_rol(2)

 
    
 
    pacientes_con_edad = []
    today = datetime.today()

    
    frecuencias = ServiciosFrecuencia.obtener_todos()
    frecuencias_por_paciente = {}

  
    for frecuencia in frecuencias:
        paciente_id = frecuencia['id_paciente']
        fecha_frecuencia = frecuencia['fecha']

        if paciente_id not in frecuencias_por_paciente or fecha_frecuencia > frecuencias_por_paciente[paciente_id]['fecha']:
            frecuencias_por_paciente[paciente_id] = frecuencia

    for paciente in pacientes_lista:
        fecha_nacimiento = paciente['fecha_nacimiento']
        edad = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        paciente['edad'] = edad

        # Añadir la última frecuencia registrada para el paciente
        paciente_id = paciente['id_paciente']
        ultima_frecuencia = frecuencias_por_paciente.get(paciente_id, None)

        if ultima_frecuencia:
            paciente['ultima_frecuencia'] = {
                'ritmo': ultima_frecuencia['ritmo'],
                'clasificacion': ultima_frecuencia['id_clasificacion'],
                'valor': ultima_frecuencia['valor'],
                'fecha': ultima_frecuencia['fecha']
            }
        else:
            paciente['ultima_frecuencia'] = None

        pacientes_con_edad.append(paciente)
    total_pacientes = session.get('total_pacientes')
    total_usuarios = session.get('total_usuarios')

    username = session.get('username', 'Usuario Invitado')
    return render_template("pacientes_empleado.html",nombre_usuario=nombre_usuario, pacientes=pacientes_con_edad, encargados=encargados_lista,username=username, total_pacientes= total_pacientes, total_usuarios=total_usuarios)


@routes.route("/agregar_paciente", methods=["POST"])
@login_requerido
def agregar_paciente():
    datos = request.get_json()
    id_encargado = datos.get("id_encargado")
    fecha_nacimiento = datos.get("fecha_nacimiento")
    tasa = "0"
    token_acceso = datos.get("token_acceso")   
    nombre = datos.get("nombre") 
    carnet = datos.get("carnet") 
    diagnostico = datos.get("diagnostico")  

    encargado = ServiciosUsuario.obtener_id(id_encargado)
    if not encargado:
        return jsonify({"mensaje": "El encargado no existe"}), 400
    
    paciente_existente = ServiciosPaciente.obtener_por_carnet(carnet)
    if paciente_existente:
        return jsonify({"mensaje": "Ya existe un paciente registrado con ese carnet"}), 400

    nuevo_paciente = ServiciosPaciente.crear(id_encargado, fecha_nacimiento, tasa, nombre, carnet, diagnostico)
    rol = session.get('rol')
    if rol == 1: 
        return jsonify({"mensaje": "Paciente agregado con éxito", "redirect": "/pacientes"}), 200
    else:
        return jsonify({"mensaje": "Paciente agregado con éxito", "redirect": "/pacientes_empleado"}), 200

@routes.route("/editar_paciente", methods=["POST"])
@login_requerido
def editar_paciente():
    datos = request.get_json()
    id_paciente = datos.get("id")
    id_encargado = datos.get("encargado")
    fecha_nacimiento = datos.get("fecha_nacimiento")
    tasa = datos.get("tasa")
    token_acceso = datos.get("token_acceso")
    nombre = datos.get("nombre")  
    carnet = datos.get("carnet")  
    diagnostico = datos.get("diagnostico") 

    encargado = ServiciosUsuario.obtener_id(id_encargado)

    '''cursor.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id_encargado,))
    if not cursor.fetchone():
        return jsonify({"mensaje": "El encargado no existe"}), 400'''
    
    if not encargado:
        return jsonify({"mensaje": "El encargado no existe"}), 400
    
    paciente = ServiciosPaciente.modificar(id_paciente, encargado=id_encargado, nacimiento=fecha_nacimiento, tasa=tasa, nombre=nombre, carnet=carnet, diagnostico=diagnostico)

    rol = session.get('rol')
    if rol == 1: 
        return jsonify({"mensaje": "Paciente actualizado con éxito", "redirect": "/pacientes"})
    else:
        return jsonify({"mensaje": "Paciente actualizado con éxito", "redirect": "/pacientes_empleado"}), 200


@routes.route("/eliminar_paciente/<int:id_paciente>", methods=["POST"])
@login_requerido
def eliminar_paciente(id_paciente):

    paciente = ServiciosPaciente.obtener_por_id(id_paciente)

    '''cursor.execute("SELECT activo FROM paciente WHERE id_paciente = %s", (id_paciente,))
    paciente = cursor.fetchone()'''

    if not paciente:
        return jsonify({"mensaje": "Paciente no encontrado"}), 404
    


    estado_actual = paciente['activo']

    '''if estado_actual == 1:


    nuevo_estado = 0 if estado_actual == 1 else 1   
    cursor.execute("UPDATE paciente SET activo = %s WHERE id_paciente = %s", (nuevo_estado, id_paciente))
    db.commit()'''

    if estado_actual == 1:
        paciente = ServiciosPaciente.desactivar(id_paciente)
        mensaje = "Paciente desactivado con éxito"
    else:
        paciente = ServiciosPaciente.activar(id_paciente)
        mensaje = "Paciente activado con éxito"

    rol = session.get('rol')
    if rol == 1: 
        return jsonify({"mensaje": mensaje, "redirect": "/pacientes"})
    else:
         return jsonify({"mensaje": mensaje, "redirect": "/pacientes_empleado"})

    

 

@routes.route("/cambiar_contrasena/<int:id_usuario>", methods=["POST"])
@login_requerido
def cambiar_contrasena(id_usuario):
    datos = request.get_json()
    nueva_contrasena = datos.get("nuevaContrasena")

    if not nueva_contrasena:
        return jsonify({"mensaje": "La nueva contraseña es requerida"}), 400

  
    #contrasena_hasheada = generate_password_hash(nueva_contrasena)

    usuario = ServiciosUsuario.modificar_contrasena(id_usuario, nueva_contrasena)

    '''cursor.execute("""
        UPDATE usuario
        SET password = %s
        WHERE id_usuario = %s
    """, (contrasena_hasheada, id_usuario)) 
    db.commit()'''

    return jsonify({"mensaje": "Contraseña cambiada con éxito", "redirect": "/usuarios"})


# ------------------- INFORMES -------------------
@routes.route("/informes")
@login_requerido
def informes():
    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    total_pacientes = session.get('total_pacientes')
    total_usuarios = session.get('total_usuarios')
    return render_template("informes.html", nombre_usuario=nombre_usuario, total_pacientes= total_pacientes, total_usuarios=total_usuarios)
 
@routes.route("/informes_empleado")
@login_requerido
def informes_empleado():
    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    total_pacientes = session.get('total_pacientes')
    total_usuarios = session.get('total_usuarios')
    #return render_template("informes_empleado.html", nombre_usuario=nombre_usuario, total_pacientes= total_pacientes, total_usuarios=total_usuarios)
        
    id_encargado = session.get('usuario_id')
    paciente = ServiciosPaciente.obtener_pacientes_con_encargado_empleado(id_encargado)
    paciente = paciente[0]
    id_paciente= paciente['id_paciente']
    nombre_paciente= paciente['nombre']
    carnet_paciente= paciente['carnet']
     
    frecuencias = ServiciosFrecuencia.obtener_frecuencias_lista(id_paciente)
     
    return render_template("informes_empleado.html",nombre_paciente=nombre_paciente, carnet_paciente=carnet_paciente, frecuencias=frecuencias, nombre_usuario=nombre_usuario, total_pacientes= total_pacientes, total_usuarios=total_usuarios)
 
#import locale
 
#locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

@routes.route("/buscar_frecuencia", methods=["POST"])
@login_requerido
def buscar_frecuencia():
    datos = request.get_json()
    paciente_codigo = datos.get("paciente")
    fecha = datos.get("fecha")
    
    if not paciente_codigo or not fecha:
        return jsonify({"mensaje": "Paciente y fecha son requeridos."}), 400

    try:
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"mensaje": "Formato de fecha incorrecto, debe ser 'YYYY-MM-DD'."}), 400
    
    paciente = ServiciosPaciente.obtener_por_carnet(paciente_codigo)
    encargado = paciente['id_encargado']
    dato_encargado = ServiciosUsuario.obtener_encargado(encargado)
    nombre_encargado= dato_encargado['nombre']
    carnet_encargado= dato_encargado['carnet']
    correo_encargado= dato_encargado['correo']
    if paciente is None:
        return jsonify({"mensaje": "Paciente no encontrado con ese código de carnet."}), 404

    if isinstance(paciente, dict):
        id_paciente = paciente['id_paciente']
        nombre_paciente = paciente['nombre']
    else:
        id_paciente = paciente[0]
        nombre_paciente = paciente[1]

    frecuencias = ServiciosFrecuencia.obtener_frecuencias_por_paciente_y_fecha(id_paciente, fecha)

    if not frecuencias:
        return jsonify({"mensaje": "No se encontraron registros de frecuencia."}), 404
    
    frecuencias_formateadas = []
    for frecuencia in frecuencias:
        fecha_formateada = frecuencia['fecha'].strftime("%a, %d %b %Y %H:%M:%S")
        frecuencia['fecha'] = fecha_formateada 
        frecuencia['nombre_paciente'] = nombre_paciente 
        frecuencias_formateadas.append(frecuencia)

    return jsonify({"frecuencias": frecuencias_formateadas, "nombre_encargado":nombre_encargado,"correo_encargado":correo_encargado,"carnet_encargado":carnet_encargado})


# ------------------- REPORTES -------------------
@routes.route("/reportes")
@login_requerido
def reportes():
    total_pacientes = session.get('total_pacientes')
    total_usuarios = session.get('total_usuarios')
    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    return render_template("reportes.html", nombre_usuario=nombre_usuario, total_pacientes=total_pacientes, total_usuarios=total_usuarios)
 
@routes.route("/reportes_empleado")
@login_requerido
def reportes_empleado():
    total_pacientes = session.get('total_pacientes')
    total_usuarios = session.get('total_usuarios')
    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    #return render_template("reportes_empleado.html", nombre_usuario=nombre_usuario, total_pacientes=total_pacientes, total_usuarios=total_usuarios)
    id_encargado = session.get('usuario_id')
    paciente = ServiciosPaciente.obtener_pacientes_con_encargado_empleado(id_encargado)
    paciente = paciente[0]
    id_paciente= paciente['carnet']
    return render_template("reportes_empleado.html", id_paciente=id_paciente, nombre_usuario=nombre_usuario, total_pacientes=total_pacientes, total_usuarios=total_usuarios)
 

@routes.route('/generar_reporte_mensual', methods=['POST'])
@login_requerido
def generar_reporte_mensual():
    paciente_codigo = request.form.get('paciente')
    
    if not paciente_codigo:
        return jsonify({"mensaje": "Código de paciente es requerido."}), 400
    
    paciente = ServiciosPaciente.obtener_por_carnet(paciente_codigo)

    if paciente is None:
        return jsonify({"mensaje": "Paciente no encontrado con ese código de carnet."}), 404

    if isinstance(paciente, dict):
        id_paciente = paciente['id_paciente']
        nombre_paciente = paciente['nombre']
    else:
        id_paciente = paciente[0]
        nombre_paciente = paciente[1]

    frecuencias = ServiciosFrecuencia.obtener_frecuencias_por_paciente_mes_actual(id_paciente)
    fecha_actual = datetime.now()
    meses = [(fecha_actual + timedelta(days=30 * i)).strftime("%Y-%m") for i in range(4)]
    
    data = {mes: {"bocinas": {"suma": 0, "contador": 0},
                  "ladridos": {"suma": 0, "contador": 0},
                  "petardos": {"suma": 0, "contador": 0}} for mes in meses}

    for frecuencia in frecuencias:
        if isinstance(frecuencia, dict):
            fecha = frecuencia['fecha']  
            id_clasificacion = frecuencia['id_clasificacion']
            valor = frecuencia['valor']
        else:
            fecha = frecuencia[3]
            id_clasificacion = frecuencia[5]
            valor = frecuencia[2]
        
        period = fecha.strftime("%Y-%m") if isinstance(fecha, datetime) else fecha
        
        if id_clasificacion in [1, 2, 3]:   
            categoria = "bocinas"
        elif id_clasificacion in [4, 5, 6]:   
            categoria = "ladridos"
        elif id_clasificacion in [7, 8, 9]:  
            categoria = "petardos"
        else:
            continue
        
        if period in data:
            data[period][categoria]["suma"] += valor
            data[period][categoria]["contador"] += 1

    resultado_final = []
    for mes in meses:
        bocinas_promedio = data[mes]["bocinas"]["suma"] / data[mes]["bocinas"]["contador"] if data[mes]["bocinas"]["contador"] > 0 else 0
        ladridos_promedio = data[mes]["ladridos"]["suma"] / data[mes]["ladridos"]["contador"] if data[mes]["ladridos"]["contador"] > 0 else 0
        petardos_promedio = data[mes]["petardos"]["suma"] / data[mes]["petardos"]["contador"] if data[mes]["petardos"]["contador"] > 0 else 0
        
        resultado_final.append({
            "period": mes,
            "bocinas": bocinas_promedio,
            "ladridos": ladridos_promedio,
            "petardos": petardos_promedio
        })
  
    return jsonify({"frecuencias": resultado_final})


@routes.route('/generar_reporte_diario', methods=['POST'])
@login_requerido
def generar_reporte_diario():
    paciente_codigo = request.form.get('paciente_dia')
    fecha_dia_str = request.form.get('fecha_dia')

    if not paciente_codigo:
        return jsonify({"mensaje": "Código de paciente es requerido."}), 400

    if not fecha_dia_str:
        return jsonify({"mensaje": "Fecha del día es requerida."}), 400

    paciente = ServiciosPaciente.obtener_por_carnet(paciente_codigo)
    if paciente is None:
        return jsonify({"mensaje": "Paciente no encontrado con ese código de carnet."}), 404

    if isinstance(paciente, dict):
        id_paciente = paciente['id_paciente']
        nombre_paciente = paciente['nombre']
    else:
        id_paciente = paciente[0]
        nombre_paciente = paciente[1]

    try:
        fecha_dia = datetime.strptime(fecha_dia_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"mensaje": "Formato de fecha no válido. Debe ser YYYY-MM-DD."}), 400

    frecuencias = ServiciosFrecuencia.obtener_frecuencias_por_paciente_dia_especifico(id_paciente, fecha_dia)

    if not frecuencias:
        return jsonify({"mensaje": f"No se encontraron frecuencias para el paciente en la fecha {fecha_dia}."}), 404

    frecuencias.sort(key=lambda x: x['fecha'] if isinstance(x, dict) else x[3])
    ultimos_registros = frecuencias[-20:]

   
    clasificaciones = {
        1: "ladridos",
        2: "ladridos",
        3: "ladridos",
        4: "bocinas",
        5: "bocinas",
        6: "bocinas",
      
        7: "petardos",
        8: "petardos",
        9: "petardos"
    }

    agrupados_por_periodo = defaultdict(lambda: {
        "period": None,
        "normales": None,
        "bocinas": None,
        "ladridos": None,
        "petardos": None
    })

    for frecuencia in ultimos_registros:
        if isinstance(frecuencia, dict):
            fecha = frecuencia['fecha']
            id_clasificacion = frecuencia['id_clasificacion']
            valor = frecuencia['valor']
        else:
            fecha = frecuencia[3]
            id_clasificacion = frecuencia[5]
            valor = frecuencia[2]

        if isinstance(fecha, datetime):
            periodo = fecha.strftime("%H:%M:%S")
        else:
            periodo = fecha[11:19]

        if id_clasificacion == 10:
            clasificacion_label = "normales"
        else:
            clasificacion_label = clasificaciones.get(id_clasificacion, "desconocido")

        if clasificacion_label not in ["normales", "bocinas", "ladridos", "petardos"]:
            continue

        agrupados_por_periodo[periodo]["period"] = periodo
        agrupados_por_periodo[periodo][clasificacion_label] = valor

    resultado_final = list(agrupados_por_periodo.values())

    return jsonify({
        "fecha_dia": fecha_dia.strftime('%Y-%m-%d'),
        "frecuencias": resultado_final
    })
# ------------------------------------------ -------------------------------------------------

FRECUENCIAS_NORMALES = {
    '0': [100, 160],
    '1': [90, 150],
    '2': [90, 150],
    '3': [80, 140],
    '4': [80, 140],
    '5': [80, 140],
    '6': [70, 120],
    '7': [70, 120],
    '8': [70, 120],
    '9': [70, 120],
    '10': [70, 120],
    '11': [70, 120],
    '12': [70, 120],
    '13': [70, 120],
    '14': [70, 120],
    '15': [70, 120]
}

@routes.route('/insertar_latido', methods=['POST'])
def set_latido():

    datos = request.get_json()
    id_user = datos.get('id_user')
    latido = float(datos.get('heart_rate'))
    fecha = datos.get('datetime')
    
    #date_object = datetime.strptime(fecha, "%a %b %d %H:%M:%S GMT%z %Y")

    paciente = ServiciosPaciente.obtener_por_id(id_user)
    id_pac = paciente['id_paciente']

    fecha_nacimiento = paciente['fecha_nacimiento']

    hoy = datetime.now()

    edad = hoy.year - fecha_nacimiento.year

    # Ajustar si la fecha actual aún no ha llegado al cumpleaños de este año
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    if edad >15:
        edad = 15

    limite_sup = FRECUENCIAS_NORMALES[str(edad)][1]
    limite_inf = FRECUENCIAS_NORMALES[str(edad)][0]

    frecuencia = ServiciosFrecuencia.crear(id_pac, 0, 10, latido)

    '''cursor.execute("""
        INSERT INTO latidos (id_paciente, latido)
        VALUES (%s, %s)
    """, (id_user, latido,))
    db.commit()'''

    if latido >limite_sup:

        id_enc = paciente['id_encargado']

        usuario = ServiciosUsuario.obtener_id(id_enc)


        '''cursor.execute("""
            SELECT * FROM paciente WHERE carnet = %s
        """, (id_user,))
        control = cursor.fetchone()  '''

        if usuario:
            token_user = usuario['token']
          
            titulo = "Frecuencia Alta Detectada"
            cuerpo = f"Frecuencia detectada de {latido} bpm"
            result = send_fcm_notification(token_user, titulo, cuerpo, latido, False)
            return jsonify(result), 200
        else:
            return jsonify({'message':'No hay token'}), 400
    elif latido <limite_inf:

        id_enc = paciente['id_encargado']

        usuario = ServiciosUsuario.obtener_id(id_enc)


        '''cursor.execute("""
            SELECT * FROM paciente WHERE carnet = %s
        """, (id_user,))
        control = cursor.fetchone()  '''

        if usuario:
            token_user = usuario['token']
          
            titulo = "Frecuencia Baja Detectada"
            cuerpo = f"Frecuencia detectada de {latido} bpm"
            result = send_fcm_notification(token_user, titulo, cuerpo, latido, False)
            return jsonify(result), 200
        else:
            return jsonify({'message':'No hay token'}), 400
    else:         
        id_enc = paciente['id_encargado']
        usuario = ServiciosUsuario.obtener_id(id_enc)
        if usuario:
            token_user = usuario['token']
            result = send_fcm_notification(token_user, '', '', latido, True)
            return jsonify(result), 200



    return jsonify({'message': 'Registrado Satisfactoriamente'}), 200

@routes.route('/control/send_notificacions', methods=['POST'])
def send_not():
    datos = request.get_json()
    id_user = datos.get('id_user')
    title = datos.get('title')
    description = datos.get('description')
    
    paciente = ServiciosPaciente.obtener_por_carnet(id_user)

    

    '''cursor.execute("""
            SELECT * FROM paciente WHERE id_paciente = %s
        """, (id_user,))
    control = cursor.fetchone()  '''

    if paciente:
        id_pac = paciente['id_paciente']
        id_enc = paciente['id_encargado']

        usuario = ServiciosUsuario.obtener_id(id_enc)

        token_user = usuario['token']
        
        titulo = title
        cuerpo = description
        result = ''
        result = send_fcm_notification(token_user, titulo, cuerpo, 0, True)
        return jsonify(result), 200
    else:
        return jsonify({'message':'No hay token'}), 200

    return jsonify({'message': 'Registrado Satisfactoriamente'}), 200

@routes.route('/insertar_tokens', methods=['POST'])
def set_tokens():
    datos = request.get_json()
    id_user = datos.get('id_user')
    
    token = datos.get('token')
     
    paciente = ServiciosPaciente.obtener_por_carnet(id_user)

    id_enc = paciente['id_encargado']

    #usuario = ServiciosUsuario.obtener_por_carnet(id_user)

    #id_usuario = usuario['id_usuario']

    usuario = ServiciosUsuario.insertar_token(id_enc, token)

    '''cursor.execute("""
        UPDATE paciente
        SET token_acceso = %s
        WHERE carnet = %s
    """, (token, id_user, ))
    db.commit()'''

    
    return jsonify({'message': 'Registrado Satisfactoriamente'}), 200



@routes.route('/insertar_sonido', methods=['POST'])
def set_sonido():
    datos = request.get_json()
    id_user = datos.get('id_user')
    
    sonido = datos.get('sound')
    fecha = datos.get('datetime')

    clasificacion = 10

    if sonido == 'bocina' or sonido=='sirena':
        clasificacion = 4
    elif sonido == 'ladrido':
        clasificacion = 1
    elif sonido == 'petardo':
        clasificacion = 7

    
    fecha =fecha.replace('GMT', '').strip()

    sonid = ServiciosSonido.crear(id_user, sonido)

    freq_cerc = 0

    if sonid:
        fecha_sonido = sonid.fecha
        #frecuencia_cercana = ServiciosSonido.buscar_registro_cercano(fecha_sonido, id_user)
        frecuencia_cercana = ServiciosSonido.buscar_ultimo_registro(id_paciente=id_user)
        if frecuencia_cercana:
            id_frecuecia = frecuencia_cercana['id_frecuencia']
            freq_cerc = int(float(frecuencia_cercana['valor']))
            resultado = ServiciosFrecuencia.modificar(id_frecuecia, clasificacion)


    #date_object = datetime.strptime(fecha, '%a %b %d %H:%M:%S %z %Y')
    
    '''cursor.execute("""
        INSERT INTO sonidos (id_paciente, sonido)
        VALUES (%s, %s)
    """, (id_user, sonido,))
    db.commit()'''

    paciente = ServiciosPaciente.obtener_por_id(id_user)

    '''cursor.execute("""
            SELECT * FROM paciente WHERE id_paciente = %s
        """, (id_user,))
    control = cursor.fetchone()  '''

    if paciente:
        id_enc = paciente['id_encargado']

        usuario = ServiciosUsuario.obtener_id(id_enc)

        token_user = usuario['token']
        
        titulo = "Ruido Molesto Detectado"
        cuerpo = f"Alerta de {sonido} cerca del paciente, frecuencia cardiaca de {freq_cerc}bpm"
        result = send_fcm_notification(token_user, titulo, cuerpo, freq_cerc, False)
        return jsonify(result), 200
    else:
        return jsonify({'message':'No hay token'}), 200

    return jsonify({'message': 'Registrado Satisfactoriamente'}), 200

@routes.route('/obtener_paciente', methods=['POST'])
def obtener_paciente():
    datos = request.get_json()
    id_usuario = datos.get("id")
  

    pacientes_lista = ServiciosPaciente.obtener_por_carnet(id_usuario)

    id_tutor = pacientes_lista['id_encargado']
 
    tutor = ServiciosUsuario.obtener_id(id_tutor)

    '''cursor.execute("""
        SELECT * FROM paciente WHERE paciente.carnet = %s
    """, (id_usuario, ))
    pacientes_lista = cursor.fetchone()'''
    
    today = datetime.today()
    fecha_nacimiento = pacientes_lista['fecha_nacimiento']
        # Calcular la edad
    edad = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    pacientes_lista['edad'] = edad  
    cuerpo = {
        'id': pacientes_lista['id_paciente'],
        'age' : pacientes_lista['edad'],
        'name' : pacientes_lista['nombre'],
        'rate' : pacientes_lista['carnet'],
        'carnet': pacientes_lista['carnet'],
        'fecha_nacimiento': pacientes_lista['fecha_nacimiento'].strftime("%d/%m/%Y")
    }

    return jsonify({'results' : [cuerpo]})





import matplotlib
matplotlib.use('Agg')  # Usa el backend no interactivo
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.axes import CategoryAxis, ValueAxis
from reportlab.platypus import SimpleDocTemplate
import queue
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image as RLImage, Paragraph
from io import BytesIO
@routes.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    id_paciente = request.args.get("id_paciente") # es ID no carnet
    print(id_paciente)

    id_pac_aux = id_paciente.find('?')
    id_pac_aux = str(id_pac_aux)[0:id_pac_aux]
    print(id_pac_aux)

    paciente = ServiciosPaciente.obtener_por_id(id_paciente)

    id_tutor = paciente['id_encargado']

    tutor = ServiciosUsuario.obtener_id(id_tutor)

    fecha_actual = datetime.now()
    #fecha_actual = fecha_actual - timedelta(days=3)
    fecha_actual = fecha_actual.strftime("%Y-%m-%d")
    print(fecha_actual)

    frecuencias = ServiciosFrecuencia.obtener_frecuencias_por_paciente_y_fecha(id_paciente, fecha_actual)
    sonidos = ServiciosSonido.obtener_por_paciente_fecha(id_paciente, fecha_actual)

    fecha_nacimiento = paciente['fecha_nacimiento']

    hoy = datetime.now()

    edad = hoy.year - fecha_nacimiento.year

    # Ajustar si la fecha actual aún no ha llegado al cumpleaños de este año
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    if edad >15:
        edad = 15

    limite_sup = FRECUENCIAS_NORMALES[str(edad)][1]
    limite_inf = FRECUENCIAS_NORMALES[str(edad)][0]



    fechas_h = []
    frecuencias_h = []
    if frecuencias:
        for frec in frecuencias:
            fecha_ac = frec['fecha'].strftime("%Y-%m-%d %H:%M:%S")
            #fecha_ac = fecha_ac.split(' ')[1]
            fecha_ac = datetime.strptime(fecha_ac, "%Y-%m-%d %H:%M:%S")
            fechas_h.append(fecha_ac)

            frecuencias_h.append(float(frec['valor']))
    

    
    fig, ax = plt.subplots()  # Crea un único eje
    ax.plot(fechas_h, frecuencias_h, marker='o', linestyle='-')
    ax.set_xlabel("Tiempo (HH:MM:SS)")
    ax.set_ylabel("Frecuencia Cardiaca (bpm)")
    ax.set_title("Frecuencia Cardiaca a lo largo del tiempo")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()  # Rota las etiquetas del eje x para mejor visualización

    buf = io.BytesIO()
    plt.savefig(buf, format='PNG')
    plt.close(fig)
    buf.seek(0)
    imagen_grafica = RLImage(buf, width=500, height=250)
    #imagen = ImageReader(buf)


    #print(f"id_paciente: {id_paciente}")
    # Crea un buffer en memoria para el PDF



    buffer = BytesIO()


    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('Titulo', fontSize=18, alignment=1, fontName="Helvetica-Bold", underline=True)
    estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  # Para el nombre de usuario y fecha
    estilo_tabla_paragrah = ParagraphStyle('Normala', fontSize=7, alignment=0)
    estilo_datos = estilos['Normal']

    #logo_direccion = os.path.join(os.getcwd(),'app', 'routes', 'logo.png')
    logo_direccion = os.path.join('var', 'www', 'sistema_cardiaco','app', 'routes', 'logo.png')
    print(logo_direccion)

    # Agregar logo del hospital
    #logo = "logo.png"  # Ruta al logo
    imagen_logo = Image(logo_direccion, 2 * inch, 1 * inch)  # Ajustar el tamaño del logo
    #imagen_logo.hAlign = 'LEFT'
    #elementos.append(imagen_logo)


    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    generado_por = Paragraph(f"<b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo)
    #generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}", estilo_subtitulo)
    #generado_por = f"<b>Generado por:</b> {nombre_usuario}"

    #elementos.append(generado_por)
    #tabla_encabezado = Table([[imagen_logo, generado_por]], colWidths=[4 * inch, 4 * inch])
    #elementos.append(tabla_encabezado)
    def add_header(canvas, doc):
        width, height = letter
        imagen_logo.drawOn(canvas, (0.5*inch), height - (0.5*inch) - imagen_logo.drawHeight)
        #tabla_encabezado.drawOn(canvas, (0.5*inch), height - (0.5*inch) - imagen_logo.drawHeight)
            
        # Obtener el ancho del texto
        #ancho_texto = canvas.stringWidth(generado_por, "Helvetica", 12)
            
        # Posicionar el texto a una pulgada del margen derecho
        posicion_texto_x = (0.3*inch)
        posicion_texto_y = (0.3*inch)
        generado_por.wrapOn(canvas, width, height)
            
        # Dibujar el texto
        generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)
        #canvas.drawString(posicion_texto_x, posicion_texto_y, generado_por)

    # Espacio entre elementos
    elementos.append(Spacer(1, 12))

    # Título del documento centrado y subrayado
    titulo = Paragraph("<u>Informe del Paciente</u>", estilo_titulo)
    elementos.append(titulo)

    # Espacio antes de los datos personales
    elementos.append(Spacer(1, 20))

    datos_paciente = Table([[Paragraph(f"<b>Nombres y Apellidos del Paciente:</b> {paciente['nombre']}", estilo_datos), '', ''],
                            [Paragraph(f"<b>Carnet:</b> {paciente['carnet']}", estilo_datos), Paragraph(f"<b>Fecha de Nacimiento:</b> {paciente['fecha_nacimiento']}", estilo_datos), Paragraph(f"<b></b>", estilo_datos)],
                            [Paragraph(f"<b>Nombres Tutor:</b> {tutor['nombre']}", estilo_datos), Paragraph(f"<b>Carnet:</b> {tutor['carnet']}", estilo_datos), Paragraph(f"<b>Telefono:</b> {tutor['telefono']}", estilo_datos)]])

    datos_paciente.setStyle(TableStyle([('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
                                        ('SPAN',(0,0),(2,0)),]))
    #nombres_paciente = Paragraph(f"<b>Nombres y Apellidos del Paciente:</b> {hoja['nombres']} {hoja['apellido_paterno']} {hoja['apellido_materno']}", estilo_datos)
       
    #elementos.append(nombres_paciente)
    elementos.append(datos_paciente)

    # Espacio antes de la tabla
    elementos.append(Spacer(1, 20))

    clasificaciones = ServiciosClasificacion.obtener_todos()
    #print(clasificaciones)

    cabecera = ['Fecha y Hora', 'Frecuencia', 'Estado del Niño', 'Irregularidad Cardiaca', 'Irregularidad Cardiaca (%)']
    cabecera_an = ['Fecha y Hora', 'Frecuencia', 'Estado']

    tabla_an = []
    tabla_an.append(cabecera_an)

    tabla = []
    tabla.append(cabecera)

    if frecuencias:

        indice = 0
        
        for frec in frecuencias:
            indice = indice + 1
            print(frec)
            fila_an = []
            if float(frec['valor'])>limite_sup:
                fila_an = [frec['fecha'], frec['valor'], 'Frecuencia Alta']
                tabla_an.append(fila_an)
            elif float(frec['valor'])<limite_inf:
                fila_an = [frec['fecha'], frec['valor'], 'Frecuencia Baja']
                tabla_an.append(fila_an)
            fila = []
            fila.append(frec['fecha'])
            fila.append(frec['valor'])
            '''soni = ""
            for clas in clasificaciones:
                if frec['id_clasificacion']==clas['id_clasificacion']:
                    soni = clas['nombre']
                    break'''
            
            #fila.append(frec['clasificacion'])
            if float(frec['valor'])>limite_sup and frec['clasificacion']=='Estado Normal':
                fila.append('Frecuencia Alta')
            elif float(frec['valor'])<limite_inf and frec['clasificacion']=='Estado Normal':
                fila.append('Frecuencia Baja')
            else:
                fila.append(frec['clasificacion'])
            if indice > 1:
                diferencia_frec = float(frec['valor']) - float(tabla[indice-1][1])
                diferencia_porc = diferencia_frec / float(tabla[indice-1][1])

                if diferencia_frec > 0.0:
                    fila.append(f'+ {diferencia_frec:.1f}')
                    fila.append(f'+ {diferencia_porc:.3f} %')
                else:
                    fila.append(f'{diferencia_frec:.1f}')
                    fila.append(f'{diferencia_porc:.3f} %')

                
            else:
                fila.append('0.0')
                fila.append('0.000 %')

                
            tabla.append(fila)
    
    cabecera = ['Fecha y Hora', 'Sonido']
    tabla_son = []
    tabla_son.append(cabecera)

    if sonidos:
        
        for frec in sonidos:
            fila = []
            fila.append(frec['fecha'])
            fila.append(frec['sonido'])
            
            tabla_son.append(fila)
    else:
        tabla_son.append(['Sin Sonidos Registrados', ''])
    
    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # color de texto en la primera fila
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación de texto (centrado)
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Negrita en la primera fila (encabezados)
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Fuente normal para el resto
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding en la primera fila
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris para la primera fila
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Mostrar líneas de la tabla
    ])

    if len(tabla_an)==1:
        tabla_an.append(['','Sin Anomalías',''])
    

    estilo_titulos_tablas = ParagraphStyle('Titulo_tabla', fontSize=15, alignment=1, fontName="Helvetica-Bold")
    elementos.append(Spacer(1, 20))
    tabla_frecuencias = Table(tabla)
    tabla_frecuencias.setStyle(style)
    elementos.append(Paragraph(f"Frecuencias Cardiacas con Irregularidades", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    elementos.append(tabla_frecuencias)

    elementos.append(Spacer(1, 35))
    elementos.append(Paragraph(f"Anomalías del Ruido Ambiente", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    tabla_sonidos = Table(tabla_son)
    tabla_sonidos.setStyle(style)
    elementos.append(tabla_sonidos)

    elementos.append(Spacer(1, 35))
    tabla_anomalias = Table(tabla_an)
    tabla_anomalias.setStyle(style)
    elementos.append(Paragraph(f"Anomalías en la Frecuencia Cardiaca", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    elementos.append(tabla_anomalias)

    elementos.append(Spacer(1, 20))

    elementos.append(imagen_grafica)
    elementos.append(Spacer(1, 60))
    firmas = Table([
        ['_____________________________', '_____________________________'],
        [f'{tutor["nombre"]}', 'Encargado del Centro Psicolegria'],
        ['Encargado o Padre','']
    ])

    firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))
    elementos.append(firmas)


    # Generar el PDF  ----------------  pdf.build(elementos)
    pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="informe.pdf", mimetype='application/pdf')

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response
    return buffer
        














    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    # Aquí defines el contenido del PDF
    p.drawString(100, 750, "Este es tu reporte PDF generado con ReportLab")
    p.drawString(100, 730, "¡Generado desde Flask!")
    p.showPage()
    p.save()
    buffer.seek(0)
     
    # Configura la respuesta con los headers adecuados para PDF
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response
 
 
 
@routes.route('/generate_pdf2', methods=['GET'])
def generate_pdf2():
    codigo = request.args.get("id_paciente") # es ID no carnet
    print(codigo)

    id_pac_aux = codigo.find('?')
    id_pac_aux = str(id_pac_aux)[0:id_pac_aux]
    print(id_pac_aux)

    paciente = ServiciosPaciente.obtener_por_carnet(codigo)
    id_paciente = paciente['id_paciente']
    id_tutor = paciente['id_encargado']

    tutor = ServiciosUsuario.obtener_id(id_tutor)

    fecha_actual = datetime.now()
    #fecha_actual = fecha_actual - timedelta(days=3)
    fecha_actual = fecha_actual.strftime("%Y-%m-%d")
    print(fecha_actual)

    frecuencias = ServiciosFrecuencia.obtener_frecuencias_por_paciente_y_fecha(id_paciente, fecha_actual)
    sonidos = ServiciosSonido.obtener_por_paciente_fecha(id_paciente, fecha_actual)

    fecha_nacimiento = paciente['fecha_nacimiento']

    hoy = datetime.now()

    edad = hoy.year - fecha_nacimiento.year

    # Ajustar si la fecha actual aún no ha llegado al cumpleaños de este año
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    if edad >15:
        edad = 15

    limite_sup = FRECUENCIAS_NORMALES[str(edad)][1]
    limite_inf = FRECUENCIAS_NORMALES[str(edad)][0]



    fechas_h = []
    frecuencias_h = []
    if frecuencias:
        for frec in frecuencias:
            fecha_ac = frec['fecha'].strftime("%Y-%m-%d %H:%M:%S")
            #fecha_ac = fecha_ac.split(' ')[1]
            fecha_ac = datetime.strptime(fecha_ac, "%Y-%m-%d %H:%M:%S")
            fechas_h.append(fecha_ac)

            frecuencias_h.append(float(frec['valor']))
    

    
    fig, ax = plt.subplots()  # Crea un único eje
    ax.plot(fechas_h, frecuencias_h, marker='o', linestyle='-')
    ax.set_xlabel("Tiempo (HH:MM:SS)")
    ax.set_ylabel("Frecuencia Cardiaca (bpm)")
    ax.set_title("Frecuencia Cardiaca a lo largo del tiempo")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()  # Rota las etiquetas del eje x para mejor visualización

    buf = io.BytesIO()
    plt.savefig(buf, format='PNG')
    plt.close(fig)
    buf.seek(0)
    imagen_grafica = RLImage(buf, width=500, height=250)
    #imagen = ImageReader(buf)


    #print(f"id_paciente: {id_paciente}")
    # Crea un buffer en memoria para el PDF
    
     

    buffer = BytesIO()


    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('Titulo', fontSize=18, alignment=1, fontName="Helvetica-Bold", underline=True)
    estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  # Para el nombre de usuario y fecha
    estilo_tabla_paragrah = ParagraphStyle('Normala', fontSize=7, alignment=0)
    estilo_datos = estilos['Normal']

    #logo_direccion = os.path.join(os.getcwd(),'app', 'routes', 'logo.png')
    logo_direccion = os.path.join('var', 'www', 'sistema_cardiaco','app', 'routes', 'logo.png')
    #print(logo_direccion)

    # Agregar logo del hospital
    logo = "logo.png"  # Ruta al logo
    imagen_logo = Image(logo_direccion, 2 * inch, 1 * inch)  # Ajustar el tamaño del logo
    #imagen_logo.hAlign = 'LEFT'
    #elementos.append(imagen_logo)


    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    generado_por = Paragraph(f"<b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo)
    #generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}", estilo_subtitulo)
    #generado_por = f"<b>Generado por:</b> {nombre_usuario}"

    #elementos.append(generado_por)
    #tabla_encabezado = Table([[imagen_logo, generado_por]], colWidths=[4 * inch, 4 * inch])
    #elementos.append(tabla_encabezado)
    def add_header(canvas, doc):
        width, height = letter
        imagen_logo.drawOn(canvas, (0.5*inch), height - (0.5*inch) - imagen_logo.drawHeight)
        #tabla_encabezado.drawOn(canvas, (0.5*inch), height - (0.5*inch) - imagen_logo.drawHeight)
            
        # Obtener el ancho del texto
        #ancho_texto = canvas.stringWidth(generado_por, "Helvetica", 12)
            
        # Posicionar el texto a una pulgada del margen derecho
        posicion_texto_x = (0.3*inch)
        posicion_texto_y = (0.3*inch)
        generado_por.wrapOn(canvas, width, height)
            
        # Dibujar el texto
        generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)
        #canvas.drawString(posicion_texto_x, posicion_texto_y, generado_por)

    # Espacio entre elementos
    elementos.append(Spacer(1, 12))

    # Título del documento centrado y subrayado
    titulo = Paragraph("<u>Informe del Paciente</u>", estilo_titulo)
    elementos.append(titulo)

    # Espacio antes de los datos personales
    elementos.append(Spacer(1, 20))

    datos_paciente = Table([[Paragraph(f"<b>Nombres y Apellidos del Paciente:</b> {paciente['nombre']}", estilo_datos), '', ''],
                            [Paragraph(f"<b>Carnet:</b> {paciente['carnet']}", estilo_datos), Paragraph(f"<b>Fecha de Nacimiento:</b> {paciente['fecha_nacimiento']}", estilo_datos), Paragraph(f"<b></b>", estilo_datos)],
                            [Paragraph(f"<b>Nombres Tutor:</b> {tutor['nombre']}", estilo_datos), Paragraph(f"<b>Carnet:</b> {tutor['carnet']}", estilo_datos), Paragraph(f"<b>Telefono:</b> {tutor['telefono']}", estilo_datos)]])

    datos_paciente.setStyle(TableStyle([('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
                                        ('SPAN',(0,0),(2,0)),]))
    #nombres_paciente = Paragraph(f"<b>Nombres y Apellidos del Paciente:</b> {hoja['nombres']} {hoja['apellido_paterno']} {hoja['apellido_materno']}", estilo_datos)
       
    #elementos.append(nombres_paciente)
    elementos.append(datos_paciente)

    # Espacio antes de la tabla
    elementos.append(Spacer(1, 20))

    clasificaciones = ServiciosClasificacion.obtener_todos()
    #print(clasificaciones)

    cabecera = ['Fecha y Hora', 'Frecuencia', 'Estado del Niño', 'Irregularidad Cardiaca', 'Irregularidad Cardiaca (%)']
    cabecera_an = ['Fecha y Hora', 'Frecuencia', 'Estado']

    tabla_an = []
    tabla_an.append(cabecera_an)

    tabla = []
    tabla.append(cabecera)

    if frecuencias:

        indice = 0
        
        for frec in frecuencias:
            indice = indice + 1
            print(frec)
            fila_an = []
            if float(frec['valor'])>limite_sup:
                fila_an = [frec['fecha'], frec['valor'], 'Frecuencia Alta']
                tabla_an.append(fila_an)
            elif float(frec['valor'])<limite_inf:
                fila_an = [frec['fecha'], frec['valor'], 'Frecuencia Baja']
                tabla_an.append(fila_an)
            fila = []
            fila.append(frec['fecha'])
            fila.append(frec['valor'])
            '''soni = ""
            for clas in clasificaciones:
                if frec['id_clasificacion']==clas['id_clasificacion']:
                    soni = clas['nombre']
                    break'''
            
            #fila.append(frec['clasificacion'])
            if float(frec['valor'])>limite_sup and frec['clasificacion']=='Estado Normal':
                fila.append('Frecuencia Alta')
            elif float(frec['valor'])<limite_inf and frec['clasificacion']=='Estado Normal':
                fila.append('Frecuencia Baja')
            else:
                fila.append(frec['clasificacion'])
            if indice > 1:
                diferencia_frec = float(frec['valor']) - float(tabla[indice-1][1])
                diferencia_porc = diferencia_frec / float(tabla[indice-1][1])

                if diferencia_frec > 0.0:
                    fila.append(f'+ {diferencia_frec:.1f}')
                    fila.append(f'+ {diferencia_porc:.3f} %')
                else:
                    fila.append(f'{diferencia_frec:.1f}')
                    fila.append(f'{diferencia_porc:.3f} %')

                
            else:
                fila.append('0.0')
                fila.append('0.000 %')

                
            tabla.append(fila)
    
    cabecera = ['Fecha y Hora', 'Sonido']
    tabla_son = []
    tabla_son.append(cabecera)

    if sonidos:
        
        for frec in sonidos:
            fila = []
            fila.append(frec['fecha'])
            fila.append(frec['sonido'])
            
            tabla_son.append(fila)
    else:
        tabla_son.append(['Sin Sonidos Registrados', ''])
    
    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # color de texto en la primera fila
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación de texto (centrado)
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Negrita en la primera fila (encabezados)
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Fuente normal para el resto
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding en la primera fila
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris para la primera fila
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Mostrar líneas de la tabla
    ])

    if len(tabla_an)==1:
        tabla_an.append(['','Sin Anomalías',''])
    

    estilo_titulos_tablas = ParagraphStyle('Titulo_tabla', fontSize=15, alignment=1, fontName="Helvetica-Bold")
    elementos.append(Spacer(1, 20))
    tabla_frecuencias = Table(tabla)
    tabla_frecuencias.setStyle(style)
    elementos.append(Paragraph(f"Frecuencias Cardiacas con Irregularidades", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    elementos.append(tabla_frecuencias)

    elementos.append(Spacer(1, 35))
    elementos.append(Paragraph(f"Anomalías del Ruido Ambiente", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    tabla_sonidos = Table(tabla_son)
    tabla_sonidos.setStyle(style)
    elementos.append(tabla_sonidos)

    elementos.append(Spacer(1, 35))
    tabla_anomalias = Table(tabla_an)
    tabla_anomalias.setStyle(style)
    elementos.append(Paragraph(f"Anomalías en la Frecuencia Cardiaca", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    elementos.append(tabla_anomalias)

    elementos.append(Spacer(1, 20))

    elementos.append(imagen_grafica)
    elementos.append(Spacer(1, 60))
    firmas = Table([
        ['_____________________________', '_____________________________'],
        [f'{tutor["nombre"]}', 'Encargado del Centro Psicolegria'],
        ['Encargado o Padre','']
    ])

    firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))

    elementos.append(firmas)


    # Generar el PDF  ----------------  pdf.build(elementos)
    pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="informe.pdf", mimetype='application/pdf')

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response
    return buffer
        














    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    # Aquí defines el contenido del PDF
    p.drawString(100, 750, "Este es tu reporte PDF generado con ReportLab")
    p.drawString(100, 730, "¡Generado desde Flask!")
    p.showPage()
    p.save()
    buffer.seek(0)
     
    # Configura la respuesta con los headers adecuados para PDF
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'


    elementos.append(Spacer(1, 40))

   
    return response
 
 
  

@routes.route("/user/modificar_usuario", methods=["POST"])
def crear_modificar_app():
     
        datos = request.get_json()
 
        print('/*/'*100)
        print(datos)
         
        id_pac = datos.get("id")
        carnet = datos.get("carnet")
        nombre = datos.get("nombre")
        edad = datos.get("fecha")         
        '''nombreTutor = datos.get("rate")
         carnetTutor = datos.get("nombreTutor")
         telefonoTutor = datos.get("carnetTutor")
         correoTutor = datos.get("telefonoTutor")
         contrasena = datos.get("correoTutor")
         rate = datos.get("contrasena")'''
 
        hoy = datetime.today()
 
        # Restar los años de la edad a la fecha de hoy
        #fecha_nacimiento = hoy.replace(year=hoy.year - edad)
 
        # Verificar si ya pasó el cumpleaños este año
        # Si la fecha de nacimiento es después de la fecha actual, restamos un año adicional
        #if hoy.month < fecha_nacimiento.month or (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
        #    fecha_nacimiento = fecha_nacimiento.replace(year=hoy.year - edad - 1)
 
        #fecha_nacimiento = fecha_nacimiento.strftime('%Y-%m-%d')
 
        fecha_nacimiento = datetime.strptime(edad, "%d/%m/%Y")
        fecha_nacimiento = fecha_nacimiento.strftime("%Y-%m-%d")
 
         
         
 
         
 
 
 
        paciente = ServiciosPaciente.modificar(id=id_pac, encargado=None, nacimiento=fecha_nacimiento, tasa=0, nombre=nombre, carnet=carnet)
 
         
 
        '''if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):    
            return jsonify({"mensaje": "Correo electrónico inválido"}), 400
 
        # Generar el hash de la contraseña antes de almacenarla
         
        usuario_nuevo = ServiciosUsuario.crear(nombre, correo, carnet, telefono, password, id_rol)'''
 
        # Insertar el nuevo usuario con la contraseña hasheada
        '''cursor.execute(
             """
             INSERT INTO usuario (nombre, correo, carnet, telefono, password, id_rol) 
             VALUES (%s, %s, %s, %s, %s, %s)
             """, 
             (nombre, correo, carnet, telefono, password, id_rol)
         )
        db.commit()'''
 
        if paciente:
 
            return jsonify({"mensaje": "Usuario agregado con éxito", "redirect": "/usuarios"}), 200
        else:
            return jsonify({"mensaje": "Error al agregar usuario"}), 500
        

@routes.route('/fechas_usos/<id>', methods=['GET'])
def obtener_fechas_usos(id):

    resultados = ServiciosFrecuencia.obtener_lista_fechas_recientes(id)

    print(resultados)

    return jsonify({'cuerpo': resultados})

@routes.route("/informes_paciente", methods=['GET'])
@login_requerido
def informes_paciente():
    nombre_usuario = session.get('nombre', 'Usuario Invitado')
    total_pacientes = session.get('total_pacientes')
    total_usuarios = session.get('total_usuarios')

    

    id_encargado = session.get('usuario_id')
    paciente = ServiciosPaciente.obtener_pacientes_con_encargado_empleado(id_encargado)
    paciente = paciente[0]
    id_paciente= paciente['id_paciente']
    nombre_paciente= paciente['nombre']
    carnet_paciente= paciente['carnet']

    resultados = ServiciosFrecuencia.obtener_lista_fechas_recientes(id_paciente)

    return render_template("informes_paciente.html", nombre_usuario=nombre_usuario, total_pacientes= total_pacientes, total_usuarios=total_usuarios, fechas = resultados, carnet=carnet_paciente)





@routes.route('/generate_pdf3', methods=['GET'])
def generate_pdf3():
    codigo = request.args.get("id_paciente") # es ID no carnet
    print(codigo)

    fecha = request.args.get("fecha")

    fecha = datetime.strptime(fecha, "%Y-%m-%d")

    id_pac_aux = codigo.find('?')
    id_pac_aux = str(id_pac_aux)[0:id_pac_aux]
    print(id_pac_aux)

    paciente = ServiciosPaciente.obtener_por_carnet(codigo)
    id_paciente = paciente['id_paciente']
    id_tutor = paciente['id_encargado']

    tutor = ServiciosUsuario.obtener_id(id_tutor)

    fecha_actual = datetime.now()
    #fecha_actual = fecha_actual - timedelta(days=3)
    fecha_actual = fecha_actual.strftime("%Y-%m-%d")
    print(fecha_actual)

    fecha_actual = fecha.strftime("%Y-%m-%d")

    frecuencias = ServiciosFrecuencia.obtener_frecuencias_por_paciente_y_fecha(id_paciente, fecha_actual)
    sonidos = ServiciosSonido.obtener_por_paciente_fecha(id_paciente, fecha_actual)


    fecha_nacimiento = paciente['fecha_nacimiento']

    hoy = datetime.now()

    edad = hoy.year - fecha_nacimiento.year

    # Ajustar si la fecha actual aún no ha llegado al cumpleaños de este año
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    if edad >15:
        edad = 15

    limite_sup = FRECUENCIAS_NORMALES[str(edad)][1]
    limite_inf = FRECUENCIAS_NORMALES[str(edad)][0]



    fechas_h = []
    frecuencias_h = []
    if frecuencias:
        for frec in frecuencias:
            fecha_ac = frec['fecha'].strftime("%Y-%m-%d %H:%M:%S")
            #fecha_ac = fecha_ac.split(' ')[1]
            fecha_ac = datetime.strptime(fecha_ac, "%Y-%m-%d %H:%M:%S")
            fechas_h.append(fecha_ac)

            frecuencias_h.append(float(frec['valor']))
    

    
    fig, ax = plt.subplots()  # Crea un único eje
    ax.plot(fechas_h, frecuencias_h, marker='o', linestyle='-')
    ax.set_xlabel("Tiempo (HH:MM:SS)")
    ax.set_ylabel("Frecuencia Cardiaca (bpm)")
    ax.set_title("Frecuencia Cardiaca a lo largo del tiempo")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()  # Rota las etiquetas del eje x para mejor visualización

    buf = io.BytesIO()
    plt.savefig(buf, format='PNG')
    plt.close(fig)
    buf.seek(0)
    imagen_grafica = RLImage(buf, width=500, height=250)
    #imagen = ImageReader(buf)


    #print(f"id_paciente: {id_paciente}")
    # Crea un buffer en memoria para el PDF
    
     

    buffer = BytesIO()


    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('Titulo', fontSize=18, alignment=1, fontName="Helvetica-Bold", underline=True)
    estilo_subtitulo = ParagraphStyle('Subtitulo', fontSize=10, alignment=0)  # Para el nombre de usuario y fecha
    estilo_tabla_paragrah = ParagraphStyle('Normala', fontSize=7, alignment=0)
    estilo_datos = estilos['Normal']

    #logo_direccion = os.path.join(os.getcwd(),'app', 'routes', 'logo.png')
    logo_direccion = os.path.join('var', 'www', 'sistema_cardiaco','app', 'routes', 'logo.png')
    #print(logo_direccion)

    # Agregar logo del hospital
    logo = "logo.png"  # Ruta al logo
    imagen_logo = Image(logo_direccion, 2 * inch, 1 * inch)  # Ajustar el tamaño del logo
    #imagen_logo.hAlign = 'LEFT'
    #elementos.append(imagen_logo)


    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    generado_por = Paragraph(f"<b>Fecha de generación:</b> {fecha_actual}", estilo_subtitulo)
    #generado_por = Paragraph(f"<b>Generado por:</b> {nombre_usuario}", estilo_subtitulo)
    #generado_por = f"<b>Generado por:</b> {nombre_usuario}"

    #elementos.append(generado_por)
    #tabla_encabezado = Table([[imagen_logo, generado_por]], colWidths=[4 * inch, 4 * inch])
    #elementos.append(tabla_encabezado)
    def add_header(canvas, doc):
        width, height = letter
        imagen_logo.drawOn(canvas, (0.5*inch), height - (0.5*inch) - imagen_logo.drawHeight)
        #tabla_encabezado.drawOn(canvas, (0.5*inch), height - (0.5*inch) - imagen_logo.drawHeight)
            
        # Obtener el ancho del texto
        #ancho_texto = canvas.stringWidth(generado_por, "Helvetica", 12)
            
        # Posicionar el texto a una pulgada del margen derecho
        posicion_texto_x = (0.3*inch)
        posicion_texto_y = (0.3*inch)
        generado_por.wrapOn(canvas, width, height)
            
        # Dibujar el texto
        generado_por.drawOn(canvas, posicion_texto_x, posicion_texto_y)
        #canvas.drawString(posicion_texto_x, posicion_texto_y, generado_por)

    # Espacio entre elementos
    elementos.append(Spacer(1, 12))

    # Título del documento centrado y subrayado
    titulo = Paragraph("<u>Informe del Paciente</u>", estilo_titulo)
    elementos.append(titulo)

    # Espacio antes de los datos personales
    elementos.append(Spacer(1, 20))

    datos_paciente = Table([[Paragraph(f"<b>Nombres y Apellidos del Paciente:</b> {paciente['nombre']}", estilo_datos), '', ''],
                            [Paragraph(f"<b>Carnet:</b> {paciente['carnet']}", estilo_datos), Paragraph(f"<b>Fecha de Nacimiento:</b> {paciente['fecha_nacimiento']}", estilo_datos), Paragraph(f"<b></b>", estilo_datos)],
                            [Paragraph(f"<b>Nombres Tutor:</b> {tutor['nombre']}", estilo_datos), Paragraph(f"<b>Carnet:</b> {tutor['carnet']}", estilo_datos), Paragraph(f"<b>Telefono:</b> {tutor['telefono']}", estilo_datos)]])

    datos_paciente.setStyle(TableStyle([('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
                                        ('SPAN',(0,0),(2,0)),]))
    #nombres_paciente = Paragraph(f"<b>Nombres y Apellidos del Paciente:</b> {hoja['nombres']} {hoja['apellido_paterno']} {hoja['apellido_materno']}", estilo_datos)
       
    #elementos.append(nombres_paciente)
    elementos.append(datos_paciente)

    # Espacio antes de la tabla
    elementos.append(Spacer(1, 20))

    clasificaciones = ServiciosClasificacion.obtener_todos()
    #print(clasificaciones)

    cabecera = ['Fecha y Hora', 'Frecuencia', 'Estado del Niño', 'Irregularidad Cardiaca', 'Irregularidad Cardiaca (%)']
    cabecera_an = ['Fecha y Hora', 'Frecuencia', 'Estado']

    tabla_an = []
    tabla_an.append(cabecera_an)

    tabla = []
    tabla.append(cabecera)

    if frecuencias:

        indice = 0
        
        for frec in frecuencias:
            indice = indice + 1
            print(frec)
            fila_an = []
            if float(frec['valor'])>limite_sup:
                fila_an = [frec['fecha'], frec['valor'], 'Frecuencia Alta']
                tabla_an.append(fila_an)
            elif float(frec['valor'])<limite_inf:
                fila_an = [frec['fecha'], frec['valor'], 'Frecuencia Baja']
                tabla_an.append(fila_an)
            fila = []
            fila.append(frec['fecha'])
            fila.append(frec['valor'])
            '''soni = ""
            for clas in clasificaciones:
                if frec['id_clasificacion']==clas['id_clasificacion']:
                    soni = clas['nombre']
                    break'''
            
            #fila.append(frec['clasificacion'])
            if float(frec['valor'])>limite_sup and frec['clasificacion']=='Estado Normal':
                fila.append('Frecuencia Alta')
            elif float(frec['valor'])<limite_inf and frec['clasificacion']=='Estado Normal':
                fila.append('Frecuencia Baja')
            else:
                fila.append(frec['clasificacion'])
            if indice > 1:
                diferencia_frec = float(frec['valor']) - float(tabla[indice-1][1])
                diferencia_porc = diferencia_frec / float(tabla[indice-1][1])

                if diferencia_frec > 0.0:
                    fila.append(f'+ {diferencia_frec:.1f}')
                    fila.append(f'+ {diferencia_porc:.3f} %')
                else:
                    fila.append(f'{diferencia_frec:.1f}')
                    fila.append(f'{diferencia_porc:.3f} %')

                
            else:
                fila.append('0.0')
                fila.append('0.000 %')

                
            tabla.append(fila)
    
    cabecera = ['Fecha y Hora', 'Sonido']
    tabla_son = []
    tabla_son.append(cabecera)

    if sonidos:
        
        for frec in sonidos:
            fila = []
            fila.append(frec['fecha'])
            fila.append(frec['sonido'])
            
            tabla_son.append(fila)
    else:
        tabla_son.append(['Sin Sonidos Registrados', ''])
    
    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # color de texto en la primera fila
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación de texto (centrado)
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Negrita en la primera fila (encabezados)
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Fuente normal para el resto
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding en la primera fila
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris para la primera fila
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Mostrar líneas de la tabla
    ])

    if len(tabla_an)==1:
        tabla_an.append(['','Sin Anomalías',''])
    

    estilo_titulos_tablas = ParagraphStyle('Titulo_tabla', fontSize=15, alignment=1, fontName="Helvetica-Bold")
    elementos.append(Spacer(1, 20))
    tabla_frecuencias = Table(tabla)
    tabla_frecuencias.setStyle(style)
    elementos.append(Paragraph(f"Frecuencias Cardiacas con Irregularidades", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    elementos.append(tabla_frecuencias)

    elementos.append(Spacer(1, 35))
    elementos.append(Paragraph(f"Anomalías del Ruido Ambiente", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    tabla_sonidos = Table(tabla_son)
    tabla_sonidos.setStyle(style)
    elementos.append(tabla_sonidos)

    elementos.append(Spacer(1, 35))
    tabla_anomalias = Table(tabla_an)
    tabla_anomalias.setStyle(style)
    elementos.append(Paragraph(f"Anomalías en la Frecuencia Cardiaca", estilo_titulos_tablas))
    elementos.append(Spacer(1,25))
    elementos.append(tabla_anomalias)

    elementos.append(Spacer(1, 20))

    elementos.append(imagen_grafica)
    elementos.append(Spacer(1, 60))
    firmas = Table([
        ['_____________________________', '_____________________________'],
        [f'{tutor["nombre"]}', 'Encargado del Centro Psicolegria'],
        ['Encargado o Padre','']
    ])

    firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))

    elementos.append(firmas)


    # Generar el PDF  ----------------  pdf.build(elementos)
    pdf.build(elementos, onFirstPage=add_header, onLaterPages=add_header)

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="informe.pdf", mimetype='application/pdf')