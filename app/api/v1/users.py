"""
Routes utilisateur : profil public/privé, mise à jour et gestion des jeux favoris.

"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """
    Récupère le profil public d'un utilisateur par son ID.
    
    """
    user = facade.get_public_user(user_id)  # Récupère le profil public
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"success": True, "data": user}), 200


@api_v1.route('/users/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """
    Récupère le profil complet de l'utilisateur connecté.
    Inclut les informations privées et la liste des jeux favoris.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    user = facade.get_user(current_user_id)  # Récupère le profil complet
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"success": True, "data": user}), 200


@api_v1.route('/users/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    """
    Met à jour le profil de l'utilisateur connecté.
    Accepte un formulaire multipart (pour upload d'image) ou du JSON.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    # Détecte le type de contenu pour traiter formulaires multipart ou JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()  # Données du formulaire
        image_file = request.files.get('image')  # Fichier image
    else:
        data = request.get_json() or {}  # Données JSON
        image_file = None

    if not data and not image_file:
        return jsonify({"error": "Aucune donnée envoyée"}), 400

    # Délègue au service métier
    updated_user, error = facade.update_user_profile(current_user_id, data, image_file)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "data": updated_user}), 200


@api_v1.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    """
    Recherche des utilisateurs par pseudonyme et/ou par ville.
    
    """
    query = request.args.get('q', '')  # Chaîne de recherche sur les pseudos
    city = request.args.get('city')  # Filtre optionnel par ville

    if not query and not city:
        return jsonify({"error": "Paramètre q ou city requis"}), 400

    users = facade.search_users(query, city)  # Recherche au niveau métier
    return jsonify({"success": True, "data": users}), 200


@api_v1.route('/users/me/favorite-games', methods=['GET'])
@jwt_required()
def get_favorite_games():
    """
    Récupère la liste des jeux favoris de l'utilisateur connecté.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    games = facade.get_favorite_games(current_user_id)  # Récupère les favoris
    return jsonify({"success": True, "data": games}), 200


@api_v1.route('/users/me/favorite-games', methods=['POST'])
@jwt_required()
def add_favorite_game():
    """
    Ajoute un jeu à la liste des favoris de l'utilisateur.
    
    Attendu dans le corps (JSON):
    - game_id: ID numérique du jeu à ajouter (int)
    
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    data = request.get_json(silent=True)  # Récupère les données JSON

    if not data or 'game_id' not in data:
        return jsonify({"error": "game_id requis"}), 400

    # Crée la relation favourite_game
    favorite, error = facade.add_favorite_game(current_user_id, data['game_id'])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": favorite}), 201


@api_v1.route('/users/me/favorite-games/<int:game_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite_game(game_id):
    """
    Retire un jeu de la liste des favoris.
    
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    # Supprime la relation favourite_game
    result, error = facade.remove_favorite_game(current_user_id, game_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Jeu retiré des favoris"}), 200
