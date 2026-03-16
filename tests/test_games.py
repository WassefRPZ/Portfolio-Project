"""Tests des endpoints jeux."""

import pytest
from tests.conftest import auth, make_game


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
