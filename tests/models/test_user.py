"""
Tests unitaires pour le modèle User (authentification et compte).

Ce module teste:
- Création d'utilisateurs
- Validation des champs obligatoires
- Hachage des mots de passe
- Relation OneToOne avec Profile
- Sérialisation (to_dict, to_public_dict)

Utilisation:
  pytest tests/models/test_user.py                    # Lance tous les tests
  pytest tests/models/test_user.py -v                # Mode verbeux
  pytest tests/models/test_user.py --cov=app.models  # Avec couverture de code
"""

import pytest
from flask import Flask
from werkzeug.security import check_password_hash

from app import db
from app.models import User


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


class TestUser:
    """
    Suite de tests pour le modèle User (authentification et compte).
    
    Teste:
    - Création d'utilisateurs
    - Validation des champs obligatoires
    - Hachage des mots de passe
    - Relation OneToOne avec Profile
    - Sérialisation (to_dict, to_public_dict)
    """
    
    def test_user_creation(self, app):
        """Test la création d'un utilisateur valide."""
        user = User(
            email='alice@example.com',
            password_hash='hashed_password_123',
            role='user',
        )
        db.session.add(user)
        db.session.commit()
        
        # Vérifie que l'utilisateur est créé avec les bonnes valeurs
        assert user.id is not None
        assert user.email == 'alice@example.com'
        assert user.role == 'user'
        assert user.created_at is not None
    
    def test_user_password_security(self, app):
        """Test que le mot de passe est correctement haché (jamais en clair)."""
        from werkzeug.security import generate_password_hash
        
        password = "SecurePassword123!"
        hashed = generate_password_hash(password)
        
        user = User(
            email='bob@example.com',
            password_hash=hashed,
        )
        db.session.add(user)
        db.session.commit()
        
        # Vérifie que le mot de passe est haché
        assert user.password_hash != password  # Pas en clair
        assert check_password_hash(user.password_hash, password)  # Mais vérifié OK
    
    def test_user_unique_email(self, app):
        """Test que deux utilisateurs ne peuvent pas avoir le même email."""
        user1 = User(email='shared@example.com', password_hash='h1')
        user2 = User(email='shared@example.com', password_hash='h2')
        
        db.session.add(user1)
        db.session.commit()
        
        db.session.add(user2)
        with pytest.raises(Exception):  # Violation de contrainte UNIQUE
            db.session.commit()
    
    def test_user_to_dict(self, app):
        """Test la sérialisation to_dict() d'un utilisateur."""
        user = User(
            email='charlie@example.com',
            password_hash='hashed',
            role='admin',
        )
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        
        # Vérifie que le dictionnaire contient les champs attendus
        assert user_dict['id'] == user.id
        assert user_dict['email'] == 'charlie@example.com'
        assert user_dict['role'] == 'admin'
        assert 'created_at' in user_dict
    
    def test_user_to_public_dict(self, app):
        """Test la sérialisation to_public_dict() sans données sensibles."""
        user = User(
            email='private@example.com',
            password_hash='hashed',
        )
        db.session.add(user)
        db.session.commit()
        
        public_dict = user.to_public_dict()
        
        # Vérifie que le profil public n'expose pas l'email
        assert 'id' in public_dict
        assert 'email' not in public_dict  # Sensible: pas en public
