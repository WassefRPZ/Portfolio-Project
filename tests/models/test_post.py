"""
Tests unitaires pour le modèle Post (flux social).

Ce module teste:
- Création de posts (texte, image, news)
- Relation avec auteur (User)
- Sérialisation

Utilisation:
  pytest tests/models/test_post.py                    # Lance tous les tests
  pytest tests/models/test_post.py -v                # Mode verbeux
  pytest tests/models/test_post.py --cov=app.models  # Avec couverture de code
"""

import pytest
from flask import Flask

from app import db
from app.models import User, Post


@pytest.fixture
def app():
    """
    Fixture pytest: Crée une application Flask en mode test.
    - Utilise une base de données en mémoire SQLite
    - Crée toutes les tables
    - Fournit un contexte d'application isolé par test
    """
    test_app = Flask(__name__)
    test_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='test-secret',
        JWT_SECRET_KEY='test-jwt-secret',
    )
    db.init_app(test_app)
    
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture pytest: Fournit un client de test Flask."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture pytest: Fournit un test CLI runner."""
    return app.test_cli_runner()


class TestPost:
    """
    Suite de tests pour le modèle Post (flux social).
    
    Teste:
    - Création de posts (texte, image, news)
    - Relation avec auteur (User)
    - Sérialisation
    """
    
    def test_post_creation_text(self, app):
        """Test la création d'un post texte."""
        user = User(email='blogger@example.com', password_hash='hashed')
        
        db.session.add(user)
        db.session.flush()
        
        post = Post(
            author_id=user.id,
            post_type='text',
            content='Je suis en train de jouer à Catan!',
        )
        db.session.add(post)
        db.session.commit()
        
        assert post.post_type == 'text'
        assert post.content == 'Je suis en train de jouer à Catan!'
        assert post.author_id == user.id
    
    def test_post_creation_image(self, app):
        """Test la création d'un post avec image."""
        user = User(email='photographer@example.com', password_hash='hashed')
        
        db.session.add(user)
        db.session.flush()
        
        post = Post(
            author_id=user.id,
            post_type='image',
            content='Soirée jeux de hier soir',
            image_url='https://example.com/game_night.jpg',
        )
        db.session.add(post)
        db.session.commit()
        
        assert post.post_type == 'image'
        assert post.image_url == 'https://example.com/game_night.jpg'
    
    def test_post_to_dict(self, app):
        """Test la sérialisation d'un post."""
        user = User(email='poster@example.com', password_hash='hashed')
        
        db.session.add(user)
        db.session.flush()
        
        post = Post(
            author_id=user.id,
            post_type='text',
            content='Découvrez les meilleur jeux de 2026!',
        )
        db.session.add(post)
        db.session.commit()
        
        post_dict = post.to_dict()
        
        assert post_dict['post_type'] == 'text'
        assert post_dict['content'] == 'Découvrez les meilleur jeux de 2026!'
        assert post_dict['author_id'] == user.id
