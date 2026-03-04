from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# POST /posts → créer une publication
# Body: { content }
# -----------------------------------------------
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
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - content
          properties:
            content:
              type: string
              example: "Soirée Catan vendredi soir, qui est partant ?"
    responses:
      201:
        description: Post created
      400:
        description: Missing content
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('content'):
        return jsonify({"error": "Le champ 'content' est requis"}), 400

    post, error = facade.create_post(current_user_id, data['content'])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": post}), 201


# -----------------------------------------------
# DELETE /posts/<post_id> → supprimer une publication
# Réservé à l'auteur du post
# -----------------------------------------------
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
        description: Forbidden (not the author)
      404:
        description: Post not found
    """
    current_user_id = get_jwt_identity()

    result, error = facade.delete_post(post_id, current_user_id)
    if error:
        status = 404 if error == "Publication introuvable" else 403
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Publication supprimée"}), 200
