from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/friends/request/<int:receiver_id>', methods=['POST'])
@jwt_required()
def send_friend_request(receiver_id):
    current_user_id = int(get_jwt_identity())
    result, error = facade.send_friend_request(current_user_id, receiver_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 201


@api_v1.route('/friends/accept/<int:requester_id>', methods=['POST'])
@jwt_required()
def accept_friend_request(requester_id):
    current_user_id = int(get_jwt_identity())
    result, error = facade.accept_friend_request(current_user_id, requester_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/friends/reject/<int:requester_id>', methods=['POST'])
@jwt_required()
def reject_friend_request(requester_id):
    current_user_id = int(get_jwt_identity())
    result, error = facade.reject_friend_request(current_user_id, requester_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/friends/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(user_id):
    current_user_id = int(get_jwt_identity())
    result, error = facade.remove_friend(current_user_id, user_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/friends', methods=['GET'])
@jwt_required()
def list_friends():
    current_user_id = int(get_jwt_identity())
    friends = facade.get_friends_list(current_user_id)
    return jsonify({"success": True, "data": friends}), 200


@api_v1.route('/friends/pending', methods=['GET'])
@jwt_required()
def pending_requests():
    current_user_id = int(get_jwt_identity())
    pending = facade.get_pending_requests(current_user_id)
    return jsonify({"success": True, "data": pending}), 200


@api_v1.route('/friends/sent', methods=['GET'])
@jwt_required()
def sent_requests():
    current_user_id = int(get_jwt_identity())
    sent = facade.get_sent_requests(current_user_id)
    return jsonify({"success": True, "data": sent}), 200
