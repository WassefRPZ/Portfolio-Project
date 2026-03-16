"""
Tests unitaires pour les modèles de données.

Ce module teste les modèles SQLAlchemy:
- Création d'instances
- Validations des champs
- Relations ORM (relationships)
- Méthodes de sérialisation (to_dict, to_public_dict)
- Contraintes d'unicité et d'intégrité

Utilisation:
  pytest tests/test_models.py                        # Lance tous les tests
  pytest tests/test_models.py::TestUser::test_*      # Lance tests spécifiques User
  pytest tests/test_models.py -v                     # Mode verbeux
  pytest tests/test_models.py --cov=app.models       # Avec couverture de code
"""

import pytest
from datetime import datetime, timezone
from flask import Flask
from werkzeug.security import check_password_hash

from app import db
from app.models import (
    User, Profile, Game, Event, EventParticipant,
    EventComment, FavoriteGame, Friend, Post
)


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
        db.create_all()  # Crée toutes les tables
        yield test_app
        db.session.remove()
        db.drop_all()  # Nettoie après le test


@pytest.fixture
def client(app):
    """Fixture pytest: Fournit un client de test Flask."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture pytest: Fournit un test CLI runner."""
    return app.test_cli_runner()


# ================================================================
# TESTS DU MODÈLE USER
# ================================================================

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


# ================================================================
# TESTS DU MODÈLE PROFILE
# ================================================================

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


# ================================================================
# TESTS DU MODÈLE GAME
# ================================================================

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


# ================================================================
# TESTS DU MODÈLE EVENT
# ================================================================

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


# ================================================================
# TESTS DU MODÈLE GAME FAVORI
# ================================================================

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


# ================================================================
# TESTS DU MODÈLE RELATION D'AMI
# ================================================================

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


# ================================================================
# TESTS DU MODÈLE POST
# ================================================================

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


# ================================================================
# TESTS DU MODÈLE ÉVÉNEMENT AVEC PARTICIPANTS
# ================================================================

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


# ================================================================
# TESTS DU MODÈLE COMMENTAIRE D'ÉVÉNEMENT
# ================================================================

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
