<<<<<<< HEAD
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)


    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Board Game Meetup API",
            "description": "API Documentation",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter: Bearer <your_token>"
            }
        }
    }

    Swagger(app, config=swagger_config, template=swagger_template)


    from app.api.v1 import api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    from app.models import (
        User,
        Game,
        Event,
        EventParticipant,
        Comment,
        Friendship,
        FavoriteGame
    )

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return {
            "message": "Board Game Meetup API",
            "version": "1.0.0",
            "routes": {
                "auth": "/api/v1/auth",
                "users": "/api/v1/users",
                "events": "/api/v1/events",
                "friends": "/api/v1/friends",
                "games": "/api/v1/games"
            }
        }

    return app
=======
from flask import Flask
from flask_restx import Api
from app.services.facade import HBnBFacade

facade = HBnBFacade()

def create_app():
    """
    Factory function qui initialise l'application Flask et les extensions.
    """
    app = Flask(__name__)

    api = Api(
        app, 
        version='1.0', 
        title='BoardGame Hub API',
        description='API de gestion pour le portfolio BoardGame Hub (Holberton)',
        doc='/api/v1' 
    )

    
    from app.api.v1.users import api as users_ns
    from app.api.v1.events import api as events_ns
    

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(events_ns, path='/api/v1/events')

    return app
>>>>>>> origin/feature/database
