from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


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
    current_user_id = int(get_jwt_identity())

    user = facade.get_user(current_user_id)
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

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
  - multipart/form-data
  - application/json
parameters:
  - in: formData
    name: image
    type: file
    description: "Image de profil (JPEG/PNG) — upload vers Cloudinary"
  - in: formData
    name: username
    type: string
  - in: formData
    name: city
    type: string
  - in: formData
    name: region
    type: string
  - in: formData
    name: bio
    type: string
responses:
  200:
    description: Profile updated
  400:
    description: Invalid data or upload error
"""

    current_user_id = int(get_jwt_identity())

    # Support multipart/form-data (avec fichier) ou application/json (sans fichier)
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        image_file = request.files.get('image')
    else:
        data = request.get_json() or {}
        image_file = None

    if not data and not image_file:
        return jsonify({"error": "Aucune donnée envoyée"}), 400

    updated_user, error = facade.update_user_profile(current_user_id, data, image_file)
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
@api_v1.route('/users/<int:user_id>', methods=['GET'])
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
        type: integer
        required: true
    responses:
      200:
        description: User profile
      404:
        description: Utilisateur introuvable
    """
    user = facade.get_public_user(user_id)
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

    current_user_id = int(get_jwt_identity())

    try:
        limit  = min(int(request.args.get('limit',  50)), 100)
        offset = max(int(request.args.get('offset',  0)),   0)
    except (ValueError, TypeError):
        limit, offset = 50, 0

    events = facade.get_user_events(current_user_id, limit=limit, offset=offset)
    return jsonify({"success": True, "data": events, "limit": limit, "offset": offset}), 200


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
    current_user_id = int(get_jwt_identity())

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
          type: integer
responses:
  201:
    description: Favorite added
"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)

    if not data or 'game_id' not in data:
        return jsonify({"error": "game_id requis"}), 400

    favorite, error = facade.add_favorite_game(current_user_id, data['game_id'])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": favorite}), 201


# -----------------------------------------------
# DELETE /users/me/favorite-games/<game_id> → retirer un jeu favori
# -----------------------------------------------
@api_v1.route('/users/me/favorite-games/<int:game_id>', methods=['DELETE'])
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
        type: integer
        required: true
    responses:
      200:
        description: Game removed
    """
    current_user_id = int(get_jwt_identity())

    result, error = facade.remove_favorite_game(current_user_id, game_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Jeu retiré des favoris"}), 200
