from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# GET /events → liste des événements
# Filtres optionnels : ?city=Paris&date=2026-03-01
# -----------------------------------------------
@api_v1.route('/events', methods=['GET'])
def list_events():
    """
List events
---
tags:
  - Events
parameters:
  - in: query
    name: city
    type: string
  - in: query
    name: date
    type: string
responses:
  200:
    description: List of events
"""
    city = request.args.get('city')
    date = request.args.get('date')

    events = facade.get_events(city=city, date=date)
    return jsonify({"success": True, "data": events}), 200


# -----------------------------------------------
# POST /events → créer un événement
# -----------------------------------------------
@api_v1.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    """
Create event
---
tags:
  - Events
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
        - title
        - game_id
        - city
        - location_text
        - event_start
        - max_participants
      properties:
        title:
          type: string
        game_id:
          type: string
        city:
          type: string
        location_text:
          type: string
        event_start:
          type: string
        max_participants:
          type: integer
responses:
  201:
    description: Event created
  401:
    description: Unauthorized
"""

    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    # Champs obligatoires
    required = ['title', 'game_id', 'city', 'location_text', 'event_start', 'max_participants']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Champ '{field}' manquant"}), 400

    new_event = facade.create_event(data, current_user_id)

    if "error" in new_event:
        return jsonify({"error": new_event["error"]}), 400

    return jsonify({"success": True, "data": new_event}), 201


# -----------------------------------------------
# GET /events/<event_id> → détails d'un événement
# -----------------------------------------------
@api_v1.route('/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """
    Get event details
    ---
    tags:
      - Events
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Event details
      404:
        description: Event not found
    """
    event = facade.get_event_details(event_id)

    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    return jsonify({"success": True, "data": event}), 200


# -----------------------------------------------
# PUT /events/<event_id> → modifier un événement
# Seulement le créateur peut modifier
# -----------------------------------------------
@api_v1.route('/events/<event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """
    Update event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Event updated
      403:
        description: Forbidden
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    # Seulement le créateur peut modifier
    if event['creator_id'] != current_user_id:
        return jsonify({"error": "Vous n'êtes pas le créateur de cet événement"}), 403

    # Pas de modif sur un event annulé ou terminé
    if event['status'] in ['cancelled', 'completed']:
        return jsonify({"error": "Impossible de modifier un événement annulé ou terminé"}), 400

    updated_event = facade.update_event(event_id, data)
    if not updated_event:
        return jsonify({"error": "Erreur lors de la mise à jour"}), 500

    return jsonify({"success": True, "data": updated_event}), 200


# -----------------------------------------------
# DELETE /events/<event_id> → annuler un événement
# Seulement le créateur peut annuler
# -----------------------------------------------
@api_v1.route('/events/<event_id>', methods=['DELETE'])
@jwt_required()
def cancel_event(event_id):
    """
    Cancel event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Event cancelled
    """
    current_user_id = get_jwt_identity()

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    # Seulement le créateur peut annuler
    if event['creator_id'] != current_user_id:
        return jsonify({"error": "Vous n'êtes pas le créateur de cet événement"}), 403

    if event['status'] == 'cancelled':
        return jsonify({"error": "Cet événement est déjà annulé"}), 400

    result, error = facade.cancel_event(event_id, current_user_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Événement annulé"}), 200


# -----------------------------------------------
# POST /events/<event_id>/join → rejoindre un événement
# -----------------------------------------------
@api_v1.route('/events/<event_id>/join', methods=['POST'])
@jwt_required()
def join_event(event_id):
    """
    Join event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
    responses:
      201:
        description: Joined event
    """
    current_user_id = get_jwt_identity()

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    # Le créateur ne peut pas rejoindre son propre event
    if event['creator_id'] == current_user_id:
        return jsonify({"error": "Vous êtes déjà le créateur de cet événement"}), 400

    if event['status'] != 'open':
        return jsonify({"error": "Cet événement n'accepte plus de participants"}), 400

    participation, error = facade.join_event(event_id, current_user_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": participation}), 201


# -----------------------------------------------
# POST /events/<event_id>/leave → quitter un événement
# -----------------------------------------------
@api_v1.route('/events/<event_id>/leave', methods=['POST'])
@jwt_required()
def leave_event(event_id):
    """
    Leave event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Left event
    """
    current_user_id = get_jwt_identity()

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    # Le créateur ne peut pas quitter son propre event
    if event['creator_id'] == current_user_id:
        return jsonify({"error": "Vous êtes le créateur, annulez l'événement si besoin"}), 400

    result, error = facade.leave_event(event_id, current_user_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Vous avez quitté l'événement"}), 200


# -----------------------------------------------
# GET /events/<event_id>/comments → voir les commentaires
# -----------------------------------------------
@api_v1.route('/events/<event_id>/comments', methods=['GET'])
def get_event_comments(event_id):
    """
    Get event comments
    ---
    tags:
      - Events
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: List of comments
    """
    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    comments = facade.get_event_comments(event_id)
    return jsonify({"success": True, "data": comments}), 200


# -----------------------------------------------
# POST /events/<event_id>/comments → ajouter un commentaire
# -----------------------------------------------
@api_v1.route('/events/<event_id>/comments', methods=['POST'])
@jwt_required()
def add_event_comment(event_id):
    """
    Add comment to event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
    responses:
      201:
        description: Comment added
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('content'):
        return jsonify({"error": "Le contenu du commentaire est requis"}), 400

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    comment, error = facade.add_comment(event_id, current_user_id, data['content'])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": comment}), 201
