from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from config import Config

db  = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    origins = app.config.get("CORS_ORIGINS", "*")
    CORS(app, origins=origins.split(",") if origins != "*" else "*")

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

    from app.models import (  # noqa: F401
        User, Profile, Game, Event, EventParticipant,
        EventComment, Friend, FavoriteGame, Post, Review
    )
    with app.app_context():
        db.create_all()

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
