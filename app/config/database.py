from app.services.serviciosAlerta import ServiciosAlerta
from app.services.serviciosClasificacion import ServiciosClasificacion
from app.services.serviciosFrecuencia import ServiciosFrecuencia
from app.services.serviciosPaciente import ServiciosPaciente
from app.services.serviciosRol import ServiciosRol
from app.services.serviciosSonido import ServiciosSonido
from app.services.serviciosUsuario import ServiciosUsuario

from datetime import date, time

def iniciar_datos():

    
    
    registros = ServiciosRol.obtener_todos()
     
    if not registros:
        nuevo_regitro = ServiciosRol.crear('Administrador')
        nuevo_regitro = ServiciosRol.crear('Padre')

    registros = ServiciosUsuario.obtener_todos()
     
    if not registros:
        nuevo_regitro = ServiciosUsuario.crear('Juan Perez', 'juanperez@email.com', 222223232, 789456123, 'admin', 1)
        nuevo_regitro = ServiciosUsuario.crear('Juan Carlos', 'nuevavidaparajuan@gmail.com', 234324, 234234, 'admin', 2)


    registros = ServiciosClasificacion.obtener_todos()
     
    if not registros:
        nuevo_regitro = ServiciosClasificacion.crear('Ladridos Fuerte', 'Clasificación para sonidos de ladridos fuertes que pueden ser molestos o perturbadores, de alta intensidad')
        nuevo_regitro = ServiciosClasificacion.crear('Ladridos Normal', 'Clasificación para sonidos de ladridos normales, comunes y moderados')
        nuevo_regitro = ServiciosClasificacion.crear('Ladridos Leve', 'Clasificación para sonidos de ladridos suaves, de baja intensidad')
        nuevo_regitro = ServiciosClasificacion.crear('Bocina Fuerte', 'Clasificación para sonidos de bocinas fuertes y estridentes que pueden generar incomodidad')
        nuevo_regitro = ServiciosClasificacion.crear('Bocina Normal', 'Clasificación para sonidos de bocinas de volumen moderado, típicos en situaciones cotidianas')
        nuevo_regitro = ServiciosClasificacion.crear('Bocina Leve', 'Clasificación para sonidos de bocinas suaves, con menor impacto acústico')
        nuevo_regitro = ServiciosClasificacion.crear('Petardo Fuerte', 'Clasificación para sonidos de Petardo que emiten frecuencias altas o ruidos fuertes explosiones')
        nuevo_regitro = ServiciosClasificacion.crear('Petardo Normal', 'Clasificación para sonidos de Petardo en situaciones comunes ')
        nuevo_regitro = ServiciosClasificacion.crear('Petardo Leve', 'Clasificación para sonidos suaves de Petardo , como susurros o zumbidos')
        nuevo_regitro = ServiciosClasificacion.crear('Estado Normal', 'Clasificación para la condición normal, sin alteraciones significativas o sonidos anormales. El estado habitual del ambiente o de los perros')


    '''registros = Servicios.obtener_todos()
    if not registros:
        nuevo_regitro = Servicios.crear()

    registros = Servicios.obtener_todos()
    if not registros:
        nuevo_regitro = Servicios.crear()

    registros = Servicios.obtener_todos()
    if not registros:
        nuevo_regitro = Servicios.crear()

    registros = Servicios.obtener_todos()
    if not registros:
        nuevo_regitro = Servicios.crear()'''

    
    

