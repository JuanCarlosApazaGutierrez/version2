import firebase_admin
from firebase_admin import credentials, firestore

credenciales = credentials.Certificate("credenciales_firebase.json")
firebase_admin.initialize_app(credenciales)
base_datos = firestore.client()
