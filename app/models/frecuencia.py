from app.config.extensiones import db
from datetime import datetime

class Frecuencia(db.Model):
    __tablename__ = "frecuencias"

    id_frecuencia = db.Column(db.Integer, primary_key = True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    ritmo = db.Column(db.String(50), nullable = False)
    id_clasificacion = db.Column(db.Integer, db.ForeignKey('clasificacion.id_clasificacion'), nullable = False)
    valor = db.Column(db.Float, nullable = False)
    id_estado = db.Column(db.Integer, nullable = True, default = None)
    activo = db.Column(db.Integer, default = 1)
    fecha = db.Column(db.DateTime, default = datetime.utcnow)

    def __init__(self, paciente, ritmo, clasificacion, valor, estado = None):
        self.id_paciente = paciente
        self.ritmo = ritmo
        self.id_clasificacion = clasificacion
        self.valor = valor
        self.id_estado = estado
        