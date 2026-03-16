"""
Routes sociales : gestion des demandes d'amis, acceptation/refus et listes relationnelles.
"""

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/friends/request/<int:receiver_id>', methods=['POST'])
@jwt_required()
def send_friend_request(receiver_id):
    """
    Envoie une demande d'amitié à un autre utilisateur.
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    result, error = facade.send_friend_request(current_user_id, receiver_id)  # Crée la demande
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 201


@api_v1.route('/friends/accept/<int:requester_id>', methods=['POST'])
@jwt_required()
def accept_friend_request(requester_id):
    """
    Accepte une demande d'amitié reçue.
    Change le statut de la relation ami de 'pending' à 'accepted'.
    
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    result, error = facade.accept_friend_request(current_user_id, requester_id)  # Accepte la demande
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/friends/reject/<int:requester_id>', methods=['POST'])
@jwt_required()
def reject_friend_request(requester_id):
    """
    Refuse une demande d'amitié reçue.
    Supprime la relation ami ou la laisse à l'état 'pending' selon la logique métier.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    result, error = facade.reject_friend_request(current_user_id, requester_id)  # Refuse la demande
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/friends/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(user_id):
    """
    Supprime un ami ou cancelle une demande d'amitié en attente.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    result, error = facade.remove_friend(current_user_id, user_id)  # Supprime la relation
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/friends', methods=['GET'])
@jwt_required()
def list_friends():
    """
    Récupère la liste complète des amis de l'utilisateur connecté.
    Ne retourne que les relations avec statut 'accepted'.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    friends = facade.get_friends_list(current_user_id)  # Récupère les amis acceptés
    return jsonify({"success": True, "data": friends}), 200


@api_v1.route('/friends/pending', methods=['GET'])
@jwt_required()
def pending_requests():
    """
    Récupère les demandes d'amitié en attente reçues par l'utilisateur.
    
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    pending = facade.get_pending_requests(current_user_id)  # Récupère les demandes reçues
    return jsonify({"success": True, "data": pending}), 200


@api_v1.route('/friends/sent', methods=['GET'])
@jwt_required()
def sent_requests():
    """
    Récupère les demandes d'amitié envoyées par l'utilisateur connecté.

    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    sent = facade.get_sent_requests(current_user_id)  # Récupère les demandes envoyées
    return jsonify({"success": True, "data": sent}), 200
