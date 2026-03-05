from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# GET /games → liste tous les jeux en base
# Table games : game_id, name, description, min_players, max_players, play_time_minutes, image_url
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
@api_v1.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """
    Get game details
    ---
    tags:
      - Games
    parameters:
      - name: game_id
        in: path
        type: integer
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
@api_v1.route('/games/<int:game_id>/events', methods=['GET'])
def get_game_events(game_id):
    """
    Get events for a game
    ---
    tags:
      - Games
    parameters:
      - name: game_id
        in: path
        type: integer
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
# POST /games → ajouter un jeu via Board Game Atlas (admin seulement)
# Body: { id_api }  — toutes les autres infos sont récupérées depuis l'API externe
# -----------------------------------------------
@api_v1.route('/games', methods=['POST'])
@jwt_required()
def create_game():
    """
    Create a new game from BoardGameGeek (Admin only)
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
            - id_api
          properties:
            id_api:
              type: integer
              description: "Identifiant BoardGameGeek (ex: 13 pour Catan, 68448 pour 7 Wonders)"
              example: 13
            name:
              type: string
              description: "Fallback manuel si BGG est inaccessible"
              example: "Catan"
            description:
              type: string
              example: "Le jeu de plateau classique"
            min_players:
              type: integer
              example: 3
            max_players:
              type: integer
              example: 4
            play_time_minutes:
              type: integer
              example: 90
            image_url:
              type: string
              example: ""
    responses:
      201:
        description: "Game created (BGG auto ou données manuelles si name/min_players/max_players/play_time_minutes fournis)"
      400:
        description: id_api manquant, introuvable sur BGG, ou jeu déjà en base
      403:
        description: Admin only
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "Action réservée aux administrateurs"}), 403

    data = request.get_json()
    if not data or not data.get('id_api'):
        return jsonify({"error": "Le champ 'id_api' est requis"}), 400

    new_game, error = facade.create_game(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": new_game}), 201


# -----------------------------------------------
# PUT /games/<game_id> → modifier un jeu (admin seulement)
# -----------------------------------------------
@api_v1.route('/games/<int:game_id>', methods=['PUT'])
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
        type: integer
        required: true
    responses:
      200:
        description: Game updated
      403:
        description: Admin only
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "Action réservée aux administrateurs"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    updated_game, error = facade.update_game(game_id, data)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "data": updated_game}), 200
