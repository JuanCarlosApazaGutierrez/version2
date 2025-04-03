import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:

 

    JWT_SECRET_KEY = os.environ.get('SECRET_KEYS')
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/app_sistema"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['cookies'] # posiblemente no se use
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)