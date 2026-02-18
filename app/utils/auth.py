from flask import jsonify
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity
from functools import wraps

def generate_token(user_id, username, email):
    """
    Génère un token JWT contenant l'ID utilisateur et quelques infos
    """
    # L'identité principale est l'ID de l'utilisateur
    identity = user_id
    # ajout des infos supplémentaires
    additional_claims = {"username": username, "email": email}
    
    # Création du token via Flask-JWT-Extended
    token = create_access_token(identity=identity, additional_claims=additional_claims)
    return token

def token_required(f):
    """
    Décorateur pour protéger les routes qui nécessitent d'être connecté.
    Injecte 'current_user_id' dans la fonction décorée.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Vérifie que le token est présent et valide dans la requête
            verify_jwt_in_request()
            # Récupère l'identité (user_id) depuis le token
            current_user_id = get_jwt_identity()
            # Appelle la fonction originale avec l'ID utilisateur
            return f(current_user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({"success": False, "error": "Token manquant ou invalide"}), 401
    return decorated

def optional_token(f):
    """
    Décorateur pour les routes où le token est optionnel.
    Injecte 'current_user_id' (qui sera l'ID ou None).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Tente de vérifier le token
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
            return f(current_user_id, *args, **kwargs)
        except Exception:
            # Si pas de token ou token invalide, on passe None
            return f(None, *args, **kwargs)
    return decorated
