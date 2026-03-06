from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import post_service


@api_v1.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create a post
    ---
    tags:
      - Posts
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: content
        type: string
        required: false
        description: "Texte du post (optionnel si image fournie)"
        example: "Soirée Catan vendredi !"
      - in: formData
        name: post_type
        type: string
        required: false
        description: "text (défaut), image, news"
      - in: formData
        name: image
        type: file
        required: false
        description: "Fichier image (JPEG, PNG…)"
    responses:
      201:
        description: Post created
      400:
        description: Ni texte ni image, ou type invalide
    """
    current_user_id = int(get_jwt_identity())
    json_data  = request.get_json(silent=True) or {}
    content    = request.form.get('content')   or json_data.get('content')
    post_type  = request.form.get('post_type') or json_data.get('post_type', 'text')
    image_file = request.files.get('image')

    post, error = post_service.create_post(
        author_id=current_user_id,
        content=content,
        image_file=image_file,
        post_type=post_type,
    )
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": post}), 201


@api_v1.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """
    Delete a post
    ---
    tags:
      - Posts
    security:
      - Bearer: []
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Post deleted
      403:
        description: Not the author
      404:
        description: Post not found
    """
    current_user_id = int(get_jwt_identity())
    result, error = post_service.delete_post(post_id, current_user_id)
    if error:
        status = 404 if "introuvable" in error else 403
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Publication supprimée"}), 200
