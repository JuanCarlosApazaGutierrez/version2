from app.config.extensiones import db

class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(150), nullable = False)
    correo = db.Column(db.String(150), nullable = False)
    carnet = db.Column(db.Integer, nullable = False)
    telefono = db.Column(db.Integer, nullable = False)
    password = db.Column(db.Text, nullable = False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'))
    activo = db.Column(db.Integer, default = 1)
    token = db.Column(db.Text, default = '0')

    def __init__(self, nombre, correo, carnet, telefono, contrasena, rol):
        self.nombre = nombre
        self.correo = correo
        self.carnet = carnet
        self.telefono = telefono
        self.password = contrasena
        self.id_rol = rol