from app.config.extensiones import db

class Paciente(db.Model):
    __tablename__ = "paciente"

    id_paciente = db.Column(db.Integer, primary_key = True)
    id_encargado = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    frecuencias = db.Column(db.Float, nullable = True, default = None)
    fecha_nacimiento = db.Column(db.Date, nullable = False)
    tasa = db.Column(db.Integer, nullable = False)
    activo = db.Column(db.Integer, default = 1)
    nombre = db.Column(db.String(150), nullable = False)
    carnet = db.Column(db.Integer, nullable = False)
    diagnostico  = db.Column(db.Text, nullable = True, default = None)

    def __init__(self, encargado, nacimiento, tasa, nombre, carnet, frecuencia = None, diagnostico = None):
        self.id_encargado = encargado
        self.frecuencias = frecuencia
        self.fecha_nacimiento = nacimiento
        self.tasa = tasa
        self.nombre = nombre
        self.carnet = carnet
        self.diagnostico = diagnostico