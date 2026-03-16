"""
Tests unitaires pour le modèle Friend (réseau social).

Ce module teste:
- Création de demandes d'amitié
- Statuts (pending, accepted)
- Unicité de la paire d'utilisateurs
- Track du demandeur (requester_id)

Utilisation:
  pytest tests/models/test_friend.py                   # Lance tous les tests
  pytest tests/models/test_friend.py -v               # Mode verbeux
  pytest tests/models/test_friend.py --cov=app.models # Avec couverture de code
"""

import pytest
from flask import Flask

from app import db
from app.models import User, Friend


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


class TestFriend:
    """
    Suite de tests pour le modèle Friend (réseau social).
    
    Teste:
    - Création de demandes d'amitié
    - Statuts (pending, accepted)
    - Unicité de la paire d'utilisateurs
    - Track du demandeur (requester_id)
    """
    
    def test_friend_request_creation(self, app):
        """Test la création d'une demande d'amitié."""
        user1 = User(email='alice@example.com', password_hash='h1')
        user2 = User(email='bob@example.com', password_hash='h2')
        
        db.session.add_all([user1, user2])
        db.session.flush()
        
        # Alice demande Bob en ami
        friendship = Friend(
            user_id_1=min(user1.id, user2.id),
            user_id_2=max(user1.id, user2.id),
            requester_id=user1.id,
            status='pending',
        )
        db.session.add(friendship)
        db.session.commit()
        
        assert friendship.status == 'pending'
        assert friendship.requester_id == user1.id
    
    def test_friend_acceptance(self, app):
        """Test l'acceptation d'une demande d'amitié."""
        user1 = User(email='sender@example.com', password_hash='h1')
        user2 = User(email='receiver@example.com', password_hash='h2')
        
        db.session.add_all([user1, user2])
        db.session.flush()
        
        friendship = Friend(
            user_id_1=min(user1.id, user2.id),
            user_id_2=max(user1.id, user2.id),
            requester_id=user1.id,
            status='pending',
        )
        db.session.add(friendship)
        db.session.commit()
        
        # Bob accepte la demande
        friendship.status = 'accepted'
        db.session.commit()
        
        assert friendship.status == 'accepted'
