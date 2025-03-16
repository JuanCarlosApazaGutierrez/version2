import mysql.connector

# Función para obtener la conexión a la base de datos
def get_db_connection():
    """
    Crea y devuelve una nueva conexión a la base de datos.
    """
    connection = mysql.connector.connect(
        host="localhost",
        user="root",      # Si tu usuario es diferente, ajústalo
        password="",      # Ajusta si tienes una contraseña
        database="app_sistema"
    )
    return connection

# Función para obtener el cursor
def get_cursor():
    """
    Obtiene un cursor de la base de datos.
    """
    connection = get_db_connection()  # Obtener la conexión
    cursor = connection.cursor(dictionary=True)  # Crear el cursor
    return cursor, connection  # Devolvemos tanto el cursor como la conexión

