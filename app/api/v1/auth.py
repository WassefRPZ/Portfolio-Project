"""Auth API endpoints for BoardGame Meetup application."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services.facade import BoardGameFacade

api = Namespace('auth', description='Authentication operations')
facade = BoardGameFacade()

register_model = api.model('Register', {
    'username': fields.String(required=True, description='Nom utilisateur'),
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Mot de passe'),
    'city': fields.String(required=True, description='Ville'),
    'region': fields.String(required=False, description='Région'),
    'bio': fields.String(required=False, description='Bio')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Mot de passe')
})


@api.route('/register')
class Register(Resource):

    @api.expect(register_model, validate=True)
    @api.response(201, 'Compte créé avec succès')
    @api.response(400, 'Données invalides ou email déjà utilisé')
    def post(self):

        data = api.payload

        existing = facade.get_user_by_email(data['email'])
        if existing:
            return {'error': 'Cet email est déjà utilisé'}, 400

        existing_username = facade.get_user_by_username(data['username'])
        if existing_username:
            return {'error': 'Ce nom d\'utilisateur est déjà pris'}, 400

        try:
            user, error = facade.register_user(data)
            if error:
                return {'error': error}, 400


            access_token = create_access_token(
                identity=str(user['user_id']),
                additional_claims={
                    'username': user['username'],
                    'email': user['email']
                }
            )

            return {
                'message': 'Compte créé avec succès',
                'user': user,
                'access_token': access_token
            }, 201

        except Exception as e:
            return {'error': str(e)}, 400



@api.route('/login')
class Login(Resource):

    @api.expect(login_model, validate=True)
    @api.response(200, 'Connexion réussie')
    @api.response(401, 'Email ou mot de passe incorrect')
    def post(self):

        credentials = api.payload


        user = facade.login_user(credentials['email'], credentials['password'])

        if not user:
            return {'error': 'Email ou mot de passe incorrect'}, 401


        access_token = create_access_token(
            identity=str(user['user_id']),
            additional_claims={
                'username': user['username'],
                'email': user['email']
            }
        )

        return {
            'access_token': access_token,
            'user': user
        }, 200