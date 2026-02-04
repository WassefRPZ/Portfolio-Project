from flask import request, jsonify
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()

@api_v1.route('/friends/request/<receiver_id>', methods=['POST'])
def send_request(receiver_id):
    requester_id = request.headers.get('X-User-ID')
    if not requester_id:
        return jsonify({"error": "Unauthorized"}), 401

    result, error = facade.add_friend(requester_id, receiver_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 201

@api_v1.route('/friends/accept/<requester_id>', methods=['POST'])
def accept_request(requester_id):
    current_user_id = request.headers.get('X-User-ID')
    if not current_user_id:
        return jsonify({"error": "Unauthorized"}), 401

    result, error = facade.accept_friend(current_user_id, requester_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 200
