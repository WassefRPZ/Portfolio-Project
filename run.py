from app import create_app

# Crée l'application en utilisant la configuration définie dans config.py
app = create_app()

if __name__ == '__main__':
    print("🎲 Lancement du serveur Board Game Meetup...")
    print("👉 Accès API : http://127.0.0.1:5000/api/v1/")
    
    app.run(debug=True, port=5000)
