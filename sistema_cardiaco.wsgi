# /var/www/sistema_cardiaco/sistema_cardiaco.wsgi
import sys
import os

# Agrega la ruta de tu aplicación
sys.path.insert(0, '/var/www/sistema_cardiaco')


from run import app as application

