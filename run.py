from app import create_app, db, iniciar_datos

app = create_app()

with app.app_context():
    db.create_all()
    iniciar_datos()

if __name__ == "__main__":
    #app.run(host='192.168.0.5', port= 8080,debug=True)
    app.run(host='192.168.0.7', port= 8080,debug=True)
