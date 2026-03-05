from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()


# -----------------------------------------------
# GET /events → liste des événements
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
    description: "Date ISO 8601 (ex: 2024-12-25)"
responses:
  200:
    description: List of events
  400:
    description: Invalid date format
"""
    city = request.args.get('city')
    date = request.args.get('date')

    events, error = facade.get_events(city=city, date=date)
    if error:
        return jsonify({"error": error}), 400
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
  - multipart/form-data
  - application/json
parameters:
  - in: formData
    name: cover
    type: file
    description: "Image de couverture (JPEG/PNG) — upload vers Cloudinary"
  - in: formData
    name: title
    type: string
    required: true
  - in: formData
    name: game_id
    type: integer
    required: true
  - in: formData
    name: location_text
    type: string
    required: true
    description: "Adresse complète — ville et région extraites automatiquement via OpenCage"
  - in: formData
    name: date_time
    type: string
    required: true
    description: "ISO 8601 (ex: 2024-12-25T19:00:00)"
  - in: formData
    name: max_players
    type: integer
    required: true
  - in: formData
    name: description
    type: string
responses:
  201:
    description: Event created
  400:
    description: Invalid input or upload error
  401:
    description: Unauthorized
"""
    current_user_id = get_jwt_identity()

    # Support multipart/form-data (avec fichier) ou application/json (sans fichier)
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        image_file = request.files.get('cover')
        # Convertir les champs entiers (form-data envoie tout en string)
        for int_field in ['game_id', 'max_players']:
            if int_field in data:
                try:
                    data[int_field] = int(data[int_field])
                except ValueError:
                    return jsonify({"error": f"'{int_field}' doit être un entier"}), 400
    else:
        data = request.get_json()
        image_file = None

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    required = ['title', 'game_id', 'location_text', 'date_time', 'max_players']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Champ '{field}' manquant"}), 400

    new_event, error = facade.create_event(data, current_user_id, image_file)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": new_event}), 201


# -----------------------------------------------
# GET /events/<event_id> → détails d'un événement
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """
    Get event details
    ---
    tags:
      - Events
    parameters:
      - name: event_id
        in: path
        type: integer
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
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>', methods=['PUT'])
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
        type: integer
        required: true
    responses:
      200:
        description: Event updated
      400:
        description: Invalid input
      403:
        description: Forbidden
      404:
        description: Event not found
    """
    current_user_id = get_jwt_identity()
    role = get_jwt().get('role', 'user')
    data = request.get_json()

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    if event['creator_id'] != current_user_id and role != 'admin':
        return jsonify({"error": "Vous n'êtes pas le créateur de cet événement"}), 403

    if event['status'] in ['cancelled', 'completed']:
        return jsonify({"error": "Impossible de modifier un événement annulé ou terminé"}), 400

    updated_event, error = facade.update_event(event_id, data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": updated_event}), 200


# -----------------------------------------------
# DELETE /events/<event_id> → annuler un événement
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>', methods=['DELETE'])
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
        type: integer
        required: true
    responses:
      200:
        description: Event cancelled
      403:
        description: Forbidden
      404:
        description: Event not found
    """
    current_user_id = get_jwt_identity()
    role = get_jwt().get('role', 'user')

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    if event['creator_id'] != current_user_id and role != 'admin':
        return jsonify({"error": "Vous n'êtes pas le créateur de cet événement"}), 403

    if event['status'] == 'cancelled':
        return jsonify({"error": "Cet événement est déjà annulé"}), 400

    # cancel_event ne prend plus user_id (auth déjà vérifiée ci-dessus)
    result, error = facade.cancel_event(event_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Événement annulé"}), 200


# -----------------------------------------------
# POST /events/<event_id>/join → rejoindre un événement
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>/join', methods=['POST'])
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
        type: integer
        required: true
    responses:
      201:
        description: Joined event
      400:
        description: Cannot join
      404:
        description: Event not found
    """
    current_user_id = get_jwt_identity()

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

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
@api_v1.route('/events/<int:event_id>/leave', methods=['POST'])
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
        type: integer
        required: true
    responses:
      200:
        description: Left event
      400:
        description: Cannot leave
      404:
        description: Event not found
    """
    current_user_id = get_jwt_identity()

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    if event['creator_id'] == current_user_id:
        return jsonify({"error": "Vous êtes le créateur, annulez l'événement si besoin"}), 400

    result, error = facade.leave_event(event_id, current_user_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "message": "Vous avez quitté l'événement"}), 200


# -----------------------------------------------
# GET /events/<event_id>/comments → voir les commentaires
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>/comments', methods=['GET'])
def get_event_comments(event_id):
    """
    Get event comments
    ---
    tags:
      - Events
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of comments
      404:
        description: Event not found
    """
    event = facade.get_event(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    comments = facade.get_event_comments(event_id)
    return jsonify({"success": True, "data": comments}), 200


# -----------------------------------------------
# POST /events/<event_id>/comments → ajouter un commentaire
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>/comments', methods=['POST'])
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
        type: integer
        required: true
    responses:
      201:
        description: Comment added
      400:
        description: Missing content
      404:
        description: Event not found
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('content'):
        return jsonify({"error": "Le contenu du commentaire est requis"}), 400

    event = facade.get_event(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    comment, error = facade.add_comment(event_id, current_user_id, data['content'])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": comment}), 201


# -----------------------------------------------
# DELETE /events/<event_id>/participants/<user_id> → expulser un participant
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>/participants/<int:user_id>', methods=['DELETE'])
@jwt_required()
def kick_participant(event_id, user_id):
    """
    Kick a participant from an event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the participant to remove
    responses:
      200:
        description: Participant removed
      403:
        description: Forbidden — not creator or admin
      404:
        description: Event or participant not found
    """
    current_user_id = get_jwt_identity()
    role = get_jwt().get('role', 'user')

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    if event['creator_id'] != current_user_id and role != 'admin':
        return jsonify({"error": "Réservé au créateur ou à un administrateur"}), 403

    if user_id == event['creator_id']:
        return jsonify({"error": "Impossible d'expulser le créateur de l'événement"}), 400

    result, error = facade.kick_participant(event_id, user_id)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Participant retiré de l'événement"}), 200


# -----------------------------------------------
# POST /events/<event_id>/close → marquer l'événement comme terminé
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>/close', methods=['POST'])
@jwt_required()
def close_event(event_id):
    """
    Close an event (mark as completed)
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Event closed
      400:
        description: Already completed or cancelled
      403:
        description: Forbidden — not creator or admin
      404:
        description: Event not found
    """
    current_user_id = get_jwt_identity()
    role = get_jwt().get('role', 'user')

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    if event['creator_id'] != current_user_id and role != 'admin':
        return jsonify({"error": "Réservé au créateur ou à un administrateur"}), 403

    result, error = facade.close_event(event_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": result}), 200


# -----------------------------------------------
# POST /events/<event_id>/open → rouvrir un événement
# -----------------------------------------------
@api_v1.route('/events/<int:event_id>/open', methods=['POST'])
@jwt_required()
def open_event(event_id):
    """
    Reopen a closed or full event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Event reopened
      400:
        description: Cannot reopen (already open or cancelled)
      403:
        description: Forbidden — not creator or admin
      404:
        description: Event not found
    """
    current_user_id = get_jwt_identity()
    role = get_jwt().get('role', 'user')

    event = facade.get_event_details(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    if event['creator_id'] != current_user_id and role != 'admin':
        return jsonify({"error": "Réservé au créateur ou à un administrateur"}), 403

    result, error = facade.open_event(event_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": result}), 200
