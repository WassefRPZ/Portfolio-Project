from flask import request, jsonify
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()

@api_v1.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    user, error = facade.register_user(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": user}), 201

@api_v1.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
        
    user = facade.login_user(data.get('email'), data.get('password'))
    if user:
        return jsonify({"success": True, "data": {"user": user, "token": "fake-jwt-token"}}), 200
    return jsonify({"error": "Invalid credentials"}), 401
