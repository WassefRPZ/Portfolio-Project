from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# GET /games → liste tous les jeux en base
# Table games : game_id, name, description, min_players, max_players, play_time, image_url
# -----------------------------------------------
@api_v1.route('/games', methods=['GET'])
def get_all_games():
    """
Get all games
---
tags:
  - Games
responses:
  200:
    description: List of games
"""
    games = facade.get_all_games()
    return jsonify({"success": True, "data": games}), 200


# -----------------------------------------------
# GET /games/search?q=catan → rechercher un jeu par nom
# -----------------------------------------------
@api_v1.route('/games/search', methods=['GET'])
@jwt_required()
def search_games():
    """
    Search games by name
    ---
    tags:
      - Games
    security:
      - Bearer: []
    parameters:
      - name: q
        in: query
        type: string
        required: true
    responses:
      200:
        description: Matching games
      400:
        description: Missing query parameter
    """
    query = request.args.get('q', '')

    if not query:
        return jsonify({"error": "Paramètre q requis"}), 400

    games = facade.search_games(query)
    return jsonify({"success": True, "data": games}), 200


# -----------------------------------------------
# GET /games/popular → jeux les plus utilisés dans les events
# -----------------------------------------------
@api_v1.route('/games/popular', methods=['GET'])
def get_popular_games():
    """
Get popular games
---
tags:
  - Games
responses:
  200:
    description: Popular games
"""
    games = facade.get_popular_games()
    return jsonify({"success": True, "data": games}), 200


# -----------------------------------------------
# GET /games/<game_id> → détails d'un jeu
# -----------------------------------------------
@api_v1.route('/games/<game_id>', methods=['GET'])
def get_game(game_id):
    """
    Get game details
    ---
    tags:
      - Games
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Game details
      404:
        description: Game not found
    """
    game = facade.get_game(game_id)
    if not game:
        return jsonify({"error": "Jeu introuvable"}), 404

    return jsonify({"success": True, "data": game}), 200


# -----------------------------------------------
# GET /games/<game_id>/events → événements utilisant ce jeu
# -----------------------------------------------
@api_v1.route('/games/<game_id>/events', methods=['GET'])
def get_game_events(game_id):
    """
    Get events for a game
    ---
    tags:
      - Games
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Events using this game
      404:
        description: Game not found
    """
    game = facade.get_game(game_id)
    if not game:
        return jsonify({"error": "Jeu introuvable"}), 404

    events = facade.get_events_by_game(game_id)
    return jsonify({"success": True, "data": events}), 200


# -----------------------------------------------
# POST /games → ajouter un jeu (admin seulement)
# Body: { name, description?, min_players, max_players, play_time, image_url? }
# -----------------------------------------------
@api_v1.route('/games', methods=['POST'])
@jwt_required()
def create_game():
    """
    Create a new game (Admin only)
    ---
    tags:
      - Games
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
            - name
            - min_players
            - max_players
            - play_time
          properties:
            name:
              type: string
              example: "Catan"
            description:
              type: string
              example: "Jeu de stratégie"
            min_players:
              type: integer
              example: 3
            max_players:
              type: integer
              example: 4
            play_time:
              type: integer
              example: 90
            image_url:
              type: string
              example: "http://image.com/catan.jpg"
    responses:
      201:
        description: Game created
      400:
        description: Invalid input
      403:
        description: Admin only
    """
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify({"error": "Action réservée aux administrateurs"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400


    required = ['name', 'min_players', 'max_players', 'play_time']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Champ '{field}' manquant"}), 400


    if data['min_players'] > data['max_players']:
        return jsonify({"error": "min_players ne peut pas dépasser max_players"}), 400

    try:
        existing = facade.get_game_by_name(data['name'])
        if existing:
            return jsonify({"error": "Ce jeu existe déjà"}), 400


        new_game = facade.create_game(data)
        return jsonify({"success": True, "data": new_game}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------------------------
# PUT /games/<game_id> → modifier un jeu (admin seulement)
# -----------------------------------------------
@api_v1.route('/games/<game_id>', methods=['PUT'])
@jwt_required()
def update_game(game_id):
    """
    Update a game (Admin only)
    ---
    tags:
      - Games
    security:
      - Bearer: []
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Game updated
      403:
        description: Admin only
    """
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify({"error": "Action réservée aux administrateurs"}), 403

    game = facade.get_game(game_id)
    if not game:
        return jsonify({"error": "Jeu introuvable"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    # Vérifier cohérence joueurs si les deux sont fournis
    min_p = data.get('min_players', game['min_players'])
    max_p = data.get('max_players', game['max_players'])
    if min_p > max_p:
        return jsonify({"error": "min_players ne peut pas dépasser max_players"}), 400

    updated_game = facade.update_game(game_id, data)
    return jsonify({"success": True, "data": updated_game}), 200
