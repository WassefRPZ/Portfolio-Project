"""Tests de la recherche globale."""

import pytest
from tests.conftest import auth


class TestGlobalSearch:

    def test_search_finds_users(self, client, user_a, user_b):
        resp = client.get('/api/v1/search?q=UserA',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'users' in data
        assert 'events' in data
        assert any(u['username'] == 'UserA' for u in data['users'])

    def test_search_finds_events(self, client, app, user_a, mock_ext):
        from tests.conftest import make_game
        gid = make_game(app)
        client.post('/api/v1/events', json={
            'title': 'Soirée Catan Unique',
            'game_id': gid,
            'location_text': 'Paris',
            'date_time': '2030-06-15T19:00:00',
            'max_players': 4,
        }, headers=auth(user_a['token']))

        resp = client.get('/api/v1/search?q=Unique',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        events = resp.get_json()['data']['events']
        assert any('Unique' in e['title'] for e in events)

    def test_search_no_email_leak(self, client, user_a, user_b):
        """La recherche globale ne doit PAS exposer les emails."""
        resp = client.get('/api/v1/search?q=User',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        users = resp.get_json()['data']['users']
        for u in users:
            assert 'email' not in u

    def test_search_missing_q_400(self, client, user_a):
        resp = client.get('/api/v1/search',
                          headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_search_empty_q_400(self, client, user_a):
        resp = client.get('/api/v1/search?q=',
                          headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_search_no_match_returns_empty_lists(self, client, user_a):
        resp = client.get('/api/v1/search?q=zzznomatch',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert data['users'] == []
        assert data['events'] == []
