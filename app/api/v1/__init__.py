from flask import Blueprint

# 1. Création du Blueprint parent (Prefix global: /api/v1)
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# 2. Import des sous-blueprints (namespaces)
# Attention aux imports circulaires : on importe APRES la création de api_v1 si nécessaire, 
# mais ici tes fichiers importent api_v1 ? Non, ils créent leur propre BP. C'est bien.
from app.api.v1.auth import auth_ns
from app.api.v1.events import events_ns
from app.api.v1.users import users_ns
from app.api.v1.friends import friends_ns
from app.api.v1.games import games_ns

# 3. Enregistrement des enfants sur le parent
# C'est ici que la magie opère pour créer : /api/v1/auth/login, /api/v1/events, etc.
api_v1.register_blueprint(auth_ns, url_prefix='/auth')
api_v1.register_blueprint(events_ns, url_prefix='/events')
api_v1.register_blueprint(users_ns, url_prefix='/users')
api_v1.register_blueprint(friends_ns, url_prefix='/friends')
api_v1.register_blueprint(games_ns, url_prefix='/games')
