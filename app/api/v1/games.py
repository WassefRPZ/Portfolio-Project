"""Game API endpoints for BoardGame Meetup application."""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.facade import BoardGameFacade

api = Namespace('games', description='Game operations')
facade = BoardGameFacade()

game_model = api.model('Game', {
    'name': fields.String(required=True, description='Nom du jeu'),
    'description': fields.String(required=False, description='Description'),
    'min_players': fields.Integer(required=True, description='Nombre min de joueurs'),
    'max_players': fields.Integer(required=True, description='Nombre max de joueurs'),
    'play_time': fields.Integer(required=True, description='Durée en minutes'),
    'image_url': fields.String(required=False, description='URL de l\'image')
})

game_update_model = api.model('GameUpdate', {
    'name': fields.String(required=False, description='Nom du jeu'),
    'description': fields.String(required=False, description='Description'),
    'min_players': fields.Integer(required=False, description='Nombre min de joueurs'),
    'max_players': fields.Integer(required=False, description='Nombre max de joueurs'),
    'play_time': fields.Integer(required=False, description='Durée en minutes'),
    'image_url': fields.String(required=False, description='URL de l\'image')
})



@api.route('/')
class GameList(Resource):

    @api.response(200, 'Liste des jeux récupérée avec succès')
    def get(self):
        """Récupérer tous les jeux disponibles"""
        games = facade.get_all_games()
        return {'success': True, 'data': games}, 200

    @jwt_required()
    @api.expect(game_model, validate=True)
    @api.response(201, 'Jeu ajouté avec succès')
    @api.response(400, 'Jeu déjà existant ou données invalides')
    @api.response(403, 'Action non autorisée')
    def post(self):
        """Ajouter un jeu en base (admin seulement)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        if not is_admin:
            return {'error': 'Action réservée aux administrateurs'}, 403

        data = api.payload

        # Vérifier si le jeu existe déjà
        existing = facade.get_game_by_name(data['name'])
        if existing:
            return {'error': 'Ce jeu existe déjà'}, 400

        try:
            new_game = facade.create_game(data)
            return {'success': True, 'data': new_game}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Données invalides'}, 400


@api.route('/search')
class GameSearch(Resource):

    @jwt_required()
    @api.response(200, 'Résultats de la recherche')
    @api.response(400, 'Paramètre de recherche manquant')
    def get(self):
        """Rechercher des jeux par nom"""
        from flask import request
        query = request.args.get('q', '')

        if not query:
            return {'error': 'Paramètre q requis'}, 400

        games = facade.search_games(query)
        return {'success': True, 'data': games}, 200


@api.route('/popular')
class PopularGames(Resource):

    @api.response(200, 'Jeux populaires récupérés')
    def get(self):
        """Récupérer les jeux les plus utilisés dans les événements"""
        games = facade.get_popular_games()
        return {'success': True, 'data': games}, 200


@api.route('/<game_id>')
class GameResource(Resource):

    @api.response(200, 'Détails du jeu récupérés')
    @api.response(404, 'Jeu introuvable')
    def get(self, game_id):
        """Voir les détails d'un jeu"""
        game = facade.get_game(game_id)
        if not game:
            return {'error': 'Jeu introuvable'}, 404

        return {'success': True, 'data': game}, 200

    @jwt_required()
    @api.expect(game_update_model, validate=True)
    @api.response(200, 'Jeu mis à jour')
    @api.response(403, 'Action non autorisée')
    @api.response(404, 'Jeu introuvable')
    def put(self, game_id):
        """Modifier un jeu (admin seulement)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        if not is_admin:
            return {'error': 'Action réservée aux administrateurs'}, 403

        game = facade.get_game(game_id)
        if not game:
            return {'error': 'Jeu introuvable'}, 404

        data = api.payload

        # Vérifier que min_players < max_players si les deux sont fournis
        min_p = data.get('min_players', game['min_players'])
        max_p = data.get('max_players', game['max_players'])
        if min_p > max_p:
            return {'error': 'min_players ne peut pas dépasser max_players'}, 400

        try:
            updated_game = facade.update_game(game_id, data)
            return {'success': True, 'data': updated_game}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Données invalides'}, 400

@api.route('/<game_id>/events')
class GameEventList(Resource):

    @api.response(200, 'Événements récupérés')
    @api.response(404, 'Jeu introuvable')
    def get(self, game_id):
        """Voir tous les événements qui utilisent ce jeu"""
        game = facade.get_game(game_id)
        if not game:
            return {'error': 'Jeu introuvable'}, 404

        events = facade.get_events_by_game(game_id)
        return {'success': True, 'data': events}, 200