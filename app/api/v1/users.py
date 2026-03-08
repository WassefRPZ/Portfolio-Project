from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    user = facade.get_public_user(user_id)
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"success": True, "data": user}), 200


@api_v1.route('/users/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    current_user_id = int(get_jwt_identity())

    user = facade.get_user(current_user_id)
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"success": True, "data": user}), 200


@api_v1.route('/users/me', methods=['PUT'])
@jwt_required()
def update_my_profile():

    current_user_id = int(get_jwt_identity())

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


@api_v1.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    query = request.args.get('q', '')
    city = request.args.get('city')

    if not query and not city:
        return jsonify({"error": "Paramètre q ou city requis"}), 400

    users = facade.search_users(query, city)
    return jsonify({"success": True, "data": users}), 200


@api_v1.route('/users/me/favorite-games', methods=['GET'])
@jwt_required()
def get_favorite_games():
    current_user_id = int(get_jwt_identity())
    games = facade.get_favorite_games(current_user_id)
    return jsonify({"success": True, "data": games}), 200


@api_v1.route('/users/me/favorite-games', methods=['POST'])
@jwt_required()
def add_favorite_game():
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)

    if not data or 'game_id' not in data:
        return jsonify({"error": "game_id requis"}), 400

    favorite, error = facade.add_favorite_game(current_user_id, data['game_id'])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": favorite}), 201


@api_v1.route('/users/me/favorite-games/<int:game_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite_game(game_id):
    current_user_id = int(get_jwt_identity())

    result, error = facade.remove_favorite_game(current_user_id, game_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Jeu retiré des favoris"}), 200
