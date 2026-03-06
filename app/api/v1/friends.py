from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import friend_service


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

    result, error = friend_service.add_friend(current_user_id, receiver_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": result}), 201


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

    result, error = friend_service.accept_friend(current_user_id, requester_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": result}), 200
