"""Tests des endpoints utilisateurs."""

import pytest
from tests.conftest import register, login, auth, VALID_PASSWORD


class TestMyProfile:

    def test_get_my_profile_ok(self, client, user_a):
        resp = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert data['email'] == user_a['email']

    def test_get_my_profile_no_auth(self, client):
        resp = client.get('/api/v1/users/me')
        assert resp.status_code == 401

    def test_update_profile_username(self, client, user_a):
        resp = client.put('/api/v1/users/me', json={'username': 'NewName'},
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data']['username'] == 'NewName'

    def test_update_profile_bio(self, client, user_a):
        resp = client.put('/api/v1/users/me', json={'bio': 'Passionné de Catan'},
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data']['bio'] == 'Passionné de Catan'

    def test_update_profile_no_auth(self, client):
        resp = client.put('/api/v1/users/me', json={'bio': 'test'})
        assert resp.status_code == 401

    def test_update_profile_empty_body(self, client, user_a):
        resp = client.put('/api/v1/users/me', json={},
                          headers=auth(user_a['token']))
        assert resp.status_code == 400


class TestPublicProfile:

    def test_get_public_profile(self, client, user_a, user_b):
        # Trouver l'id de user_b via /users/me
        me = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        user_b_id = me.get_json()['data']['id']

        resp = client.get(f'/api/v1/users/{user_b_id}',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        data = resp.get_json()['data']
        # La vue publique ne doit PAS exposer l'email
        assert 'email' not in data
        assert data['username'] == user_b['username']

    def test_get_unknown_user_404(self, client, user_a):
        resp = client.get('/api/v1/users/99999', headers=auth(user_a['token']))
        assert resp.status_code == 404


class TestSearchUsers:

    def test_search_by_username(self, client, user_a, user_b):
        resp = client.get('/api/v1/users/search?q=UserB',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        results = resp.get_json()['data']
        assert any(u['username'] == 'UserB' for u in results)

    def test_search_no_param_returns_400(self, client, user_a):
        resp = client.get('/api/v1/users/search', headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_search_results_no_email(self, client, user_a, user_b):
        """Les résultats de recherche ne doivent pas exposer l'email."""
        resp = client.get('/api/v1/users/search?q=UserB',
                          headers=auth(user_a['token']))
        results = resp.get_json()['data']
        for u in results:
            assert 'email' not in u


class TestMyEvents:

    def test_get_my_events_empty(self, client, user_a):
        resp = client.get('/api/v1/users/me/events',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert data == [] or isinstance(data, list)


class TestFavoriteGames:

    def test_get_favorites_empty(self, client, user_a):
        resp = client.get('/api/v1/users/me/favorite-games',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []

    def test_add_and_get_favorite(self, client, app, user_a):
        from tests.conftest import make_game
        gid = make_game(app)

        resp = client.post('/api/v1/users/me/favorite-games',
                           json={'game_id': gid},
                           headers=auth(user_a['token']))
        assert resp.status_code == 201
        # La réponse doit être le jeu complet (pas juste les IDs)
        data = resp.get_json()['data']
        assert 'name' in data
        assert 'min_players' in data

    def test_add_duplicate_favorite_400(self, client, app, user_a):
        from tests.conftest import make_game
        gid = make_game(app)
        client.post('/api/v1/users/me/favorite-games',
                    json={'game_id': gid}, headers=auth(user_a['token']))
        resp = client.post('/api/v1/users/me/favorite-games',
                           json={'game_id': gid}, headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_remove_favorite(self, client, app, user_a):
        from tests.conftest import make_game
        gid = make_game(app)
        client.post('/api/v1/users/me/favorite-games',
                    json={'game_id': gid}, headers=auth(user_a['token']))
        resp = client.delete(f'/api/v1/users/me/favorite-games/{gid}',
                             headers=auth(user_a['token']))
        assert resp.status_code == 200
