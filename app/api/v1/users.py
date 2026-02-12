"""
============================================
Routes utilisateurs
============================================
"""
from flask import Blueprint, request, jsonify
from app.services.facade import BoardGameFacade
from app.utils.auth import token_required

users_ns = Blueprint('users', __name__)
facade = BoardGameFacade()

@users_ns.route('/me', methods=['GET'])
@token_required
def get_my_profile(current_user_id):
    """
    GET /api/v1/users/me
    Headers: Authorization: Bearer <token>
    """
    user = facade.get_user(current_user_id)
    
    if not user:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 404
    
    return jsonify({"success": True, "data": user}), 200

@users_ns.route('/me', methods=['PUT'])
@token_required
def update_my_profile(current_user_id):
    """
    PUT /api/v1/users/me
    Headers: Authorization: Bearer <token>
    Body: { "username"?, "city"?, "region"?, "bio"?, "profile_image_url"? }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "Pas de données à mettre à jour"}), 400
    
    updated_user = facade.update_user_profile(current_user_id, data)
    
    if not updated_user:
        return jsonify({"success": False, "error": "Erreur lors de la mise à jour"}), 500
    
    return jsonify({"success": True, "data": updated_user}), 200

@users_ns.route('/search', methods=['GET'])
@token_required
def search_users(current_user_id):
    """
    GET /api/v1/users/search?q=<query>&city=<city>
    Headers: Authorization: Bearer <token>
    """
    query = request.args.get('q', '')
    city = request.args.get('city')
    
    users = facade.search_users(query, city)
    
    return jsonify({"success": True, "data": users}), 200

@users_ns.route('/me/favorite-games', methods=['POST'])
@token_required
def add_favorite_game(current_user_id):
    """
    POST /api/v1/users/me/favorite-games
    Headers: Authorization: Bearer <token>
    Body: { "game_id" }
    """
    data = request.get_json()
    
    if not data or 'game_id' not in data:
        return jsonify({"success": False, "error": "game_id requis"}), 400
    
    favorite, error = facade.add_favorite_game(current_user_id, data['game_id'])
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    return jsonify({"success": True, "data": favorite}), 201

@users_ns.route('/me/favorite-games/<game_id>', methods=['DELETE'])
@token_required
def remove_favorite_game(current_user_id, game_id):
    """
    DELETE /api/v1/users/me/favorite-games/<game_id>
    Headers: Authorization: Bearer <token>
    """
    result, error = facade.remove_favorite_game(current_user_id, game_id)
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    return jsonify({"success": True, "message": "Jeu retiré des favoris"}), 200