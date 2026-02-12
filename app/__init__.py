"""
============================================
Board Game Meetup - Application Factory
============================================
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)  # Autorise le frontend React à communiquer avec l'API

    # Import des Blueprints
    from app.api.v1.auth import auth_ns
    from app.api.v1.users import users_ns
    from app.api.v1.events import events_ns
    from app.api.v1.friends import friends_ns
    from app.api.v1.games import games_ns

    # Enregistrement des Blueprints avec le préfixe /api/v1
    app.register_blueprint(auth_ns, url_prefix='/api/v1/auth')
    app.register_blueprint(users_ns, url_prefix='/api/v1/users')
    app.register_blueprint(events_ns, url_prefix='/api/v1/events')
    app.register_blueprint(friends_ns, url_prefix='/api/v1/friends')
    app.register_blueprint(games_ns, url_prefix='/api/v1/games')

    # Route de test pour vérifier que l'API fonctionne
    @app.route('/')
    def index():
        return {
            "message": "Board Game Meetup API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/v1/auth",
                "users": "/api/v1/users",
                "events": "/api/v1/events",
                "friends": "/api/v1/friends",
                "games": "/api/v1/games"
            }
        }

    return app