from flask import request, jsonify
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# GET /search?q=... → recherche globale (utilisateurs + événements)
# -----------------------------------------------
@api_v1.route('/search', methods=['GET'])
def global_search():
    """
    Global search across users and events
    ---
    tags:
      - Search
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: "Mot-clé à rechercher (username pour les joueurs, titre/description pour les événements)"
    responses:
      200:
        description: Résultats de la recherche
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
              properties:
                users:
                  type: array
                  description: Joueurs dont le username correspond
                events:
                  type: array
                  description: Événements ouverts dont le titre ou la description correspond
      400:
        description: Paramètre q manquant
    """
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({"error": "Paramètre 'q' requis"}), 400

    results = facade.global_search(query)
    return jsonify({"success": True, "data": results}), 200
