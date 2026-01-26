def test_create_event(client):
    """Test: Création d'un événement"""
    # 1. Créer un utilisateur pour être l'auteur
    user_resp = client.post('/api/v1/auth/register', json={
        "username": "EventCreator",
        "email": "creator@example.com",
        "password": "pw",
        "city": "Lyon"
    })
    user_id = user_resp.json['data']['user_id']

    # 2. Créer l'événement
    response = client.post('/api/v1/events/', json={
        "title": "Soirée Monopoly",
        "game_name": "Monopoly",
        "city": "Lyon",
        "event_date": "2026-12-25",
        "event_time": "20:00:00",
        "max_participants": 4,
        "user_id": user_id
    })

    assert response.status_code == 201
    assert response.json['title'] == "Soirée Monopoly"

def test_get_events(client):
    """Test: Récupérer la liste des événements"""
    response = client.get('/api/v1/events/')
    assert response.status_code == 200
    assert isinstance(response.json, list)
