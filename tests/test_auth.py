"""Tests du système d'authentification."""

import pytest
from tests.conftest import register, login, auth, VALID_PASSWORD


class TestRegister:

    def test_register_success(self, client):
        resp = register(client, 'Alice', 'alice@test.com')
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['user']['email'] == 'alice@test.com'

    def test_register_returns_token(self, client):
        resp = register(client, 'Alice', 'alice@test.com')
        token = resp.get_json()['data']['access_token']
        assert isinstance(token, str) and len(token) > 20

    def test_register_duplicate_email(self, client):
        register(client, 'Alice', 'alice@test.com')
        resp = register(client, 'Alice2', 'alice@test.com')
        assert resp.status_code == 400

    def test_register_duplicate_username(self, client):
        register(client, 'Alice', 'alice@test.com')
        resp = register(client, 'Alice', 'alice2@test.com')
        assert resp.status_code == 400

    def test_register_weak_password_no_uppercase(self, client):
        resp = register(client, 'Bob', 'bob@test.com', password='test@1234')
        assert resp.status_code == 400

    def test_register_weak_password_no_special(self, client):
        resp = register(client, 'Bob', 'bob@test.com', password='TestPass1234')
        assert resp.status_code == 400

    def test_register_weak_password_too_short(self, client):
        resp = register(client, 'Bob', 'bob@test.com', password='T@1a')
        assert resp.status_code == 400

    def test_register_missing_username(self, client):
        resp = client.post('/api/v1/auth/register', json={
            'email': 'bob@test.com', 'password': VALID_PASSWORD, 'city': 'Lyon',
        })
        assert resp.status_code == 400

    def test_register_missing_email(self, client):
        resp = client.post('/api/v1/auth/register', json={
            'username': 'Bob', 'password': VALID_PASSWORD, 'city': 'Lyon',
        })
        assert resp.status_code == 400

    def test_register_no_body(self, client):
        resp = client.post('/api/v1/auth/register')
        assert resp.status_code == 400


class TestLogin:

    def test_login_success(self, client):
        register(client, 'Alice', 'alice@test.com')
        resp = client.post('/api/v1/auth/login', json={
            'email': 'alice@test.com', 'password': VALID_PASSWORD,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']

    def test_login_wrong_password(self, client):
        register(client, 'Alice', 'alice@test.com')
        resp = client.post('/api/v1/auth/login', json={
            'email': 'alice@test.com', 'password': 'WrongPass@1',
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post('/api/v1/auth/login', json={
            'email': 'ghost@test.com', 'password': VALID_PASSWORD,
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post('/api/v1/auth/login', json={'email': 'alice@test.com'})
        assert resp.status_code == 400

    def test_login_no_body(self, client):
        resp = client.post('/api/v1/auth/login')
        assert resp.status_code == 400
