from flask import request, jsonify
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()

@api_v1.route('/users/me', methods=['GET'])
def get_my_profile():
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    user = facade.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

@api_v1.route('/users/me', methods=['PUT'])
def update_my_profile():
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    updated_user = facade.update_user_profile(user_id, data)
    if not updated_user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(updated_user), 200
