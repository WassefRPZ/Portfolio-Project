"""
============================================
Routes amis
============================================
"""
from flask import Blueprint, request, jsonify
from app.services.facade import BoardGameFacade
from app.utils.auth import token_required

friends_ns = Blueprint('friends', __name__)
facade = BoardGameFacade()

@friends_ns.route('/request/<receiver_id>', methods=['POST'])
@token_required
def send_friend_request(current_user_id, receiver_id):
    """
    POST /api/v1/friends/request/<receiver_id>
    Headers: Authorization: Bearer <token>
    """
    result, error = facade.add_friend(current_user_id, receiver_id)
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    return jsonify({"success": True, "data": result}), 201

@friends_ns.route('/accept/<requester_id>', methods=['POST'])
@token_required
def accept_friend_request(current_user_id, requester_id):
    """
    POST /api/v1/friends/accept/<requester_id>
    Headers: Authorization: Bearer <token>
    """
    result, error = facade.accept_friend(current_user_id, requester_id)
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    return jsonify({"success": True, "data": result}), 200

@friends_ns.route('', methods=['GET'])
@token_required
def get_my_friends(current_user_id):
    """
    GET /api/v1/friends
    Headers: Authorization: Bearer <token>
    """
    friends = facade.get_friends(current_user_id)
    
    return jsonify({"success": True, "data": friends}), 200