"""Tests du système d'amitié."""

import pytest
from tests.conftest import register, login, auth, VALID_PASSWORD


def _uid(client, token):
    """Récupère l'id de l'utilisateur connecté."""
    return client.get('/api/v1/users/me', headers=auth(token)).get_json()['data']['id']


class TestSendRequest:

    def test_send_request_ok(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        resp = client.post(f'/api/v1/friends/request/{uid_b}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['status'] == 'pending'

    def test_send_request_to_self_400(self, client, user_a):
        uid_a = _uid(client, user_a['token'])
        resp = client.post(f'/api/v1/friends/request/{uid_a}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_send_duplicate_request_400(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.post(f'/api/v1/friends/request/{uid_b}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_send_request_unknown_user_400(self, client, user_a):
        resp = client.post('/api/v1/friends/request/99999',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_send_request_no_auth_401(self, client):
        resp = client.post('/api/v1/friends/request/1')
        assert resp.status_code == 401


class TestAcceptRequest:

    def test_accept_request_ok(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.post(f'/api/v1/friends/accept/{uid_a}',
                           headers=auth(user_b['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data']['status'] == 'accepted'

    def test_requester_cannot_accept_own_request(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.post(f'/api/v1/friends/accept/{uid_b}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_accept_nonexistent_request_400(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        resp = client.post(f'/api/v1/friends/accept/{uid_a}',
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_accept_already_accepted_400(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        client.post(f'/api/v1/friends/accept/{uid_a}', headers=auth(user_b['token']))
        resp = client.post(f'/api/v1/friends/accept/{uid_a}',
                           headers=auth(user_b['token']))
        assert resp.status_code == 400


class TestRejectRequest:

    def test_reject_ok(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.post(f'/api/v1/friends/reject/{uid_a}',
                           headers=auth(user_b['token']))
        assert resp.status_code == 200

    def test_reject_nonexistent_400(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        resp = client.post(f'/api/v1/friends/reject/{uid_a}',
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_reject_own_request_400(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.post(f'/api/v1/friends/reject/{uid_b}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400


class TestRemoveFriend:

    def test_remove_ok(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        client.post(f'/api/v1/friends/accept/{uid_a}', headers=auth(user_b['token']))
        resp = client.delete(f'/api/v1/friends/{uid_b}',
                             headers=auth(user_a['token']))
        assert resp.status_code == 200

    def test_remove_not_friends_400(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        resp = client.delete(f'/api/v1/friends/{uid_b}',
                             headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_can_resend_after_remove(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        client.post(f'/api/v1/friends/accept/{uid_a}', headers=auth(user_b['token']))
        client.delete(f'/api/v1/friends/{uid_b}', headers=auth(user_a['token']))
        resp = client.post(f'/api/v1/friends/request/{uid_b}',
                           headers=auth(user_a['token']))
        assert resp.status_code == 201


class TestListFriends:

    def test_list_empty(self, client, user_a):
        resp = client.get('/api/v1/friends', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []

    def test_list_with_friend(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        client.post(f'/api/v1/friends/accept/{uid_a}', headers=auth(user_b['token']))
        resp = client.get('/api/v1/friends', headers=auth(user_a['token']))
        friends = resp.get_json()['data']
        assert len(friends) == 1
        assert friends[0]['username'] == 'UserB'

    def test_list_excludes_pending(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.get('/api/v1/friends', headers=auth(user_a['token']))
        assert resp.get_json()['data'] == []


class TestPendingRequests:

    def test_pending_received(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.get('/api/v1/friends/pending', headers=auth(user_b['token']))
        assert resp.status_code == 200
        pending = resp.get_json()['data']
        assert len(pending) == 1
        assert pending[0]['username'] == 'UserA'
        assert 'friendship_id' in pending[0]

    def test_pending_empty(self, client, user_a):
        resp = client.get('/api/v1/friends/pending', headers=auth(user_a['token']))
        assert resp.get_json()['data'] == []

    def test_sender_not_in_pending(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.get('/api/v1/friends/pending', headers=auth(user_a['token']))
        assert resp.get_json()['data'] == []


class TestSentRequests:

    def test_sent_ok(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.get('/api/v1/friends/sent', headers=auth(user_a['token']))
        assert resp.status_code == 200
        sent = resp.get_json()['data']
        assert len(sent) == 1
        assert sent[0]['username'] == 'UserB'

    def test_sent_empty(self, client, user_a):
        resp = client.get('/api/v1/friends/sent', headers=auth(user_a['token']))
        assert resp.get_json()['data'] == []

    def test_receiver_not_in_sent(self, client, user_a, user_b):
        uid_b = _uid(client, user_b['token'])
        client.post(f'/api/v1/friends/request/{uid_b}', headers=auth(user_a['token']))
        resp = client.get('/api/v1/friends/sent', headers=auth(user_b['token']))
        assert resp.get_json()['data'] == []
