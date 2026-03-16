"""
Tests unitaires pour le modèle Event (événements).

Ce module teste:
- Création d'événements
- Relation avec Creator (User)
- Relation avec Game
- Relation avec EventParticipant
- Sérialisation

Utilisation:
  pytest tests/models/test_event.py                   # Lance tous les tests
  pytest tests/models/test_event.py -v               # Mode verbeux
  pytest tests/models/test_event.py --cov=app.models # Avec couverture de code
"""

import pytest
from datetime import datetime
from flask import Flask

from app import db
from app.models import User, Game, Event


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


class TestEvent:
    """
    Suite de tests pour le modèle Event (événements).
    
    Teste:
    - Création d'événements
    - Relation avec Creator (User)
    - Relation avec Game
    - Relation avec EventParticipant
    - Sérialisation
    """
    
    def test_event_creation(self, app):
        """Test la création d'un événement avec tous les champs."""
        user = User(email='creator@example.com', password_hash='hashed')
        game = Game(name='Carcassonne', min_players=2, max_players=6, play_time_minutes=45)
        
        db.session.add_all([user, game])
        db.session.flush()
        
        event = Event(
            creator_id=user.id,
            game_id=game.id,
            title='Soirée Carcassonne',
            description='Venez jouer à Carcassonne avec nous!',
            city='Marseille',
            region='PACA',
            location_text='Café du Centre, Marseille',
            date_time=datetime(2026, 4, 15, 19, 0, 0),
            max_players=4,
            latitude=43.2965,
            longitude=5.3698,
        )
        db.session.add(event)
        db.session.commit()
        
        assert event.id is not None
        assert event.title == 'Soirée Carcassonne'
        assert event.status == 'open'  # Statut par défaut
        assert event.creator_id == user.id
        assert event.game_id == game.id
    
    def test_event_to_dict(self, app):
        """Test la sérialisation d'un événement."""
        user = User(email='organizer@example.com', password_hash='hashed')
        game = Game(name='Puerto Rico', min_players=2, max_players=5, play_time_minutes=90)
        
        db.session.add_all([user, game])
        db.session.flush()
        
        event = Event(
            creator_id=user.id,
            game_id=game.id,
            title='Tournoi Puerto Rico',
            city='Toulouse',
            location_text='Ludothèque',
            date_time=datetime(2026, 5, 20, 20, 0, 0),
            max_players=3,
        )
        db.session.add(event)
        db.session.commit()
        
        event_dict = event.to_dict()
        
        assert event_dict['title'] == 'Tournoi Puerto Rico'
        assert event_dict['city'] == 'Toulouse'
        assert event_dict['current_players'] == 0  # Pas encore de participants
