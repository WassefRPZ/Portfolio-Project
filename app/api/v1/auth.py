from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.api.v1 import api_v1
from app.services import facade
from app import limiter


@api_v1.route('/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    user, error = facade.register_user(data)
    if error:
        return jsonify({"error": error}), 400

    access_token = create_access_token(
        identity=str(user['id']),
        additional_claims={
            'username': user.get('username'),
            'email':    user['email'],
            'role':     user.get('role', 'user'),
        }
    )

    return jsonify({
        "success": True,
        "data": {
            "user":         user,
            "access_token": access_token,
        }
    }), 201


@api_v1.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    email    = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    user, error = facade.login_user(email, password)

    if error:
        return jsonify({"error": error}), 401

    access_token = create_access_token(
        identity=str(user['id']),
        additional_claims={
            'username': user.get('username'),
            'email':    user['email'],
            'role':     user.get('role', 'user'),
        }
    )

    return jsonify({
        "success": True,
        "data": {
            "user":         user,
            "access_token": access_token,
        }
    }), 200
