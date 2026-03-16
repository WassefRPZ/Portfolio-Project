"""
Routes des événements : listing filtré, création, mise à jour, participation et commentaires.
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1
from app.services import facade


@api_v1.route('/events', methods=['GET'])
@jwt_required()
def list_events():
    """
    Liste les événements ouverts avec pagination et filtres multiples.
    """
    city = request.args.get('city')  # Filtre par ville
    date = request.args.get('date')  # Filtre par date

    # Valide et limite les paramètres de pagination
    try:
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 par page
        offset = max(int(request.args.get('offset', 0)), 0)  # Min 0
    except (ValueError, TypeError):
        limit, offset = 50, 0  # Valeurs par défaut en cas d'erreur

    # Paramètres de géolocalisation
    lat = request.args.get('lat', type=float)  # Latitude du centre de recherche
    lng = request.args.get('lng', type=float)  # Longitude du centre de recherche
    radius = request.args.get('radius', default=10, type=float)  # Rayon en km
    if radius is not None:
        radius = min(max(radius, 0), 200)  # Valide le rayon

    # Appelle le service métier avec tous les filtres
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
    """
    Crée un nouvel événement lancé par l'utilisateur connecté.
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    # Détecte le type de contenu pour traiter formulaires multipart ou JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()  # Données du formulaire
        image_file = request.files.get('cover')  # Fichier image
        # Convertit les champs numériques qui viennent en string du formulaire
        for int_field in ['game_id', 'max_players']:
            if int_field in data:
                try:
                    data[int_field] = int(data[int_field])  # Conversion string -> int
                except ValueError:
                    return jsonify({"error": f"'{int_field}' doit être un entier"}), 400
    else:
        data = request.get_json(silent=True)  # Données JSON
        image_file = None

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    # Valide les champs obligatoires
    required = ['title', 'game_id', 'location_text', 'date_time', 'max_players']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Champ '{field}' manquant"}), 400

    # Crée l'événement via le service métier
    new_event, error = facade.create_event(data, current_user_id, image_file)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": new_event}), 201


@api_v1.route('/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    """
    Récupère les détails complets d'un événement.
    Inclut le créateur, les participants, les commentaires et la géolocalisation.
    """
    event = facade.get_event_details(event_id)  # Récupère l'événement avec relations

    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    return jsonify({"success": True, "data": event}), 200


@api_v1.route('/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """
    Met à jour un événement existant.
    Seul le créateur de l'événement peut le modifier.
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    data = request.get_json(silent=True)  # Récupère les données JSON

    if not data:
        return jsonify({"error": "Pas de données envoyées"}), 400

    # Appelle le service métier avec vérification d'autorisation
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
    """
    Annule un événement existant.
    Seul le créateur de l'événement peut l'annuler.
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    # Appelle le service métier avec vérification d'autorisation
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
    """
    Ajoute l'utilisateur connecté comme participant à un événement.
    Crée une relation EventParticipant avec le statut 'confirmed'.
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    # Crée la participation via le service métier
    participation, error = facade.join_event(event_id, current_user_id)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "data": participation}), 201


@api_v1.route('/events/<int:event_id>/leave', methods=['POST'])
@jwt_required()
def leave_event(event_id):
    """
    Retire l'utilisateur connecté de la liste des participants d'un événement.
    Supprime la relation EventParticipant.
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT

    # Supprime la participation via le service métier
    result, error = facade.leave_event(event_id, current_user_id)
    if error:
        status = 404 if "introuvable" in error else 400
        return jsonify({"error": error}), status

    return jsonify({"success": True, "message": "Vous avez quitté l'événement"}), 200


@api_v1.route('/events/<int:event_id>/comment', methods=['GET'])
@jwt_required()
def get_event_comments(event_id):
    """
    Récupère les commentaires d'un événement avec pagination.
    """
    event = facade.get_event(event_id)  # Vérifie que l'événement existe
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    # Valide et limite les paramètres de pagination
    try:
        limit  = min(int(request.args.get('limit',  50)), 100)  # Max 100 par page
        offset = max(int(request.args.get('offset',  0)),   0)  # Min 0
    except (ValueError, TypeError):
        limit, offset = 50, 0  # Valeurs par défaut en cas d'erreur

    comments = facade.get_event_comments(event_id, limit=limit, offset=offset)  # Récupère la page
    return jsonify({"success": True, "data": comments, "limit": limit, "offset": offset}), 200


@api_v1.route('/events/<int:event_id>/comment', methods=['POST'])
@jwt_required()
def add_event_comment(event_id):
    """
    Ajoute un commentaire à un événement.
    """
    current_user_id = int(get_jwt_identity())  # Extrait l'ID du token JWT
    data = request.get_json(silent=True)  # Récupère les données JSON

    # Valide que le contenu du commentaire est présent et non vide
    if not data or not data.get('content', '').strip():
        return jsonify({"error": "Le contenu du commentaire est requis"}), 400

    # Vérifie que l'événement existe
    event = facade.get_event(event_id)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404

    # Crée le commentaire via le service métier
    comment, error = facade.add_comment(event_id, current_user_id, data['content'].strip())
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True, "data": comment}), 201
