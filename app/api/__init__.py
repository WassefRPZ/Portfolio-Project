from flask import Blueprint
from app.api.v1.auth import auth_ns
from app.api.v1.events import events_ns
from app.api.v1.users import users_ns
from app.api.v1.friends import friends_ns

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

api_v1.register_blueprint(auth_ns, url_prefix='/auth')
api_v1.register_blueprint(events_ns, url_prefix='/events')
api_v1.register_blueprint(users_ns, url_prefix='/users')
api_v1.register_blueprint(friends_ns, url_prefix='/friends')
