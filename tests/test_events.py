"""Tests des endpoints événements."""

import pytest
from tests.conftest import auth, make_game, VALID_PASSWORD, register, login


class TestListEvents:

    def test_list_events_empty(self, client, user_a):
        resp = client.get('/api/v1/events', headers=auth(user_a['token']))
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['data'] == []
        assert body['total_count'] == 0

    def test_list_events_no_auth(self, client):
        resp = client.get('/api/v1/events')
        assert resp.status_code == 401


class TestCreateEvent:

    def test_create_event_ok(self, client, app, user_a, mock_ext):
        gid = make_game(app)
        resp = client.post('/api/v1/events', json={
            'title': 'Soirée Catan',
            'game_id': gid,
            'location_text': '5 avenue des Jeux, Paris',
            'date_time': '2030-06-15T19:00:00',
            'max_players': 4,
            'description': 'Fun evening',
        }, headers=auth(user_a['token']))
        assert resp.status_code == 201
        body = resp.get_json()
        assert 'data' in body
        data = body['data']
        assert data['title'] == 'Soirée Catan'
        assert data['status'] == 'open'

    def test_create_event_no_auth(self, client, app):
        gid = make_game(app)
        resp = client.post('/api/v1/events', json={
            'title': 'Test', 'game_id': gid,
            'location_text': 'Paris', 'date_time': '2030-01-01T18:00:00',
            'max_players': 4,
        })
        assert resp.status_code == 401

    def test_create_event_missing_field(self, client, app, user_a, mock_ext):
        gid = make_game(app)
        resp = client.post('/api/v1/events', json={
            'game_id': gid,
            'location_text': 'Paris',
            'date_time': '2030-01-01T18:00:00',
            # 'title' manquant
        }, headers=auth(user_a['token']))
        assert resp.status_code == 400


class TestGetEvent:

    def test_get_event_ok(self, client, event_id, user_a):
        resp = client.get(f'/api/v1/events/{event_id}', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data']['id'] == event_id

    def test_get_event_unknown_404(self, client, user_a):
        resp = client.get('/api/v1/events/99999', headers=auth(user_a['token']))
        assert resp.status_code == 404


class TestUpdateEvent:

    def test_update_event_ok(self, client, event_id, user_a):
        resp = client.put(f'/api/v1/events/{event_id}',
                          json={'title': 'Nouveau titre'},
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data']['title'] == 'Nouveau titre'

    def test_update_event_not_creator_403(self, client, event_id, user_b):
        resp = client.put(f'/api/v1/events/{event_id}',
                          json={'title': 'Hack'},
                          headers=auth(user_b['token']))
        assert resp.status_code == 403


class TestCancelEvent:

    def test_cancel_event_ok(self, client, event_id, user_a):
        resp = client.delete(f'/api/v1/events/{event_id}',
                             headers=auth(user_a['token']))
        assert resp.status_code == 200
        # Vérification que le statut est bien 'cancelled'
        detail = client.get(f'/api/v1/events/{event_id}', headers=auth(user_a['token']))
        assert detail.get_json()['data']['status'] == 'cancelled'

    def test_cancel_event_not_creator_403(self, client, event_id, user_b):
        resp = client.delete(f'/api/v1/events/{event_id}',
                             headers=auth(user_b['token']))
        assert resp.status_code == 403

    def test_cancel_already_cancelled_400(self, client, event_id, user_a):
        client.delete(f'/api/v1/events/{event_id}', headers=auth(user_a['token']))
        resp = client.delete(f'/api/v1/events/{event_id}', headers=auth(user_a['token']))
        assert resp.status_code == 400


class TestJoinLeaveEvent:

    def test_join_event_ok(self, client, event_id, user_b):
        resp = client.post(f'/api/v1/events/{event_id}/join',
                           headers=auth(user_b['token']))
        assert resp.status_code == 201

    def test_creator_cannot_join_own_event(self, client, event_id, user_a):
        resp = client.post(f'/api/v1/events/{event_id}/join',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_join_twice_400(self, client, event_id, user_b):
        client.post(f'/api/v1/events/{event_id}/join',
                    headers=auth(user_b['token']))
        resp = client.post(f'/api/v1/events/{event_id}/join',
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_leave_event_ok(self, client, event_id, user_b):
        client.post(f'/api/v1/events/{event_id}/join',
                    headers=auth(user_b['token']))
        resp = client.post(f'/api/v1/events/{event_id}/leave',
                           headers=auth(user_b['token']))
        assert resp.status_code == 200

    def test_creator_cannot_leave_event(self, client, event_id, user_a):
        resp = client.post(f'/api/v1/events/{event_id}/leave',
                           headers=auth(user_a['token']))
        assert resp.status_code == 400


class TestEventComments:

    def test_get_comments_empty(self, client, event_id, user_a):
        resp = client.get(f'/api/v1/events/{event_id}/comment', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []

    def test_add_comment_ok(self, client, event_id, user_a):
        resp = client.post(f'/api/v1/events/{event_id}/comment',
                           json={'content': 'Super soirée !'},
                           headers=auth(user_a['token']))
        assert resp.status_code == 201
        data = resp.get_json()['data']
        assert data['content'] == 'Super soirée !'
        # username et profile_image_url doivent être présents
        assert 'username' in data

    def test_add_comment_no_auth_401(self, client, event_id):
        resp = client.post(f'/api/v1/events/{event_id}/comment',
                           json={'content': 'test'})
        assert resp.status_code == 401

    def test_add_comment_empty_content_400(self, client, event_id, user_a):
        resp = client.post(f'/api/v1/events/{event_id}/comment',
                           json={'content': ''},
                           headers=auth(user_a['token']))
        assert resp.status_code == 400
