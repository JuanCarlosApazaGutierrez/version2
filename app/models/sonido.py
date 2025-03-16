from app.config.extensiones import db
from datetime import datetime

class Sonido(db.Model):
    __tablename__ = "sonidos"

    id = db.Column(db.Integer, primary_key = True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'))
    fecha = db.Column(db.DateTime, default = datetime.utcnow)
    sonido = db.Column(db.String(20), nullable = False)

    def __init__(self, paciente, sonido):
        self.id_paciente = paciente
        self.sonido = sonido
