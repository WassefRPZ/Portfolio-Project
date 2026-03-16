"""
Routes du catalogue de jeux : consultation paginée et recherche textuelle.

"""

from flask import request, jsonify
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/games', methods=['GET'])
def list_games():
    """
    Récupère une liste paginée de tous les jeux du catalogue.

    """
    try:
        # Valide et limite les paramètres de pagination
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 par page
        offset = max(int(request.args.get('offset', 0)), 0)  # Min 0
    except (ValueError, TypeError):
        limit, offset = 50, 0  # Valeurs par défaut en cas d'erreur

    games, total = facade.list_games(limit=limit, offset=offset)  # Récupère la page
    return jsonify({"success": True, "data": games, "total_count": total}), 200


@api_v1.route('/games/search', methods=['GET'])
def search_games():
    """
    Recherche des jeux par nom (recherche textuelle substring).

    """
    query = request.args.get('q', '').strip()  # Récupère et nettoie la chaîne de recherche

    if not query:
        return jsonify({"error": "Paramètre 'q' requis"}), 400

    games = facade.search_games(query)  # Cherche les jeux au niveau métier
    return jsonify({"success": True, "data": games}), 200
