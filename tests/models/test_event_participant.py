"""
Tests unitaires pour les événements et leurs participants.

Ce module teste:
- Inscription d'utilisateurs aux événements
- Statut de participation (confirmed, pending)
- Comptage des participants

Utilisation:
  pytest tests/models/test_event_participant.py                    # Lance tous les tests
  pytest tests/models/test_event_participant.py -v               # Mode verbeux
  pytest tests/models/test_event_participant.py --cov=app.models # Avec couverture de code
"""

import pytest
from datetime import datetime
from flask import Flask

from app import db
from app.models import User, Game, Event, EventParticipant


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


class TestEventWithParticipants:
    """
    Suite de tests pour les événements et leurs participants.
    
    Teste:
    - Inscription d'utilisateurs aux événements
    - Statut de participation (confirmed, pending)
    - Comptage des participants
    """
    
    def test_event_participant_join(self, app):
        """Test qu'un utilisateur peut rejoindre un événement."""
        creator = User(email='creator@example.com', password_hash='h1')
        participant = User(email='player@example.com', password_hash='h2')
        game = Game(name='Dominion', min_players=2, max_players=4, play_time_minutes=45)
        
        db.session.add_all([creator, participant, game])
        db.session.flush()
        
        event = Event(
            creator_id=creator.id,
            game_id=game.id,
            title='Partie Dominion',
            city='Bordeaux',
            location_text='Salle de jeu',
            date_time=datetime(2026, 6, 1, 18, 0, 0),
            max_players=4,
        )
        db.session.add(event)
        db.session.flush()
        
        # Le créateur est auto-participant
        creator_participation = EventParticipant(
            event_id=event.id,
            user_id=creator.id,
            status='confirmed',
        )
        
        # Un autre utilisateur rejoint
        player_participation = EventParticipant(
            event_id=event.id,
            user_id=participant.id,
            status='confirmed',
        )
        
        db.session.add_all([creator_participation, player_participation])
        db.session.commit()
        
        # Vérifie que les deux sont participants
        confirmeds = [p for p in event.participants if p.status == 'confirmed']
        assert len(confirmeds) == 2
    
    def test_event_participant_to_dict(self, app):
        """Test la sérialisation d'une participation."""
        user = User(email='gamer@example.com', password_hash='hashed')
        game = Game(name='Azul', min_players=2, max_players=4, play_time_minutes=30)
        
        db.session.add_all([user, game])
        db.session.flush()
        
        event = Event(
            creator_id=user.id,
            game_id=game.id,
            title='Tournoi Azul',
            city='Nantes',
            location_text='Club de jeu',
            date_time=datetime(2026, 7, 10, 19, 0, 0),
            max_players=3,
        )
        db.session.add(event)
        db.session.flush()
        
        participation = EventParticipant(
            event_id=event.id,
            user_id=user.id,
            status='confirmed',
        )
        db.session.add(participation)
        db.session.commit()
        
        part_dict = participation.to_dict()
        
        assert part_dict['status'] == 'confirmed'
        assert part_dict['user_id'] == user.id
        assert part_dict['event_id'] == event.id
