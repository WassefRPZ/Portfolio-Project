from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/search', methods=['GET'])
@jwt_required()
def global_search():
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({"error": "Paramètre 'q' requis"}), 400

    results = facade.global_search(query)
    return jsonify({"success": True, "data": results}), 200
