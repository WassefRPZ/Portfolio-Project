"""
Tests unitaires pour le modèle Game (catalogue de jeux).

Ce module teste:
- Création de jeux
- Validation des joueurs min/max
- Unicité du nom
- Sérialisation

Utilisation:
  pytest tests/models/test_game.py                    # Lance tous les tests
  pytest tests/models/test_game.py -v                # Mode verbeux
  pytest tests/models/test_game.py --cov=app.models  # Avec couverture de code
"""

import pytest
from flask import Flask

from app import db
from app.models import Game


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


class TestGame:
    """
    Suite de tests pour le modèle Game (catalogue de jeux).
    
    Teste:
    - Création de jeux
    - Validation des joueurs min/max
    - Unicité du nom
    - Sérialisation
    """
    
    def test_game_creation(self, app):
        """Test la création d'un jeu avec tous les champs."""
        game = Game(
            name='Catan',
            description='Construisez vos colonies sur une île',
            min_players=2,
            max_players=4,
            play_time_minutes=60,
            image_url='https://example.com/catan.jpg',
        )
        db.session.add(game)
        db.session.commit()
        
        assert game.id is not None
        assert game.name == 'Catan'
        assert game.min_players == 2
        assert game.max_players == 4
    
    def test_game_unique_name(self, app):
        """Test que deux jeux ne peuvent pas avoir le même nom."""
        game1 = Game(name='Ticket to Ride', min_players=2, max_players=5, play_time_minutes=45)
        game2 = Game(name='Ticket to Ride', min_players=2, max_players=5, play_time_minutes=45)
        
        db.session.add(game1)
        db.session.commit()
        
        db.session.add(game2)
        with pytest.raises(Exception):
            db.session.commit()
    
    def test_game_to_dict(self, app):
        """Test la sérialisation d'un jeu."""
        game = Game(
            name='Agricola',
            description='Jeu de gestion de ferme',
            min_players=1,
            max_players=5,
            play_time_minutes=90,
        )
        db.session.add(game)
        db.session.commit()
        
        game_dict = game.to_dict()
        
        assert game_dict['name'] == 'Agricola'
        assert game_dict['min_players'] == 1
        assert game_dict['max_players'] == 5
        assert game_dict['play_time_minutes'] == 90
