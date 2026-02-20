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