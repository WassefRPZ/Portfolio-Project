from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


# -----------------------------------------------
# GET /friends → voir sa liste d'amis
# -----------------------------------------------
@api_v1.route('/friends', methods=['GET'])
@jwt_required()
def get_my_friends():
    """
Get my friends
---
tags:
  - Friends
security:
  - Bearer: []
responses:
  200:
    description: List of friends
"""
    current_user_id = int(get_jwt_identity())

    friends = facade.get_friends(current_user_id)
    return jsonify({"success": True, "data": friends}), 200


# -----------------------------------------------
# GET /friends/requests → voir ses demandes reçues en attente
# -----------------------------------------------
@api_v1.route('/friends/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    """
Get pending friend requests
---
tags:
  - Friends
security:
  - Bearer: []
responses:
  200:
    description: Pending requests
"""
    current_user_id = int(get_jwt_identity())

    requests_list = facade.get_pending_requests(current_user_id)
    return jsonify({"success": True, "data": requests_list}), 200


# -----------------------------------------------
# POST /friends/request/<receiver_id> → envoyer une demande
# -----------------------------------------------
@api_v1.route('/friends/request/<int:receiver_id>', methods=['POST'])
@jwt_required()
def send_friend_request(receiver_id):
    """
    Send a friend request
    ---
    tags:
      - Friends
    security:
      - Bearer: []
    parameters:
      - name: receiver_id
        in: path
        type: integer
        required: true
    responses:
      201:
        description: Friend request sent
      400:
        description: Bad request
    """
    current_user_id = int(get_jwt_identity())

    result, error = facade.add_friend(current_user_id, receiver_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": result}), 201


# -----------------------------------------------
# POST /friends/accept/<requester_id> → accepter une demande
# -----------------------------------------------
@api_v1.route('/friends/accept/<int:requester_id>', methods=['POST'])
@jwt_required()
def accept_friend_request(requester_id):
    """
    Accept a friend request
    ---
    tags:
      - Friends
    security:
      - Bearer: []
    parameters:
      - name: requester_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Friend request accepted
    """
    current_user_id = int(get_jwt_identity())

    result, error = facade.accept_friend(current_user_id, requester_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": result}), 200


# -----------------------------------------------
# POST /friends/decline/<requester_id> → refuser une demande
# -----------------------------------------------
@api_v1.route('/friends/decline/<int:requester_id>', methods=['POST'])
@jwt_required()
def decline_friend_request(requester_id):
    """
    Decline a friend request
    ---
    tags:
      - Friends
    security:
      - Bearer: []
    parameters:
      - name: requester_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Friend request declined
    """
    current_user_id = int(get_jwt_identity())

    result, error = facade.decline_friend(current_user_id, requester_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Demande refusée"}), 200


# -----------------------------------------------
# DELETE /friends/<friend_id> → supprimer un ami
# -----------------------------------------------
@api_v1.route('/friends/<int:friend_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(friend_id):
    """
    Remove a friend
    ---
    tags:
      - Friends
    security:
      - Bearer: []
    parameters:
      - name: friend_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Friend removed
    """
    current_user_id = int(get_jwt_identity())

    result, error = facade.remove_friend(current_user_id, friend_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Ami supprimé"}), 200


# -----------------------------------------------
# GET /friends/sent → voir ses demandes envoyées en attente
# -----------------------------------------------
@api_v1.route('/friends/sent', methods=['GET'])
@jwt_required()
def get_sent_requests():
    """
    Get pending friend requests sent by the current user
    ---
    tags:
      - Friends
    security:
      - Bearer: []
    responses:
      200:
        description: Pending sent requests
    """
    current_user_id = int(get_jwt_identity())

    sent = facade.get_sent_requests(current_user_id)
    return jsonify({"success": True, "data": sent}), 200
