from app import create_app, db
import app.models

# Crée l'application en utilisant la configuration définie dans config.py
app = create_app()

if __name__ == '__main__':
    print(" Démarrage du système...")

    # Bloc magique : Crée les tables si elles n'existent pas
    with app.app_context():
        try:
            db.create_all()
            print(" Base de données & Tables synchronisées avec succès.")
        except Exception as e:
            print(f" Erreur lors de la création des tables : {e}")
            print("Assure-toi que la base de données 'boardgame_meetup' existe bien dans MySQL.")
    
    print(" Serveur accessible sur : http://127.0.0.1:5000/api/v1/")
    print(" Documentation Swagger : http://127.0.0.1:5000/apidocs/")
    app.run(debug=True, port=5000)
