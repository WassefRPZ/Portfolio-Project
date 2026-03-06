from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/posts', methods=['GET'])
@jwt_required()
def list_posts():
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
    except (ValueError, TypeError):
        limit, offset = 50, 0

    posts, total = facade.list_posts(limit=limit, offset=offset)
    return jsonify({"success": True, "data": posts, "total_count": total}), 200


@api_v1.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = int(get_jwt_identity())

    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        image_file = request.files.get('image')
    else:
        data = request.get_json(silent=True) or {}
        image_file = None

    result, error = facade.create_post(current_user_id, data, image_file)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": result}), 201


@api_v1.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    result, error = facade.get_post(post_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"success": True, "data": result}), 200


@api_v1.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

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
    current_user_id = int(get_jwt_identity())

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
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
    except (ValueError, TypeError):
        limit, offset = 50, 0

    posts, total = facade.list_user_posts(user_id, limit=limit, offset=offset)
    return jsonify({"success": True, "data": posts, "total_count": total}), 200
