from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/games', methods=['GET'])
@jwt_required()
def list_games():
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
    except (ValueError, TypeError):
        limit, offset = 50, 0

    games, total = facade.list_games(limit=limit, offset=offset)
    return jsonify({"success": True, "data": games, "total_count": total}), 200


@api_v1.route('/games/search', methods=['GET'])
@jwt_required()
def search_games():
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({"error": "Paramètre 'q' requis"}), 400

    games = facade.search_games(query)
    return jsonify({"success": True, "data": games}), 200
