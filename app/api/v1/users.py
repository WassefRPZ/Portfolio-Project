<<<<<<< HEAD
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# GET /users/me → voir son propre profil
# Retourne : user + ses jeux favoris (géré dans facade.get_user)
# -----------------------------------------------
@api_v1.route('/users/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """
Get current user profile
---
tags:
  - Users
security:
  - Bearer: []
responses:
  200:
    description: User profile
  401:
    description: Unauthorized
"""
    current_user_id = get_jwt_identity()

    user = facade.get_user(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"success": True, "data": user}), 200


# -----------------------------------------------
# PUT /users/me → modifier son profil
# Champs modifiables : username, city, region, bio, profile_image_url
# -----------------------------------------------
@api_v1.route('/users/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    """
Update current user profile
---
tags:
  - Users
security:
  - Bearer: []
consumes:
  - application/json
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      properties:
        username:
          type: string
        city:
          type: string
        region:
          type: string
        bio:
          type: string
        profile_image_url:
          type: string
responses:
  200:
    description: Profile updated
"""

    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Aucune donnée envoyée"}), 400

    updated_user = facade.update_user_profile(current_user_id, data)
    if not updated_user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"success": True, "data": updated_user}), 200


# -----------------------------------------------
# GET /users/search?q=john&city=Paris → chercher des joueurs
# -----------------------------------------------
@api_v1.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    """
    Search users
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - name: q
        in: query
        type: string
        required: false
      - name: city
        in: query
        type: string
        required: false
    responses:
      200:
        description: List of users
      400:
        description: Missing parameters
    """
    query = request.args.get('q', '')
    city = request.args.get('city')

    if not query and not city:
        return jsonify({"error": "Paramètre q ou city requis"}), 400

    users = facade.search_users(query, city)
    return jsonify({"success": True, "data": users}), 200


# -----------------------------------------------
# GET /users/<user_id> → voir le profil d'un autre joueur
# -----------------------------------------------
@api_v1.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """
    Get another user's profile
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: User profile
      404:
        description: User not found
    """
    user = facade.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"success": True, "data": user}), 200


# -----------------------------------------------
# GET /users/me/events → ses événements (créés + rejoints)
# -----------------------------------------------
@api_v1.route('/users/me/events', methods=['GET'])
@jwt_required()
def get_my_events():
    """
Get my events
---
tags:
  - Users
security:
  - Bearer: []
responses:
  200:
    description: User events
"""

    current_user_id = get_jwt_identity()

    events = facade.get_user_events(current_user_id)
    return jsonify({"success": True, "data": events}), 200


# -----------------------------------------------
# GET /users/me/favorite-games → voir ses jeux favoris
# -----------------------------------------------
@api_v1.route('/users/me/favorite-games', methods=['GET'])
@jwt_required()
def get_my_favorite_games():
    """
Get favorite games
---
tags:
  - Users
security:
  - Bearer: []
responses:
  200:
    description: Favorite games
"""
    current_user_id = get_jwt_identity()

    favorites = facade.get_favorite_games(current_user_id)
    return jsonify({"success": True, "data": favorites}), 200


# -----------------------------------------------
# POST /users/me/favorite-games → ajouter un jeu favori
# Body: { game_id }
# -----------------------------------------------
@api_v1.route('/users/me/favorite-games', methods=['POST'])
@jwt_required()
def add_favorite_game():
    """
Add favorite game
---
tags:
  - Users
security:
  - Bearer: []
consumes:
  - application/json
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      required:
        - game_id
      properties:
        game_id:
          type: string
responses:
  201:
    description: Favorite added
"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'game_id' not in data:
        return jsonify({"error": "game_id requis"}), 400

    favorite, error = facade.add_favorite_game(current_user_id, data['game_id'])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": favorite}), 201


# -----------------------------------------------
# DELETE /users/me/favorite-games/<game_id> → retirer un jeu favori
# -----------------------------------------------
@api_v1.route('/users/me/favorite-games/<game_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite_game(game_id):
    """
    Remove favorite game
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Game removed
    """
    current_user_id = get_jwt_identity()

    result, error = facade.remove_favorite_game(current_user_id, game_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Jeu retiré des favoris"}), 200
=======
from flask_restx import Namespace, Resource, fields
from app.services import facade

# Création du Namespace 'users'.
api = Namespace('users', description='Opérations liées à la gestion des utilisateurs')

# Ce modèle définit quels champs sont renvoyés au client (frontend) lors d'une requête GET.
user_model = api.model('User', {
    'id': fields.String(readonly=True, description='Identifiant unique de l\'utilisateur'),
    'first_name': fields.String(required=True, description='Prénom'),
    'last_name': fields.String(required=True, description='Nom de famille'),
    'email': fields.String(required=True, description='Adresse email'),
    'city': fields.String(description='Ville de résidence'),
    'bio': fields.String(description='Biographie courte'),
    'is_admin': fields.Boolean(readonly=True, description='Statut administrateur'),
    'created_at': fields.String(readonly=True, description='Date d\'inscription')
})

# Ce modèle définit les données attendues lors d'une requête PUT.
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='Nouveau prénom'),
    'last_name': fields.String(description='Nouveau nom de famille'),
    'city': fields.String(description='Nouvelle ville'),
    'bio': fields.String(description='Nouvelle biographie')
})


@api.route('/<string:user_id>')
@api.response(404, 'Utilisateur non trouvé')
class UserResource(Resource):
    """
    Classe gérant les opérations sur un utilisateur spécifique via son ID.
    """

    @api.doc('get_user')
    @api.marshal_with(user_model)
    def get(self, user_id):
        """
        Récupérer les détails d'un utilisateur par son ID.
        
        Cette méthode appelle la façade pour obtenir les données et utilise
        le décorateur @api.marshal_with pour formater la réponse JSON selon le user_model.
        """
        # Appel à la couche Business Logic
        user = facade.get_user(user_id)

        # Gestion d'erreur si l'utilisateur n'existe pas
        if not user:
            api.abort(404, "User not found")
        
        # Retourne l'objet
        return user.to_dict(), 200

    @api.doc('update_user')
    @api.expect(user_update_model, validate=True)
    @api.marshal_with(user_model) # Formate la réponse avec le modèle complet
    def put(self, user_id):
        """
        Mettre à jour les informations d'un utilisateur.
        
        Attend un objet JSON contenant les champs à modifier (first_name, last_name, city, bio).
        """
        # Récupération des données envoyées dans le corps de la requête
        user_data = api.payload
        
        # Appel à la façade pour effectuer la modification
        updated_user = facade.update_user(user_id, user_data)
        
        # Si la façade retourne None, c'est que l'utilisateur n'existe pas
        if not updated_user:
            api.abort(404, "User not found")
            
        return updated_user.to_dict(), 200
    
>>>>>>> origin/feature/database
