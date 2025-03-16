from app.config.extensiones import db
from datetime import datetime

class Alerta(db.Model):
    __tablename__ = "alertas"

    id_alerta = db.Column(db.Integer, primary_key = True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'))
    fecha = db.Column(db.DateTime, default = datetime.utcnow)
    alerta = db.Column(db.String(255))
    frecuencia = db.Column(db.Float)
    sonido = db.Column(db.String(20))

    def __init__(self, paciente, alerta, frecuencia, sonido):
        self.id_paciente = paciente
        self.alerta = alerta
        self.frecuencia = frecuencia
        self.sonido = sonido