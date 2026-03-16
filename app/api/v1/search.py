"""
Route de recherche globale : interroge plusieurs entités (utilisateurs, jeux, événements).

Ce module expose un endpoint de recherche unifié qui interroge simultanément:
- Les utilisateurs (par pseudonyme)
- Les jeux (par nom)
- Les événements (par titre/description)
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/search', methods=['GET'])
@jwt_required()
def global_search():
    """
    Effectue une recherche globale sur plusieurs types d'entités.
    
    """
    query = request.args.get('q', '').strip()  # Récupère et nettoie la chaîne de recherche

    if not query:
        return jsonify({"error": "Paramètre 'q' requis"}), 400

    # Appelle le service métier qui interroge tous les référentiels
    results = facade.global_search(query)
    return jsonify({"success": True, "data": results}), 200
