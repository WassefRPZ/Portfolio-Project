"""
Point d'entrée principal de l'application Flask.

Ce script:
- Crée l'application Flask via create_app()
- Lit les paramètres de lancement (host, port, debug)
- Affiche les URLs utiles
- Démarre le serveur web développement

Paramètres d'environnement:
- FLASK_DEBUG: Active le mode debug (défaut: false)
- FLASK_HOST: Interface d'écoute (défaut: 127.0.0.1)
- FLASK_PORT: Port d'écoute (défaut: 5000)
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"  # Mode debug
    port  = int(os.getenv("FLASK_PORT", "5000"))  # Port TCP
    host  = os.getenv("FLASK_HOST", "127.0.0.1")  # Interface d'écoute

    print("Démarrage de BoardGame Hub...")  # Titre
    print(f"API accessible sur   : http://{host}:{port}/api/v1/")  # URL API
    print(f"Documentation Swagger : http://{host}:{port}/apidocs/")  # URL docs
    
    app.run(debug=debug, host=host, port=port)
