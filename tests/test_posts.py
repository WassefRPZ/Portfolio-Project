"""Tests des endpoints posts (fil d'actualité)."""

import pytest
from tests.conftest import auth


class TestCreatePost:

    def test_create_text_post_ok(self, client, user_a):
        resp = client.post('/api/v1/posts',
                           json={'content': 'Soirée Catan vendredi !'},
                           headers=auth(user_a['token']))
        assert resp.status_code == 201
        data = resp.get_json()['data']
        assert data['content'] == 'Soirée Catan vendredi !'
        assert data['post_type'] == 'text'

    def test_create_post_no_content_no_image_400(self, client, user_a):
        resp = client.post('/api/v1/posts', json={},
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_create_post_no_auth_401(self, client):
        resp = client.post('/api/v1/posts',
                           json={'content': 'test'})
        assert resp.status_code == 401


class TestGetFeed:

    def test_get_feed_empty(self, client, user_a):
        resp = client.get('/api/v1/posts', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []

    def test_get_feed_returns_posts(self, client, user_a):
        client.post('/api/v1/posts', json={'content': 'Post 1'},
                    headers=auth(user_a['token']))
        client.post('/api/v1/posts', json={'content': 'Post 2'},
                    headers=auth(user_a['token']))

        resp = client.get('/api/v1/posts', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert len(resp.get_json()['data']) == 2

    def test_feed_pagination(self, client, user_a):
        for i in range(5):
            client.post('/api/v1/posts', json={'content': f'Post {i}'},
                        headers=auth(user_a['token']))

        resp = client.get('/api/v1/posts?limit=2&offset=0',
                          headers=auth(user_a['token']))
        assert len(resp.get_json()['data']) == 2

    def test_feed_no_auth_401(self, client):
        resp = client.get('/api/v1/posts')
        assert resp.status_code == 401


class TestDeletePost:

    def _create_post(self, client, token):
        resp = client.post('/api/v1/posts', json={'content': 'à supprimer'},
                           headers=auth(token))
        return resp.get_json()['data']['id']

    def test_delete_own_post_ok(self, client, user_a):
        pid = self._create_post(client, user_a['token'])
        resp = client.delete(f'/api/v1/posts/{pid}',
                             headers=auth(user_a['token']))
        assert resp.status_code == 200

    def test_delete_others_post_403(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        resp = client.delete(f'/api/v1/posts/{pid}',
                             headers=auth(user_b['token']))
        assert resp.status_code == 403

    def test_delete_unknown_post_404(self, client, user_a):
        resp = client.delete('/api/v1/posts/99999',
                             headers=auth(user_a['token']))
        assert resp.status_code == 404


class TestLikePost:

    def _create_post(self, client, token):
        resp = client.post('/api/v1/posts', json={'content': 'test'},
                           headers=auth(token))
        return resp.get_json()['data']['id']

    def test_like_post_ok(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        resp = client.post(f'/api/v1/posts/{pid}/like',
                           headers=auth(user_b['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data']['likes_count'] == 1

    def test_like_own_post_ok(self, client, user_a):
        pid = self._create_post(client, user_a['token'])
        resp = client.post(f'/api/v1/posts/{pid}/like',
                           headers=auth(user_a['token']))
        assert resp.status_code == 200

    def test_like_twice_400(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        client.post(f'/api/v1/posts/{pid}/like', headers=auth(user_b['token']))
        resp = client.post(f'/api/v1/posts/{pid}/like',
                           headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_unlike_post_ok(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        client.post(f'/api/v1/posts/{pid}/like', headers=auth(user_b['token']))
        resp = client.delete(f'/api/v1/posts/{pid}/like',
                             headers=auth(user_b['token']))
        assert resp.status_code == 200

    def test_unlike_not_liked_400(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        resp = client.delete(f'/api/v1/posts/{pid}/like',
                             headers=auth(user_b['token']))
        assert resp.status_code == 400

    def test_like_unknown_post_404(self, client, user_a):
        resp = client.post('/api/v1/posts/99999/like',
                           headers=auth(user_a['token']))
        assert resp.status_code == 404


class TestPostComments:

    def _create_post(self, client, token):
        resp = client.post('/api/v1/posts', json={'content': 'test'},
                           headers=auth(token))
        return resp.get_json()['data']['id']

    def test_add_comment_ok(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        resp = client.post(f'/api/v1/posts/{pid}/comments',
                           json={'content': 'Super post !'},
                           headers=auth(user_b['token']))
        assert resp.status_code == 201
        assert resp.get_json()['data']['content'] == 'Super post !'

    def test_add_comment_empty_400(self, client, user_a):
        pid = self._create_post(client, user_a['token'])
        resp = client.post(f'/api/v1/posts/{pid}/comments',
                           json={'content': ''},
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_get_comments(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        client.post(f'/api/v1/posts/{pid}/comments',
                    json={'content': 'Commentaire 1'},
                    headers=auth(user_b['token']))

        resp = client.get(f'/api/v1/posts/{pid}/comments',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert len(resp.get_json()['data']) == 1

    def test_delete_own_comment_ok(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        c_resp = client.post(f'/api/v1/posts/{pid}/comments',
                             json={'content': 'Mon commentaire'},
                             headers=auth(user_b['token']))
        cid = c_resp.get_json()['data']['id']

        resp = client.delete(f'/api/v1/posts/comments/{cid}',
                             headers=auth(user_b['token']))
        assert resp.status_code == 200

    def test_delete_others_comment_403(self, client, user_a, user_b):
        pid = self._create_post(client, user_a['token'])
        c_resp = client.post(f'/api/v1/posts/{pid}/comments',
                             json={'content': 'Commentaire UserB'},
                             headers=auth(user_b['token']))
        cid = c_resp.get_json()['data']['id']

        resp = client.delete(f'/api/v1/posts/comments/{cid}',
                             headers=auth(user_a['token']))
        assert resp.status_code == 403
