from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# POST /reviews → soumettre un avis
# Body: { rating, comment?, event_id? | reviewed_user_id? }
# Cibles mutuellement exclusives : event_id XOR reviewed_user_id
# -----------------------------------------------
@api_v1.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    """
    Submit a review
    ---
    tags:
      - Reviews
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
            - rating
          properties:
            rating:
              type: integer
              description: "Note de 1 à 5"
              example: 4
            comment:
              type: string
              example: "Super soirée, très bonne ambiance !"
            event_id:
              type: integer
              description: "ID de l'événement à noter (exclusif avec reviewed_user_id)"
              example: 1
            reviewed_user_id:
              type: integer
              description: "ID du joueur à noter (exclusif avec event_id)"
              example: 2
    responses:
      201:
        description: Review submitted
      400:
        description: Invalid input
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    review, error = facade.create_review(current_user_id, data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": review}), 201


# -----------------------------------------------
# GET /users/<user_id>/reviews → avis reçus par un joueur
# -----------------------------------------------
@api_v1.route('/users/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    """
    Get reviews for a user
    ---
    tags:
      - Reviews
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of reviews
      404:
        description: User not found
    """
    reviews, error = facade.get_reviews_by_user(user_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify({"success": True, "data": reviews}), 200


# -----------------------------------------------
# GET /events/<event_id>/reviews → avis sur un événement
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>/reviews', methods=['GET'])
def get_event_reviews(event_id):
    """
    Get reviews for an event
    ---
    tags:
      - Reviews
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of reviews
      404:
        description: Event not found
    """
    reviews, error = facade.get_reviews_by_event(event_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify({"success": True, "data": reviews}), 200


# -----------------------------------------------
# DELETE /reviews/<review_id> → supprimer son avis
# -----------------------------------------------
@api_v1.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """
    Delete a review
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    parameters:
      - name: review_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Review deleted
      403:
        description: Not the author
      404:
        description: Review not found
    """
    current_user_id = get_jwt_identity()
    result, error = facade.delete_review(review_id, current_user_id)
    if error:
        status = 404 if "introuvable" in error else 403
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Avis supprimé"}), 200
