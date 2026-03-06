from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/events', methods=['GET'])
@jwt_required()
def list_events():
    city = request.args.get('city')
    date = request.args.get('date')

    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
    except (ValueError, TypeError):
        limit, offset = 50, 0

    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=10, type=float)
    if radius is not None:
        radius = min(max(radius, 0), 200)

    events, total_count, error = facade.get_events(
        city=city, date=date, limit=limit, offset=offset,
        lat=lat, lng=lng, radius=radius,
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True, "data": events, "total_count": total_count}), 200


@api_v1.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    current_user_id = int(get_jwt_identity())

    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        image_file = request.files.get('cover')
        for int_field in ['game_id', 'max_players']:
            if int_field in data:
                try:
                    data[int_field] = int(data[int_field])
                except ValueError:
                    return jsonify({"error": f"'{int_field}' doit être un entier"}), 400
    else:
        data = request.get_json(silent=True)
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


@api_v1.route('/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    event = facade.get_event_details(event_id)

    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    return jsonify({"success": True, "data": event}), 200


@api_v1.route('/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    updated_event, error = facade.update_event(event_id, current_user_id, data)
    if error:
        if error == "forbidden":
            return jsonify({"error": "Vous n'êtes pas le créateur de cet événement"}), 403
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "data": updated_event}), 200


@api_v1.route('/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def cancel_event(event_id):
    current_user_id = int(get_jwt_identity())

    result, error = facade.cancel_event(event_id, current_user_id)
    if error:
        if error == "forbidden":
            return jsonify({"error": "Vous n'êtes pas le créateur de cet événement"}), 403
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Événement annulé"}), 200


@api_v1.route('/events/<int:event_id>/join', methods=['POST'])
@jwt_required()
def join_event(event_id):
    current_user_id = int(get_jwt_identity())

    participation, error = facade.join_event(event_id, current_user_id)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "data": participation}), 201


@api_v1.route('/events/<int:event_id>/leave', methods=['POST'])
@jwt_required()
def leave_event(event_id):
    current_user_id = int(get_jwt_identity())

    result, error = facade.leave_event(event_id, current_user_id)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Vous avez quitté l'événement"}), 200


@api_v1.route('/events/<int:event_id>/comment', methods=['GET'])
@jwt_required()
def get_event_comments(event_id):
    event = facade.get_event(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    try:
        limit  = min(int(request.args.get('limit',  50)), 100)
        offset = max(int(request.args.get('offset',  0)),   0)
    except (ValueError, TypeError):
        limit, offset = 50, 0

    comments = facade.get_event_comments(event_id, limit=limit, offset=offset)
    return jsonify({"success": True, "data": comments, "limit": limit, "offset": offset}), 200


@api_v1.route('/events/<int:event_id>/comment', methods=['POST'])
@jwt_required()
def add_event_comment(event_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)

    if not data or not data.get('content', '').strip():
        return jsonify({"error": "Le contenu du commentaire est requis"}), 400

    event = facade.get_event(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    comment, error = facade.add_comment(event_id, current_user_id, data['content'].strip())
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": comment}), 201
