"""Tests du système d'avis (reviews)."""

import pytest
from tests.conftest import auth, make_game


class TestCreateReview:

    def test_review_event_ok(self, client, event_id, user_b):
        resp = client.post('/api/v1/reviews',
                           json={'event_id': event_id, 'rating': 5,
                                 'comment': 'Super soirée !'},
                           headers=auth(user_b['token']))
        assert resp.status_code == 201
        data = resp.get_json()['data']
        assert data['rating'] == 5
        assert data['event_id'] == event_id

    def test_review_user_ok(self, client, user_a, user_b):
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me_a.get_json()['data']['id']

        resp = client.post('/api/v1/reviews',
                           json={'reviewed_user_id': a_id, 'rating': 4},
                           headers=auth(user_b['token']))
        assert resp.status_code == 201
        assert resp.get_json()['data']['reviewed_user_id'] == a_id

    def test_review_rating_out_of_range_400(self, client, event_id, user_b):
        resp = client.post('/api/v1/reviews',
                           json={'event_id': event_id, 'rating': 6},
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_review_both_targets_400(self, client, event_id, user_a, user_b):
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me_a.get_json()['data']['id']
        resp = client.post('/api/v1/reviews',
                           json={'event_id': event_id, 'reviewed_user_id': a_id,
                                 'rating': 3},
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_review_no_target_400(self, client, user_b):
        resp = client.post('/api/v1/reviews',
                           json={'rating': 3},
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_review_self_400(self, client, user_a):
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me_a.get_json()['data']['id']
        resp = client.post('/api/v1/reviews',
                           json={'reviewed_user_id': a_id, 'rating': 5},
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_duplicate_event_review_400(self, client, event_id, user_b):
        client.post('/api/v1/reviews',
                    json={'event_id': event_id, 'rating': 4},
                    headers=auth(user_b['token']))
        resp = client.post('/api/v1/reviews',
                           json={'event_id': event_id, 'rating': 5},
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_duplicate_user_review_400(self, client, user_a, user_b):
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me_a.get_json()['data']['id']
        client.post('/api/v1/reviews',
                    json={'reviewed_user_id': a_id, 'rating': 4},
                    headers=auth(user_b['token']))
        resp = client.post('/api/v1/reviews',
                           json={'reviewed_user_id': a_id, 'rating': 5},
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_review_no_auth_401(self, client, event_id):
        resp = client.post('/api/v1/reviews',
                           json={'event_id': event_id, 'rating': 3})
        assert resp.status_code == 401


class TestGetReviews:

    def test_get_event_reviews(self, client, event_id, user_b):
        client.post('/api/v1/reviews',
                    json={'event_id': event_id, 'rating': 5},
                    headers=auth(user_b['token']))

        resp = client.get(f'/api/v1/events/{event_id}/reviews',
                          headers=auth(user_b['token']))
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert len(data) == 1
        assert data[0]['rating'] == 5

    def test_get_user_reviews(self, client, user_a, user_b):
        me_a = client.get('/api/v1/users/me', headers=auth(user_a['token']))
        a_id = me_a.get_json()['data']['id']
        client.post('/api/v1/reviews',
                    json={'reviewed_user_id': a_id, 'rating': 4},
                    headers=auth(user_b['token']))

        resp = client.get(f'/api/v1/users/{a_id}/reviews',
                          headers=auth(user_b['token']))
        assert resp.status_code == 200
        assert len(resp.get_json()['data']) == 1


class TestDeleteReview:

    def test_delete_own_review_ok(self, client, event_id, user_b):
        r_resp = client.post('/api/v1/reviews',
                             json={'event_id': event_id, 'rating': 3},
                             headers=auth(user_b['token']))
        rid = r_resp.get_json()['data']['id']

        resp = client.delete(f'/api/v1/reviews/{rid}',
                             headers=auth(user_b['token']))
        assert resp.status_code == 200

    def test_delete_others_review_403(self, client, event_id, user_a, user_b):
        r_resp = client.post('/api/v1/reviews',
                             json={'event_id': event_id, 'rating': 3},
                             headers=auth(user_b['token']))
        rid = r_resp.get_json()['data']['id']

        resp = client.delete(f'/api/v1/reviews/{rid}',
                             headers=auth(user_a['token']))
        assert resp.status_code == 403

    def test_delete_unknown_review_404(self, client, user_a):
        resp = client.delete('/api/v1/reviews/99999',
                             headers=auth(user_a['token']))
        assert resp.status_code == 404
