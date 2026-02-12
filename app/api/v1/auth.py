"""
============================================
Routes d'authentification
============================================
"""
from flask import Blueprint, request, jsonify
from app.services.facade import BoardGameFacade
from app.utils.auth import generate_token

auth_ns = Blueprint('auth', __name__)
facade = BoardGameFacade()

@auth_ns.route('/register', methods=['POST'])
def register():
    """
    POST /api/v1/auth/register
    Body: { "username", "email", "password", "city", "region"?, "bio"? }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "Pas de données envoyées"}), 400
    
    user, error = facade.register_user(data)
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Générer le token JWT
    token = generate_token(user['user_id'], user['username'], user['email'])
    
    return jsonify({
        "success": True,
        "data": {
            "user": user,
            "token": token
        }
    }), 201

@auth_ns.route('/login', methods=['POST'])
def login():
    """
    POST /api/v1/auth/login
    Body: { "email", "password" }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "Pas de données envoyées"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email et mot de passe requis"}), 400
    
    user = facade.login_user(email, password)
    
    if not user:
        return jsonify({"success": False, "error": "Email ou mot de passe incorrect"}), 401
    
    # Générer le token JWT
    token = generate_token(user['user_id'], user['username'], user['email'])
    
    return jsonify({
        "success": True,
        "data": {
            "user": user,
            "token": token
        }
    }), 200