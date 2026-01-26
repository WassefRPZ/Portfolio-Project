def test_friend_request_flow(client):
    """Scenario complet : User1 demande User2 en ami, User2 accepte"""
    
    # 1. Création User 1
    r1 = client.post('/api/v1/auth/register', json={"username": "U1", "email": "u1@t.com", "password": "pw"})
    id1 = r1.json['data']['id']

    # 2. Création User 2
    r2 = client.post('/api/v1/auth/register', json={"username": "U2", "email": "u2@t.com", "password": "pw"})
    id2 = r2.json['data']['id']

    # 3. U1 envoie une demande à U2
    req_resp = client.post(f'/api/v1/friends/request/{id2}', headers={'X-User-ID': id1})
    assert req_resp.status_code == 201
    assert req_resp.json['data']['status'] == 'pending'

    # 4. U2 accepte la demande de U1
    acc_resp = client.post(f'/api/v1/friends/accept/{id1}', headers={'X-User-ID': id2})
    assert acc_resp.status_code == 200
    assert acc_resp.json['success'] is True
    