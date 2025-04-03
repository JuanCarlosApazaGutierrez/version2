import mysql.connector

 
db = mysql.connector.connect(
    host="localhost", 
    user="root",  
    password="",   
    database="app_sistema"  
)

cursor = db.cursor(dictionary=True)