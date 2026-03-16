"""
Tests unitaires pour les commentaires d'événements.

Ce module teste:
- Création de commentaires
- Relation avec Event et Author
- Sérialisation

Utilisation:
  pytest tests/models/test_event_comment.py                    # Lance tous les tests
  pytest tests/models/test_event_comment.py -v               # Mode verbeux
  pytest tests/models/test_event_comment.py --cov=app.models # Avec couverture de code
"""

import pytest
from datetime import datetime
from flask import Flask

from app import db
from app.models import User, Game, Event, EventComment


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


class TestEventComment:
    """
    Suite de tests pour les commentaires d'événements.
    
    Teste:
    - Création de commentaires
    - Relation avec Event et Author
    - Sérialisation
    """
    
    def test_event_comment_creation(self, app):
        """Test la création d'un commentaire sur un événement."""
        user = User(email='commenter@example.com', password_hash='hashed')
        game = Game(name='Pandemic', min_players=2, max_players=4, play_time_minutes=45)
        
        db.session.add_all([user, game])
        db.session.flush()
        
        event = Event(
            creator_id=user.id,
            game_id=game.id,
            title='Sauvez le monde!',
            city='Nice',
            location_text='Ludothèque',
            date_time=datetime(2026, 8, 15, 19, 0, 0),
            max_players=4,
        )
        db.session.add(event)
        db.session.flush()
        
        comment = EventComment(
            event_id=event.id,
            user_id=user.id,
            content='Excited for this game night!',
        )
        db.session.add(comment)
        db.session.commit()
        
        assert comment.content == 'Excited for this game night!'
        assert comment.event_id == event.id
        assert comment.user_id == user.id
        assert comment.created_at is not None
    
    def test_event_comment_to_dict(self, app):
        """Test la sérialisation d'un commentaire."""
        user = User(email='reviewer@example.com', password_hash='hashed')
        game = Game(name='Ticket to Ride', min_players=2, max_players=5, play_time_minutes=45)
        
        db.session.add_all([user, game])
        db.session.flush()
        
        event = Event(
            creator_id=user.id,
            game_id=game.id,
            title='Railway Builder',
            city='Strasbourg',
            location_text='Salle',
            date_time=datetime(2026, 9, 5, 20, 0, 0),
            max_players=5,
        )
        db.session.add(event)
        db.session.flush()
        
        comment = EventComment(
            event_id=event.id,
            user_id=user.id,
            content='Super jeu, vivement la prochaine!',
        )
        db.session.add(comment)
        db.session.commit()
        
        comment_dict = comment.to_dict()
        
        assert comment_dict['content'] == 'Super jeu, vivement la prochaine!'
        assert comment_dict['user_id'] == user.id
        assert comment_dict['event_id'] == event.id
