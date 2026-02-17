"""User API endpoints for BoardGame Meetup application."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import BoardGameFacade

api = Namespace('users', description='User operations')
facade = BoardGameFacade()

user_update_model = api.model('UserUpdate', {
    'username': fields.String(required=False, description='Nom utilisateur'),
    'city': fields.String(required=False, description='Ville'),
    'region': fields.String(required=False, description='Région'),
    'bio': fields.String(required=False, description='Bio'),
    'profile_image_url': fields.String(required=False, description='Photo de profil')
})

favorite_game_model = api.model('FavoriteGame', {
    'game_id': fields.String(required=True, description='ID du jeu')
})


@api.route('/me')
class Me(Resource):

    @jwt_required()
    @api.response(200, 'Profil récupéré avec succès')
    @api.response(404, 'Utilisateur introuvable')
    def get(self):

        current_user_id = get_jwt_identity()

        user = facade.get_user(current_user_id)
        if not user:
            return {'error': 'Utilisateur introuvable'}, 404

        return {'success': True, 'data': user}, 200

    @jwt_required()
    @api.expect(user_update_model, validate=True)
    @api.response(200, 'Profil mis à jour avec succès')
    @api.response(404, 'Utilisateur introuvable')
    def put(self):

        current_user_id = get_jwt_identity()
        data = api.payload

        updated_user = facade.update_user_profile(current_user_id, data)
        if not updated_user:
            return {'error': 'Utilisateur introuvable'}, 404

        return {'success': True, 'data': updated_user}, 200



@api.route('/search')
class UserSearch(Resource):

    @jwt_required()
    @api.response(200, 'Résultats de la recherche')
    @api.response(400, 'Paramètre de recherche manquant')
    def get(self):

        from flask import request
        query = request.args.get('q', '')
        city = request.args.get('city')

        if not query and not city:
            return {'error': 'Paramètre q ou city requis'}, 400

        users = facade.search_users(query, city)
        return {'success': True, 'data': users}, 200


@api.route('/<user_id>')
class UserResource(Resource):

    @jwt_required()
    @api.response(200, 'Profil récupéré avec succès')
    @api.response(404, 'Utilisateur introuvable')
    def get(self, user_id):

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'Utilisateur introuvable'}, 404

        return {'success': True, 'data': user}, 200


@api.route('/me/events')
class MyEvents(Resource):

    @jwt_required()
    @api.response(200, 'Événements récupérés avec succès')
    def get(self):
        current_user_id = get_jwt_identity()
        events = facade.get_user_events(current_user_id)
        return {'success': True, 'data': events}, 200


@api.route('/me/favorite-games')
class MyFavoriteGames(Resource):

    @jwt_required()
    @api.response(200, 'Jeux favoris récupérés avec succès')
    def get(self):

        current_user_id = get_jwt_identity()
        favorites = facade.get_favorite_games(current_user_id)
        return {'success': True, 'data': favorites}, 200

    @jwt_required()
    @api.expect(favorite_game_model, validate=True)
    @api.response(201, 'Jeu ajouté aux favoris')
    @api.response(400, 'Jeu déjà en favori ou introuvable')
    def post(self):

        current_user_id = get_jwt_identity()
        data = api.payload

        favorite, error = facade.add_favorite_game(current_user_id, data['game_id'])
        if error:
            return {'error': error}, 400

        return {'success': True, 'data': favorite}, 201



@api.route('/me/favorite-games/<game_id>')
class MyFavoriteGameResource(Resource):

    @jwt_required()
    @api.response(200, 'Jeu retiré des favoris')
    @api.response(400, 'Jeu introuvable dans les favoris')
    def delete(self, game_id):

        current_user_id = get_jwt_identity()

        result, error = facade.remove_favorite_game(current_user_id, game_id)
        if error:
            return {'error': error}, 400

        return {'success': True, 'message': 'Jeu retiré des favoris'}, 200