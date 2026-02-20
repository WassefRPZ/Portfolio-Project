from app import create_app

# Création de l'application via la factory function définie dans app/__init__.py
app = create_app()

if __name__ == '__main__':
    # Lancement du serveur de développement Flask
    # debug=True permet le rechargement automatique quand tu modifies le code
    # host='0.0.0.0' rend le serveur accessible depuis l'extérieur (utile si tu utilises Docker ou une VM)
    app.run(debug=True, host='0.0.0.0', port=5000)
