"""Tests du système d'amitié."""

import pytest
from tests.conftest import auth


class TestSendRequest:

    def test_send_request_ok(self, client, user_a, user_b):
        me_b = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        b_id = me_b.get_json()['data']['id']

        resp = client.post(f'/api/v1/friends/request/{b_id}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 201

    def test_send_request_to_self_400(self, client, user_a):
        me = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me.get_json()['data']['id']

        resp = client.post(f'/api/v1/friends/request/{a_id}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_send_duplicate_request_400(self, client, user_a, user_b):
        me_b = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        b_id = me_b.get_json()['data']['id']

        client.post(f'/api/v1/friends/request/{b_id}', headers=auth(user_a['token']))
        resp = client.post(f'/api/v1/friends/request/{b_id}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_send_request_unknown_user_400(self, client, user_a):
        resp = client.post('/api/v1/friends/request/99999',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_send_request_no_auth_401(self, client):
        resp = client.post('/api/v1/friends/request/1')
        assert resp.status_code == 401


class TestPendingRequests:

    def test_get_pending_received(self, client, user_a, user_b):
        me_b = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        b_id = me_b.get_json()['data']['id']
        client.post(f'/api/v1/friends/request/{b_id}', headers=auth(user_a['token']))

        resp = client.get('/api/v1/friends/requests', headers=auth(user_b['token']))
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert len(data) == 1
        # L'email du requester ne doit PAS être exposé
        assert 'email' not in data[0]['requester']

    def test_get_pending_sent(self, client, user_a, user_b):
        me_b = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        b_id = me_b.get_json()['data']['id']
        client.post(f'/api/v1/friends/request/{b_id}', headers=auth(user_a['token']))

        resp = client.get('/api/v1/friends/sent', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert len(resp.get_json()['data']) == 1


class TestAcceptDeclineRequest:

    def _setup(self, client, user_a, user_b):
        """user_a envoie une demande à user_b, retourne l'id de user_a."""
        me_b = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        b_id = me_b.get_json()['data']['id']
        client.post(f'/api/v1/friends/request/{b_id}', headers=auth(user_a['token']))
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        return me_a.get_json()['data']['id']

    def test_accept_request_ok(self, client, user_a, user_b):
        a_id = self._setup(client, user_a, user_b)
        resp = client.post(f'/api/v1/friends/accept/{a_id}',
                           headers=auth(user_b['token']))
        assert resp.status_code == 200

    def test_requester_cannot_accept_own_request(self, client, user_a, user_b):
        """Le demandeur ne peut pas accepter sa propre demande."""
        me_b = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        b_id = me_b.get_json()['data']['id']
        client.post(f'/api/v1/friends/request/{b_id}', headers=auth(user_a['token']))

        # user_a essaie d'accepter la demande qu'il a lui-même envoyée
        resp = client.post(f'/api/v1/friends/accept/{b_id}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_decline_request_ok(self, client, user_a, user_b):
        a_id = self._setup(client, user_a, user_b)
        resp = client.post(f'/api/v1/friends/decline/{a_id}',
                           headers=auth(user_b['token']))
        assert resp.status_code == 200

    def test_accept_nonexistent_request_400(self, client, user_a, user_b):
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me_a.get_json()['data']['id']
        resp = client.post(f'/api/v1/friends/accept/{a_id}',
                           headers=auth(user_b['token']))
        assert resp.status_code == 400


class TestFriendsList:

    def test_get_friends_empty(self, client, user_a):
        resp = client.get('/api/v1/friends', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []

    def test_get_friends_after_accept(self, client, user_a, user_b):
        me_b = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        b_id = me_b.get_json()['data']['id']
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me_a.get_json()['data']['id']

        client.post(f'/api/v1/friends/request/{b_id}', headers=auth(user_a['token']))
        client.post(f'/api/v1/friends/accept/{a_id}', headers=auth(user_b['token']))

        resp = client.get('/api/v1/friends', headers=auth(user_a['token']))
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert len(data) == 1
        # L'email de l'ami ne doit pas être exposé
        assert 'email' not in data[0]

    def test_remove_friend_ok(self, client, user_a, user_b):
        me_b = client.get('/api/v1/users/me', headers=auth(user_b['token']))
        b_id = me_b.get_json()['data']['id']
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me_a.get_json()['data']['id']

        client.post(f'/api/v1/friends/request/{b_id}', headers=auth(user_a['token']))
        client.post(f'/api/v1/friends/accept/{a_id}', headers=auth(user_b['token']))

        resp = client.delete(f'/api/v1/friends/{b_id}', headers=auth(user_a['token']))
        assert resp.status_code == 200
