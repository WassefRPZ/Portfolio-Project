"""
Tests unitaires pour le modèle FavoriteGame (relation M2M).

Ce module teste:
- Ajout de jeux aux favoris
- Relation avec User et Game
- Contrainte d'unicité (user + game)

Utilisation:
  pytest tests/models/test_favorite_game.py                    # Lance tous les tests
  pytest tests/models/test_favorite_game.py -v               # Mode verbeux
  pytest tests/models/test_favorite_game.py --cov=app.models # Avec couverture de code
"""

import pytest
from flask import Flask

from app import db
from app.models import User, Game, FavoriteGame


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


class TestFavoriteGame:
    """
    Suite de tests pour le modèle FavoriteGame (relation M2M).
    
    Teste:
    - Ajout de jeux aux favoris
    - Relation avec User et Game
    - Contrainte d'unicité (user + game)
    """
    
    def test_favorite_game_creation(self, app):
        """Test l'ajout d'un jeu aux favoris."""
        user = User(email='fan@example.com', password_hash='hashed')
        game = Game(name='7 Wonders', min_players=3, max_players=7, play_time_minutes=45)
        
        db.session.add_all([user, game])
        db.session.flush()
        
        favorite = FavoriteGame(user_id=user.id, game_id=game.id)
        db.session.add(favorite)
        db.session.commit()
        
        assert favorite.user_id == user.id
        assert favorite.game_id == game.id
        assert favorite.added_at is not None
    
    def test_favorite_game_unique_per_user(self, app):
        """Test qu'un utilisateur ne peut ajouter un jeu aux favoris qu'une fois."""
        user = User(email='collector@example.com', password_hash='hashed')
        game = Game(name='Splendor', min_players=2, max_players=4, play_time_minutes=30)
        
        db.session.add_all([user, game])
        db.session.flush()
        
        fav1 = FavoriteGame(user_id=user.id, game_id=game.id)
        db.session.add(fav1)
        db.session.commit()
        
        fav2 = FavoriteGame(user_id=user.id, game_id=game.id)
        db.session.add(fav2)
        with pytest.raises(Exception):  # Violation UNIQUE
            db.session.commit()
