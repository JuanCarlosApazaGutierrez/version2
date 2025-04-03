from flask import Flask
from app.routes.routes_2 import routes  # Importar las rutas
from flask import Flask, session
import os
from app.config.extensiones import db
from app.config.database import iniciar_datos
from app.config.config import Config

 
def create_app(config_class = Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    
    
    db.init_app(app)
    
    # Registrar las rutas
    app.register_blueprint(routes)
    app.secret_key = os.urandom(24)  # O usa una clave personalizada si prefieres

    return app
