"""
============================================
Routes jeux
============================================
"""
from flask import Blueprint, request, jsonify
from app.services.facade import BoardGameFacade
from app.utils.auth import token_required

games_ns = Blueprint('games', __name__)
facade = BoardGameFacade()

@games_ns.route('/search', methods=['GET'])
@token_required
def search_games(current_user_id):
    """
    GET /api/v1/games/search?q=<query>
    Headers: Authorization: Bearer <token>
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"success": False, "error": "Paramètre 'q' requis"}), 400
    
    games = facade.search_games(query)
    
    return jsonify({"success": True, "data": games}), 200