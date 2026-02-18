"""
============================================
Routes événements
============================================
"""
from flask import Blueprint, request, jsonify
from app.services.facade import BoardGameFacade
from app.utils.auth import token_required, optional_token

events_ns = Blueprint('events', __name__)
facade = BoardGameFacade()

@events_ns.route('', methods=['GET'])
@optional_token
def list_events(current_user_id):
    """
    GET /api/v1/events?city=<city>&date=<date>
    Headers: Authorization: Bearer <token> (optionnel)
    """
    city = request.args.get('city')
    date = request.args.get('date')
    
    events = facade.get_events(city=city, date=date)
    
    return jsonify({"success": True, "data": events}), 200

@events_ns.route('', methods=['POST'])
@token_required
def create_event(current_user_id):
    """
    POST /api/v1/events
    Headers: Authorization: Bearer <token>
    Body: {
        "title", "game_id", "city", "location_text",
        "event_start", "max_participants",
        "description"?, "latitude"?, "longitude"?
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "Pas de données envoyées"}), 400
    
    new_event = facade.create_event(data, current_user_id)
    
    if "error" in new_event:
        return jsonify({"success": False, "error": new_event["error"]}), 400
    
    return jsonify({"success": True, "data": new_event}), 201

@events_ns.route('/<event_id>', methods=['GET'])
@optional_token
def get_event_details(current_user_id, event_id):
    """
    GET /api/v1/events/<event_id>
    Headers: Authorization: Bearer <token> (optionnel)
    """
    event = facade.get_event_details(event_id)
    
    if not event:
        return jsonify({"success": False, "error": "Événement introuvable"}), 404
    
    return jsonify({"success": True, "data": event}), 200

@events_ns.route('/<event_id>', methods=['PUT'])
@token_required
def update_event(current_user_id, event_id):
    """
    PUT /api/v1/events/<event_id>
    Headers: Authorization: Bearer <token>
    Body: { champs à modifier }
    """
    data = request.get_json()
    
    # Appel à la nouvelle méthode facade.update_event
    response, status_code = facade.update_event(event_id, current_user_id, data)
    
    return jsonify(response), status_code

@events_ns.route('/<event_id>', methods=['DELETE'])
@token_required
def cancel_event(current_user_id, event_id):
    """
    DELETE /api/v1/events/<event_id>
    Headers: Authorization: Bearer <token>
    """
    # Appel à la nouvelle méthode facade.cancel_event
    response, status_code = facade.cancel_event(event_id, current_user_id)
    
    return jsonify(response), status_code

@events_ns.route('/<event_id>/join', methods=['POST'])
@token_required
def join_event(current_user_id, event_id):
    """
    POST /api/v1/events/<event_id>/join
    Headers: Authorization: Bearer <token>
    """
    participation, error = facade.join_event(event_id, current_user_id)
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    return jsonify({"success": True, "data": participation}), 201

@events_ns.route('/<event_id>/leave', methods=['POST'])
@token_required
def leave_event(current_user_id, event_id):
    """
    POST /api/v1/events/<event_id>/leave
    Headers: Authorization: Bearer <token>
    """
    result, error = facade.leave_event(event_id, current_user_id)
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    return jsonify({"success": True, "message": "Vous avez quitté l'événement"}), 200

@events_ns.route('/<event_id>/comments', methods=['GET'])
@optional_token
def get_event_comments(current_user_id, event_id):
    """
    GET /api/v1/events/<event_id>/comments
    Headers: Authorization: Bearer <token> (optionnel)
    """
    # TODO: Implémenter la récupération des commentaires (Fonctionnalité "Could Have")
    return jsonify({"success": True, "data": []}), 200

@events_ns.route('/<event_id>/comments', methods=['POST'])
@token_required
def add_event_comment(current_user_id, event_id):
    """
    POST /api/v1/events/<event_id>/comments
    Headers: Authorization: Bearer <token>
    Body: { "content" }
    """
    # TODO: Implémenter l'ajout de commentaire (Fonctionnalité "Could Have")
    return jsonify({"success": False, "error": "Fonctionnalité à venir"}), 501
