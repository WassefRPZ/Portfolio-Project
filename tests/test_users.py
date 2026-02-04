def test_get_my_profile(client):
    """Doit récupérer ses propres infos"""
    # 1. Inscription
    resp = client.post('/api/v1/auth/register', json={
        "username": "ProfileUser", "email": "prof@test.com", "password": "pw", "city": "Lyon"
    })
    user_id = resp.json['data']['id']

    # 2. Appel de la route protégée avec le Header
    response = client.get('/api/v1/users/me', headers={
        'X-User-ID': user_id
    })
    
    assert response.status_code == 200
    assert response.json['username'] == "ProfileUser"
    assert response.json['city'] == "Lyon"

def test_update_profile(client):
    """Doit mettre à jour la bio"""
    # 1. Inscription
    resp = client.post('/api/v1/auth/register', json={
        "username": "UpdateUser", "email": "up@test.com", "password": "pw"
    })
    user_id = resp.json['data']['id']

    # 2. Mise à jour
    response = client.put('/api/v1/users/me', json={
        "bio": "Nouvelle bio super cool"
    }, headers={'X-User-ID': user_id})

    assert response.status_code == 200
    assert response.json['bio'] == "Nouvelle bio super cool"
    