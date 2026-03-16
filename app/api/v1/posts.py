"""
Routes des posts : flux social, création, modification/suppression et filtrage par auteur.

"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/posts', methods=['GET'])
@jwt_required()
def list_posts():
    """
    Récupère une liste paginée de tous les posts du flux social.
    
    """
    # Valide et limite les paramètres de pagination
    try:
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 par page
        offset = max(int(request.args.get('offset', 0)), 0)   # Min 0
    except (ValueError, TypeError):
        limit, offset = 50, 0  # Valeurs par défaut en cas d'erreur

    posts, total = facade.list_posts(limit=limit, offset=offset)  # Récupère la page
    return jsonify({"success": True, "data": posts, "total_count": total}), 200


@api_v1.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """
    Crée un nouveau post sur le fil social.
    Accepte un formulaire multipart (pour image) ou du JSON.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    # Détecte le type de contenu pour traiter formulaires multipart ou JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()  # Données du formulaire
        image_file = request.files.get('image')  # Fichier image
    else:
        data = request.get_json(silent=True) or {}  # Données JSON
        image_file = None

    # Crée le post via le service métier
    result, error = facade.create_post(current_user_id, data, image_file)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 201


@api_v1.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    """
    Récupère les détails complets d'un post spécifique.

    """
    result, error = facade.get_post(post_id)  # Récupère le post
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """
    Met à jour un post existant.
    Seul l'auteur du post peut le modifier.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    data = request.get_json(silent=True) or {}  # Récupère les données JSON

    # Appelle le service métier avec vérification d'autorisation
    result, error = facade.update_post(current_user_id, post_id, data)
    if error:
        if error == "forbidden":
            return jsonify({"error": "Vous n'êtes pas l'auteur de ce post"}), 403
        if error == "Post introuvable":
            return jsonify({"error": error}), 404
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """
    Supprime un post existant.
    Seul l'auteur du post peut le supprimer.
    
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    # Appelle le service métier avec vérification d'autorisation
    result, error = facade.delete_post(current_user_id, post_id)
    if error:
        if error == "forbidden":
            return jsonify({"error": "Vous n'êtes pas l'auteur de ce post"}), 403
        if error == "Post introuvable":
            return jsonify({"error": error}), 404
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/posts/user/<int:user_id>', methods=['GET'])
@jwt_required()
def list_user_posts(user_id):
    """
    Récupère tous les posts d'un utilisateur spécifique avec pagination.
    
    """
    # Valide et limite les paramètres de pagination
    try:
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 par page
        offset = max(int(request.args.get('offset', 0)), 0)   # Min 0
    except (ValueError, TypeError):
        limit, offset = 50, 0  # Valeurs par défaut en cas d'erreur

    # Récupère les posts de l'utilisateur
    posts, total = facade.list_user_posts(user_id, limit=limit, offset=offset)
    return jsonify({"success": True, "data": posts, "total_count": total}), 200
