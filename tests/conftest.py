"""
Configuration et fixtures communes pour les tests BoardGame Hub.
Base de données: boardgame_hub_test (MySQL, isolée de la prod)
APIs externes: mockées (OpenCage, Cloudinary)
"""

import os
import sys

# ── Doit être défini AVANT tout import de l'app ─────────────────────────────
# load_dotenv() ne surcharge pas les variables déjà présentes dans os.environ
os.environ['DB_NAME'] = 'boardgame_hub_test'
os.environ['RATELIMIT_ENABLED'] = 'False'
# ─────────────────────────────────────────────────────────────────────────────

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import mysql.connector
from unittest.mock import patch


# ── Crée la base de test si elle n'existe pas ────────────────────────────────
def _ensure_test_db():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'dev_user'),
        password=os.getenv('DB_PASSWORD', '')
    )
    cur  = conn.cursor()
    cur.execute(
        'CREATE DATABASE IF NOT EXISTS boardgame_hub_test '
        'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
    )
    conn.commit()
    cur.close()
    conn.close()

_ensure_test_db()

# ── Import de l'app (après avoir fixé DB_NAME) ───────────────────────────────
from app import create_app, db as _db
from app.models import Game
from app.services import facade


# ─────────────────────────────────────────────────────────────────────────────
# Valeurs de retour des mocks externes
GEOCODE_RESULT    = ({'latitude': 48.8566, 'longitude': 2.3522, 'city': 'Paris', 'region': 'Île-de-France'}, None)
CLOUDINARY_URL    = ('https://res.cloudinary.com/test/image/upload/v1/test.jpg', None)
VALID_PASSWORD    = 'Test@1234'


# ── App (session) ─────────────────────────────────────────────────────────────
@pytest.fixture(scope='session')
def app():
    """Application Flask pointant sur boardgame_hub_test."""
    _app = create_app()
    _app.config['TESTING']                  = True
    _app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False   # pas d'expiry en test
    return _app


# ── Client HTTP (session) ────────────────────────────────────────────────────
@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


# ── Nettoyage avant et après chaque test ──────────────────────────────────────
def _wipe(app):
    """Vide toutes les tables de la base de test."""
    with app.app_context():
        _db.session.remove()
        _db.session.execute(_db.text('SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'))
        _db.session.execute(_db.text('SET FOREIGN_KEY_CHECKS = 0'))
        for table in [
            'post_likes', 'post_comments', 'posts',
            'friends', 'event_comments', 'event_participants',
            'favorite_games', 'events', 'games', 'profiles', 'users',
        ]:
            _db.session.execute(_db.text(f'DELETE FROM {table}'))
        _db.session.execute(_db.text('SET FOREIGN_KEY_CHECKS = 1'))
        _db.session.commit()


@pytest.fixture(autouse=True)
def clean_tables(app):
    """Vide toutes les tables AVANT et APRÈS chaque test."""
    _wipe(app)
    yield
    _wipe(app)


# ── Mock des services externes (fixture opt-in) ───────────────────────────────
@pytest.fixture
def mock_ext():
    """Mock OpenCage et Cloudinary pour éviter les appels HTTP réels."""
    with patch.object(facade, '_geocode',
                      return_value=GEOCODE_RESULT), \
         patch.object(facade, '_upload_to_cloudinary',
                      return_value=CLOUDINARY_URL):
        yield


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def register(client, username, email, password=VALID_PASSWORD, city='Paris'):
    return client.post('/api/v1/auth/register', json={
        'username': username, 'email': email,
        'password': password, 'city': city,
    })


def login(client, email, password=VALID_PASSWORD):
    resp = client.post('/api/v1/auth/login', json={
        'email': email, 'password': password,
    })
    return resp.get_json()['data']['access_token']


def auth(token):
    """En-tête Authorization pour le client de test."""
    return {'Authorization': f'Bearer {token}'}


def make_game(app, name='Catan', min_p=2, max_p=4, time=60):
    """Crée un jeu directement en base et retourne son id."""
    with app.app_context():
        with _db.engine.connect() as conn:
            result = conn.execute(_db.text(
                "INSERT INTO games (name, description, min_players, max_players, play_time_min) "
                "VALUES (:n, :d, :min_p, :max_p, :t)"
            ), {'n': name, 'd': 'Test game', 'min_p': min_p, 'max_p': max_p, 't': time})
            conn.commit()
            gid = result.lastrowid
    return gid


# ── Fixtures utilisateurs ─────────────────────────────────────────────────────
@pytest.fixture
def user_a(client):
    register(client, 'UserA', 'a@test.com')
    token = login(client, 'a@test.com')
    return {'token': token, 'email': 'a@test.com', 'username': 'UserA'}


@pytest.fixture
def user_b(client):
    register(client, 'UserB', 'b@test.com')
    token = login(client, 'b@test.com')
    return {'token': token, 'email': 'b@test.com', 'username': 'UserB'}


@pytest.fixture
def event_id(client, app, user_a, mock_ext):
    """Crée un événement et retourne son id."""
    gid = make_game(app)
    resp = client.post('/api/v1/events', json={
        'title': 'Soirée Catan',
        'game_id': gid,
        'location_text': '1 rue de Rivoli, Paris',
        'date_time': '2030-06-15T19:00:00',
        'max_players': 4,
    }, headers=auth(user_a['token']))
    return resp.get_json()['data']['id']
