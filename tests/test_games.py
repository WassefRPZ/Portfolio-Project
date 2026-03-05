"""Tests des endpoints jeux."""

import pytest
from tests.conftest import auth, make_game


class TestListGames:

    def test_get_all_games(self, client, app):
        make_game(app, 'Catan')
        make_game(app, 'Dixit')
        resp = client.get('/api/v1/games')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert len(data) == 2

    def test_get_all_games_empty(self, client):
        resp = client.get('/api/v1/games')
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []

    def test_get_popular_games_no_auth(self, client):
        resp = client.get('/api/v1/games/popular')
        assert resp.status_code == 200

    def test_get_game_by_id(self, client, app):
        gid = make_game(app, 'Monopoly')
        resp = client.get(f'/api/v1/games/{gid}')
        assert resp.status_code == 200
        assert resp.get_json()['data']['name'] == 'Monopoly'

    def test_get_game_unknown_404(self, client):
        resp = client.get('/api/v1/games/99999')
        assert resp.status_code == 404


class TestSearchGames:

    def test_search_no_auth(self, client, app):
        """La recherche de jeux est publique (pas de JWT requis)."""
        make_game(app, 'Ticket to Ride')
        resp = client.get('/api/v1/games/search?q=Ticket')
        assert resp.status_code == 200
        assert any(g['name'] == 'Ticket to Ride'
                   for g in resp.get_json()['data'])

    def test_search_missing_q_400(self, client):
        resp = client.get('/api/v1/games/search')
        assert resp.status_code == 400

    def test_search_no_match(self, client, app):
        make_game(app, 'Catan')
        resp = client.get('/api/v1/games/search?q=zzznomatch')
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []


class TestGameEvents:

    def test_get_events_for_game(self, client, app, user_a, mock_ext):
        gid = make_game(app)
        client.post('/api/v1/events', json={
            'title': 'Soirée', 'game_id': gid,
            'location_text': 'Paris', 'date_time': '2030-01-01T18:00:00',
            'max_players': 4,
        }, headers=auth(user_a['token']))

        resp = client.get(f'/api/v1/games/{gid}/events',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert len(resp.get_json()['data']) == 1
