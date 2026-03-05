from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


# -----------------------------------------------
# GET /posts → fil d'actualité avec pagination (offset/limit)
# -----------------------------------------------
@api_v1.route('/posts', methods=['GET'])
@jwt_required()
def get_feed():
    """
    Get the news feed (paginated)
    ---
    tags:
      - Posts
    security:
      - Bearer: []
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        description: "Nombre de posts à retourner (défaut 20, max 50)"
      - name: offset
        in: query
        type: integer
        required: false
        description: "Nombre de posts à sauter (scroll infini)"
    responses:
      200:
        description: List of posts
    """
    current_user_id = int(get_jwt_identity())
    try:
        limit  = min(int(request.args.get('limit',  20)), 50)
        offset = max(int(request.args.get('offset',  0)),  0)
    except (ValueError, TypeError):
        limit, offset = 20, 0

    posts = facade.get_feed(limit=limit, offset=offset, current_user_id=current_user_id)
    return jsonify({"success": True, "data": posts, "limit": limit, "offset": offset}), 200


# -----------------------------------------------
# POST /posts → créer une publication
# multipart/form-data : content, post_type, image (file)
# ou application/json : content, post_type
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

    post, error = facade.create_post(
        author_id=current_user_id,
        content=content,
        image_file=image_file,
        post_type=post_type,
    )
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": post}), 201


# -----------------------------------------------
# DELETE /posts/<post_id> → supprimer son post
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
        description: Not the author
      404:
        description: Post not found
    """
    current_user_id = int(get_jwt_identity())
    result, error = facade.delete_post(post_id, current_user_id)
    if error:
        status = 404 if "introuvable" in error else 403
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Publication supprimée"}), 200


# -----------------------------------------------
# POST /posts/<post_id>/like → liker un post
# -----------------------------------------------
@api_v1.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """
    Like a post
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
        description: Post liked
      400:
        description: Déjà liké
      404:
        description: Post introuvable
    """
    current_user_id = int(get_jwt_identity())
    result, error = facade.like_post(current_user_id, post_id)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "data": result}), 200


# -----------------------------------------------
# DELETE /posts/<post_id>/like → retirer son like
# -----------------------------------------------
@api_v1.route('/posts/<int:post_id>/like', methods=['DELETE'])
@jwt_required()
def unlike_post(post_id):
    """
    Unlike a post
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
        description: Like retiré
      400:
        description: Pas encore liké
      404:
        description: Post introuvable
    """
    current_user_id = int(get_jwt_identity())
    result, error = facade.unlike_post(current_user_id, post_id)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "data": result}), 200


# -----------------------------------------------
# GET /posts/<post_id>/comments → commentaires d'un post
# -----------------------------------------------
@api_v1.route('/posts/<int:post_id>/comments', methods=['GET'])
@jwt_required()
def get_post_comments(post_id):
    """
    Get comments for a post
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
        description: List of comments
      404:
        description: Post introuvable
    """
    result, error = facade.get_post_comments(post_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify({"success": True, "data": result}), 200


# -----------------------------------------------
# POST /posts/<post_id>/comments → commenter un post
# -----------------------------------------------
@api_v1.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_post_comment(post_id):
    """
    Add a comment to a post
    ---
    tags:
      - Posts
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
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
              example: "Bonne idée, je viens !"
    responses:
      201:
        description: Comment added
      400:
        description: Contenu vide
      404:
        description: Post introuvable
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data or not data.get('content'):
        return jsonify({"error": "Le champ 'content' est requis"}), 400

    comment, error = facade.add_post_comment(current_user_id, post_id, data['content'])
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "data": comment}), 201


# -----------------------------------------------
# DELETE /posts/comments/<comment_id> → supprimer son commentaire
# -----------------------------------------------
@api_v1.route('/posts/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_post_comment(comment_id):
    """
    Delete a post comment
    ---
    tags:
      - Posts
    security:
      - Bearer: []
    parameters:
      - name: comment_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Comment deleted
      403:
        description: Not the author
      404:
        description: Comment not found
    """
    current_user_id = int(get_jwt_identity())
    result, error = facade.delete_post_comment(comment_id, current_user_id)
    if error:
        status = 404 if "introuvable" in error else 403
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Commentaire supprimé"}), 200
