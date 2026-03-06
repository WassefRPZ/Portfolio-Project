from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import cloudinary
from config import Config

db      = SQLAlchemy()
jwt     = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Cloudinary
    cloudinary.config(
        cloud_name  = app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key     = app.config.get("CLOUDINARY_API_KEY"),
        api_secret  = app.config.get("CLOUDINARY_API_SECRET"),
        secure      = True,
    )

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    origins = app.config.get("CORS_ORIGINS", "*")
    CORS(app, origins=origins.split(",") if origins != "*" else "*")

    # Swagger UI
    SWAGGER_URL = '/apidocs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL,
        config={'app_name': "Board Game Meetup API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Blueprint
    from app.api.v1 import api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    from app.models import (  # noqa: F401
        User, Profile, Game, Event, EventParticipant,
        EventComment, FavoriteGame, Friend, Post
    )
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return {
            "message": "Board Game Meetup API",
            "version": "1.0.0",
            "docs":    "/apidocs",
            "routes": {
                "auth":    "/api/v1/auth",
                "users":   "/api/v1/users",
                "events":  "/api/v1/events",
                "search":  "/api/v1/search",
            }
        }

    return app
