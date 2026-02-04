def test_register_success(client):
    """Doit pouvoir inscrire un nouvel utilisateur"""
    response = client.post('/api/v1/auth/register', json={
        "username": "TestUser",
        "email": "test@example.com",
        "password": "password123",
        "city": "Paris"
    })
    assert response.status_code == 201
    assert "id" in response.json['data']

def test_register_duplicate_email(client):
    """Ne doit pas pouvoir inscrire deux fois le même email"""
    # 1er user
    client.post('/api/v1/auth/register', json={
        "username": "User1", "email": "dup@test.com", "password": "123"
    })
    # 2eme user
    response = client.post('/api/v1/auth/register', json={
        "username": "User2", "email": "dup@test.com", "password": "123"
    })
    assert response.status_code == 400
    assert "error" in response.json

def test_login_success(client):
    """Doit pouvoir se connecter avec les bons identifiants"""
    # Création
    client.post('/api/v1/auth/register', json={
        "username": "LoginUser", "email": "login@test.com", "password": "123"
    })
    # Connexion
    response = client.post('/api/v1/auth/login', json={
        "email": "login@test.com",
        "password": "123"
    })
    assert response.status_code == 200
    assert "token" in response.json['data']
