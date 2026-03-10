"""Tests du système de posts."""

import pytest
from tests.conftest import register, login, auth, VALID_PASSWORD


def _uid(client, token):
    return client.get('/api/v1/users/me', headers=auth(token)).get_json()['data']['id']


class TestCreatePost:

    def test_create_text_post_ok(self, client, user_a):
        resp = client.post('/api/v1/posts',
                           json={'content': 'Soirée Catan vendredi !'},
                           headers=auth(user_a['token']))
        assert resp.status_code == 201
        data = resp.get_json()['data']
        assert data['content'] == 'Soirée Catan vendredi !'
        assert data['post_type'] == 'text'

    def test_create_post_with_type(self, client, user_a):
        resp = client.post('/api/v1/posts',
                           json={'content': 'Breaking news', 'post_type': 'news'},
                           headers=auth(user_a['token']))
        assert resp.status_code == 201
        assert resp.get_json()['data']['post_type'] == 'news'

    def test_create_post_no_content_no_image_400(self, client, user_a):
        resp = client.post('/api/v1/posts', json={},
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_create_post_invalid_type_400(self, client, user_a):
        resp = client.post('/api/v1/posts',
                           json={'content': 'test', 'post_type': 'video'},
                           headers=auth(user_a['token']))
        assert resp.status_code == 400

    def test_create_post_no_auth_401(self, client):
        resp = client.post('/api/v1/posts', json={'content': 'test'})
        assert resp.status_code == 401


class TestGetPost:

    def test_get_post_ok(self, client, user_a):
        resp = client.post('/api/v1/posts',
                           json={'content': 'Mon post'},
                           headers=auth(user_a['token']))
        pid = resp.get_json()['data']['id']

        resp = client.get(f'/api/v1/posts/{pid}',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data']['content'] == 'Mon post'

    def test_get_post_not_found_404(self, client, user_a):
        resp = client.get('/api/v1/posts/99999',
                          headers=auth(user_a['token']))
        assert resp.status_code == 404


class TestUpdatePost:

    def test_update_own_post_ok(self, client, user_a):
        resp = client.post('/api/v1/posts',
                           json={'content': 'Original'},
                           headers=auth(user_a['token']))
        pid = resp.get_json()['data']['id']

        resp = client.put(f'/api/v1/posts/{pid}',
                          json={'content': 'Modifié'},
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data']['content'] == 'Modifié'

    def test_update_others_post_403(self, client, user_a, user_b):
        resp = client.post('/api/v1/posts',
                           json={'content': 'Post de A'},
                           headers=auth(user_a['token']))
        pid = resp.get_json()['data']['id']

        resp = client.put(f'/api/v1/posts/{pid}',
                          json={'content': 'Hack'},
                          headers=auth(user_b['token']))
        assert resp.status_code == 403

    def test_update_not_found_404(self, client, user_a):
        resp = client.put('/api/v1/posts/99999',
                          json={'content': 'test'},
                          headers=auth(user_a['token']))
        assert resp.status_code == 404


class TestDeletePost:

    def test_delete_own_post_ok(self, client, user_a):
        resp = client.post('/api/v1/posts',
                           json={'content': 'À supprimer'},
                           headers=auth(user_a['token']))
        pid = resp.get_json()['data']['id']

        resp = client.delete(f'/api/v1/posts/{pid}',
                             headers=auth(user_a['token']))
        assert resp.status_code == 200

        resp = client.get(f'/api/v1/posts/{pid}',
                          headers=auth(user_a['token']))
        assert resp.status_code == 404

    def test_delete_others_post_403(self, client, user_a, user_b):
        resp = client.post('/api/v1/posts',
                           json={'content': 'Post de A'},
                           headers=auth(user_a['token']))
        pid = resp.get_json()['data']['id']

        resp = client.delete(f'/api/v1/posts/{pid}',
                             headers=auth(user_b['token']))
        assert resp.status_code == 403

    def test_delete_not_found_404(self, client, user_a):
        resp = client.delete('/api/v1/posts/99999',
                             headers=auth(user_a['token']))
        assert resp.status_code == 404


class TestListPosts:

    def test_list_empty(self, client, user_a):
        resp = client.get('/api/v1/posts', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['data'] == []
        assert resp.get_json()['total_count'] == 0

    def test_list_with_posts(self, client, user_a):
        client.post('/api/v1/posts', json={'content': 'Post 1'},
                    headers=auth(user_a['token']))
        client.post('/api/v1/posts', json={'content': 'Post 2'},
                    headers=auth(user_a['token']))

        resp = client.get('/api/v1/posts', headers=auth(user_a['token']))
        assert resp.status_code == 200
        assert resp.get_json()['total_count'] == 2

    def test_list_pagination(self, client, user_a):
        for i in range(3):
            client.post('/api/v1/posts', json={'content': f'Post {i}'},
                        headers=auth(user_a['token']))

        resp = client.get('/api/v1/posts?limit=2&offset=0',
                          headers=auth(user_a['token']))
        data = resp.get_json()
        assert len(data['data']) == 2
        assert data['total_count'] == 3


class TestListUserPosts:

    def test_list_user_posts_ok(self, client, user_a, user_b):
        uid_a = _uid(client, user_a['token'])
        client.post('/api/v1/posts', json={'content': 'Post A'},
                    headers=auth(user_a['token']))
        client.post('/api/v1/posts', json={'content': 'Post B'},
                    headers=auth(user_b['token']))

        resp = client.get(f'/api/v1/posts/user/{uid_a}',
                          headers=auth(user_a['token']))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total_count'] == 1
        assert data['data'][0]['content'] == 'Post A'
