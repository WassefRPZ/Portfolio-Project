from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# GET /users/me → voir son propre profil
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
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"success": True, "data": user}), 200


# -----------------------------------------------
# PUT /users/me → modifier son profil
# Champs modifiables : first_name, last_name, username, city, region, bio, profile_image_url
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
        first_name:
          type: string
        last_name:
          type: string
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

    updated_user, error = facade.update_user_profile(current_user_id, data)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

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
        description: Utilisateur introuvable
    """
    user = facade.get_user(user_id)
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

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
