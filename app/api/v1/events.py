from flask import request, jsonify
from app.services.facade import BoardGameFacade
from app.api.v1 import api_v1

facade = BoardGameFacade()

@api_v1.route('/events', methods=['GET'])
def list_events():
    events = facade.get_events()
    return jsonify(events), 200

@api_v1.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    creator_id = request.headers.get('X-User-ID', data.get('user_id', 'usr_001'))
    
    new_event = facade.create_event(data, creator_id)
    return jsonify(new_event), 201
