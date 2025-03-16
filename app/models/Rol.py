from app.config.extensiones import db

class Rol(db.Model):
    __tablename__ = "roles"

    id_rol = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False)
    activo = db.Column(db.Integer, default = 1)

    def __init__(self, nombre):
        self.nombre = nombre