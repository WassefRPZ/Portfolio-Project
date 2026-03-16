"""
Tests unitaires pour le modèle Profile (informations publiques).

Ce module teste:
- Création de profils
- Relation OneToOne avec User
- Unicité du pseudonyme
- Sérialisation

Utilisation:
  pytest tests/models/test_profile.py                 # Lance tous les tests
  pytest tests/models/test_profile.py -v             # Mode verbeux
  pytest tests/models/test_profile.py --cov=app.models  # Avec couverture de code
"""

import pytest
from flask import Flask

from app import db
from app.models import User, Profile


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


class TestProfile:
    """
    Suite de tests pour le modèle Profile (informations publiques).
    
    Teste:
    - Création de profils
    - Relation OneToOne avec User
    - Unicité du pseudonyme
    - Sérialisation
    """
    
    def test_profile_creation(self, app):
        """Test la création d'un profil associé à un utilisateur."""
        user = User(email='dave@example.com', password_hash='hashed')
        db.session.add(user)
        db.session.flush()  # Obtient l'ID sans committer
        
        profile = Profile(
            user_id=user.id,
            username='dave_the_gamer',
            bio='Je joue aux jeux de société',
            city='Paris',
            region='Île-de-France',
        )
        db.session.add(profile)
        db.session.commit()
        
        # Vérifie que le profil est créé avec les bonnes valeurs
        assert profile.username == 'dave_the_gamer'
        assert profile.city == 'Paris'
    
    def test_profile_unique_username(self, app):
        """Test que deux profils ne peuvent pas avoir le même pseudonyme."""
        user1 = User(email='user1@example.com', password_hash='h1')
        user2 = User(email='user2@example.com', password_hash='h2')
        db.session.add_all([user1, user2])
        db.session.flush()
        
        profile1 = Profile(user_id=user1.id, username='unique_player')
        profile2 = Profile(user_id=user2.id, username='unique_player')
        
        db.session.add(profile1)
        db.session.commit()
        
        db.session.add(profile2)
        with pytest.raises(Exception):  # Violation UNIQUE
            db.session.commit()
    
    def test_profile_to_dict(self, app):
        """Test la sérialisation to_dict() d'un profil."""
        user = User(email='eve@example.com', password_hash='hashed')
        db.session.add(user)
        db.session.flush()
        
        profile = Profile(
            user_id=user.id,
            username='eve_games',
            bio='Passionnée par les jeux',
            city='Lyon',
        )
        db.session.add(profile)
        db.session.commit()
        
        profile_dict = profile.to_dict()
        
        # Vérifie que le dictionnaire contient les champs
        assert profile_dict['username'] == 'eve_games'
        assert profile_dict['bio'] == 'Passionnée par les jeux'
        assert profile_dict['city'] == 'Lyon'
        assert profile_dict['user_id'] == user.id
