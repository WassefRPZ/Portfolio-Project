from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# POST /auth/register
# Body: { username, email, password, city, region?, bio? }
# -----------------------------------------------
@api_v1.route('/auth/register', methods=['POST'])
def register():
    """
Register a new user
---
tags:
  - Auth
consumes:
  - application/json
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      required:
        - username
        - email
        - password
        - city
      properties:
        username:
          type: string
          example: nina
        email:
          type: string
          example: nina@test.com
        password:
          type: string
          example: motdepasse123
        city:
          type: string
          example: Paris
        region:
          type: string
          example: Île-de-France
        bio:
          type: string
          example: Passionnée de jeux de société
responses:
  201:
    description: User registered
  400:
    description: Invalid input
"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    user, error = facade.register_user(data)
    if error:
        return jsonify({"error": error}), 400

    access_token = create_access_token(
        identity=user['id'],  # INT — utilisé comme identité JWT
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


# -----------------------------------------------
# POST /auth/login
# Body: { email, password }
# -----------------------------------------------
@api_v1.route('/auth/login', methods=['POST'])
def login():
    """
    Login user
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    email    = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    user = facade.login_user(email, password)

    if not user:
        return jsonify({"error": "Email ou mot de passe incorrect"}), 401

    access_token = create_access_token(
        identity=user['id'],  # INT — utilisé comme identité JWT
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
