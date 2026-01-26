from flask import Blueprint

# 1. Création du Blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# 2. Import des routes après la création
from app.api.v1 import auth, events, users, friends
