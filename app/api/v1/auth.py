"""
Routes d'authentification : inscription, connexion et génération de jetons JWT.
"""

from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.api.v1 import api_v1
from app.services import facade
from app import limiter


@api_v1.route('/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """
    Endpoint d'inscription pour créer un nouveau compte utilisateur.
    """
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
    """
    Endpoint de connexion pour authentifier un utilisateur existant.
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    email    = data.get('email')  # Récupère l'email fourni
    password = data.get('password')  # Récupère le mot de passe en clair

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    # Délègue au service métier pour vérifier les identifiants
    user, error = facade.login_user(email, password)

    if error:
        return jsonify({"error": error}), 401

    # Génère un token JWT contenant l'ID et les informations clés de l'utilisateur
    access_token = create_access_token(
        identity=str(user['id']),  # ID stocké dans le token
        additional_claims={
            'username': user.get('username'),  # Informations supplémentaires dans le token
            'email':    user['email'],
            'role':     user.get('role', 'user'),
        }
    )

    return jsonify({
        "success": True,
        "data": {
            "user":         user,  # Données complètes de l'utilisateur
            "access_token": access_token,  # Token à envoyer dans les en-têtes futurs
        }
    }), 200
