from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from config import Config

db      = SQLAlchemy()
migrate = Migrate()
jwt     = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)   # Flask-Migrate gère le schéma
    jwt.init_app(app)
    CORS(app)

    # Swagger
    swagger_config = {
        "headers": [],
        "specs": [{
            "endpoint":     "apispec",
            "route":        "/apispec.json",
            "rule_filter":  lambda rule: True,
            "model_filter": lambda tag: True,
        }],
        "static_url_path": "/swagger_static",
        "swagger_ui":      True,
        "specs_route":     "/apidocs/"
    }
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title":       "Board Game Meetup API",
            "description": "API Documentation",
            "version":     "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type":        "apiKey",
                "name":        "Authorization",
                "in":          "header",
                "description": "Enter: Bearer <your_token>"
            }
        }
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # Blueprint
    from app.api.v1 import api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    # Import explicite des modèles pour que Flask-Migrate les découvre tous
    from app.models import (       # noqa: F401
        User, Game, Event, EventParticipant, Comment, Friendship, FavoriteGame, Post, Review
    )

    @app.route('/')
    def index():
        return {
            "message": "Board Game Meetup API",
            "version": "1.0.0",
            "docs":    "/apidocs/",
            "routes": {
                "auth":    "/api/v1/auth",
                "users":   "/api/v1/users",
                "events":  "/api/v1/events",
                "friends": "/api/v1/friends",
                "games":   "/api/v1/games"
            }
        }

    return app
