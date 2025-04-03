from app.config.extensiones import db

class Clasificacion(db.Model):
    __tablename__ = "clasificacion"

    id_clasificacion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable = False)
    descripcion = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Integer, default=1)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion