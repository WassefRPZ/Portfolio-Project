from flask import Flask
from config import Config
from app.models import db
from app.api.v1 import api_v1

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(api_v1)

    return app
