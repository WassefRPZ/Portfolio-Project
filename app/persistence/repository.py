from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app import db
from app.models import (
    User, Profile, Game, Event, EventParticipant,
    EventComment, Friend, FavoriteGame, Post, Review
)


class SQLAlchemyRepository:
    """
    Classe de base — fournit les opérations CRUD communes.
    Chaque sous-classe spécialise les requêtes pour son modèle.
    """

    def __init__(self, model):
        self.model = model

    def get_all(self):
        return self.model.query.all()

    def save(self, obj):
        """Ajoute l'objet en session et commit immédiatement."""
        db.session.add(obj)
        db.session.commit()
        return obj

    def delete(self, obj):
        """Supprime l'objet en session et commit immédiatement."""
        db.session.delete(obj)
        db.session.commit()

    def commit(self):
        """Commit les changements déjà en session (utile pour les mises à jour)."""
        db.session.commit()


# =============================================================================
# USERS
# =============================================================================

class UserRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(User)

    def get_by_id(self, user_id):
        return User.query.filter_by(id=user_id).first()

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_by_username(self, username):
        """Cherche un utilisateur via son profil (username est dans profiles)."""
        return (
            User.query
            .join(Profile, User.id == Profile.user_id)
            .filter(Profile.username == username)
            .first()
        )

    def search(self, query, city=None):
        """Recherche par username ou ville via join avec profiles."""
        q = (
            User.query
            .join(Profile, User.id == Profile.user_id)
        )
        if query:
            q = q.filter(Profile.username.like(f'%{query}%'))
        if city:
            q = q.filter(Profile.city == city)
        return q.limit(20).all()


# =============================================================================
# PROFILES
# =============================================================================

class ProfileRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(Profile)

    def get_by_user_id(self, user_id):
        return Profile.query.filter_by(user_id=user_id).first()

    def get_by_username(self, username):
        return Profile.query.filter_by(username=username).first()


# =============================================================================
# GAMES
# =============================================================================

class GameRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(Game)

    def get_by_id(self, game_id):
        return Game.query.filter_by(id=game_id).first()

    def get_by_api_id(self, id_api):
        """Recherche un jeu par son identifiant Board Game Atlas."""
        return Game.query.filter_by(id_api=id_api).first()

    def get_by_name(self, name):
        return Game.query.filter_by(name=name).first()

    def get_all_ordered(self):
        return Game.query.order_by(Game.name).all()

    def search(self, query):
        return Game.query.filter(Game.name.like(f'%{query}%')).limit(10).all()

    def get_popular(self):
        """Retourne les jeux les plus utilisés dans les événements."""
        return (
            db.session.query(Game, func.count(Event.id).label('total'))
            .join(Event, Game.id == Event.game_id)
            .group_by(Game.id)
            .order_by(func.count(Event.id).desc())
            .limit(10)
            .all()
        )


# =============================================================================
# EVENTS
# =============================================================================

class EventRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(Event)

    def get_by_id(self, event_id):
        return Event.query.filter_by(id=event_id).first()

    def get_by_id_full(self, event_id):
        """Chargement complet avec joinedload — évite le problème N+1."""
        return (
            Event.query
            .options(
                joinedload(Event.creator),
                joinedload(Event.game_obj),
                joinedload(Event.participants),
            )
            .filter_by(id=event_id)
            .first()
        )

    def get_open_events(self, city=None, date=None):
        """Retourne les événements ouverts, avec filtres optionnels."""
        q = (
            Event.query
            .options(
                joinedload(Event.game_obj),
                joinedload(Event.participants),
            )
            .filter_by(status='open')
        )

        if city:
            q = q.filter_by(city=city)

        if date:
            try:
                target = datetime.fromisoformat(date)
                q = q.filter(db.func.date(Event.date_time) == target.date())
            except (ValueError, TypeError):
                return None, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25)"

        return q.order_by(Event.date_time).limit(50).all(), None

    def get_by_creator(self, creator_id):
        return Event.query.filter_by(creator_id=creator_id).all()

    def get_by_ids(self, event_ids):
        """Récupère plusieurs événements en une seule requête."""
        if not event_ids:
            return []
        return Event.query.filter(Event.id.in_(event_ids)).all()

    def get_by_game(self, game_id):
        return (
            Event.query
            .filter_by(game_id=game_id, status='open')
            .order_by(Event.date_time)
            .all()
        )


# =============================================================================
# EVENT PARTICIPANTS
# =============================================================================

class EventParticipantRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(EventParticipant)

    def get(self, event_id, user_id, status='confirmed'):
        return EventParticipant.query.filter_by(
            event_id=event_id, user_id=user_id, status=status
        ).first()

    def get_any(self, event_id, user_id):
        """Retourne la participation quel que soit le statut."""
        return EventParticipant.query.filter_by(
            event_id=event_id, user_id=user_id
        ).first()

    def count_confirmed(self, event_id):
        return EventParticipant.query.filter_by(
            event_id=event_id, status='confirmed'
        ).count()

    def get_confirmed_by_user(self, user_id):
        return EventParticipant.query.filter_by(
            user_id=user_id, status='confirmed'
        ).all()


# =============================================================================
# EVENT COMMENTS
# =============================================================================

class EventCommentRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(EventComment)

    def get_by_event(self, event_id):
        """Charge les commentaires avec leurs auteurs en une seule requête."""
        return (
            EventComment.query
            .options(joinedload(EventComment.author))
            .filter_by(event_id=event_id)
            .order_by(EventComment.created_at)
            .all()
        )


# =============================================================================
# FRIENDS
# =============================================================================

class FriendRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(Friend)

    def get(self, user_id_1, user_id_2):
        """Retourne la relation entre deux utilisateurs (ordre normalisé côté facade)."""
        return Friend.query.filter_by(
            user_id_1=user_id_1, user_id_2=user_id_2
        ).first()

    def get_with_status(self, user_id_1, user_id_2, status):
        return Friend.query.filter_by(
            user_id_1=user_id_1, user_id_2=user_id_2, status=status
        ).first()

    def get_accepted(self, user_id):
        return (
            Friend.query
            .options(joinedload(Friend.user1), joinedload(Friend.user2))
            .filter(
                Friend.status == 'accepted',
                (Friend.user_id_1 == user_id) | (Friend.user_id_2 == user_id)
            )
            .all()
        )

    def get_pending_received(self, user_id):
        """Demandes en attente reçues par user_id (il est dans la relation mais n'est pas l'expéditeur)."""
        return (
            Friend.query
            .options(joinedload(Friend.requester))
            .filter(
                Friend.status == 'pending',
                (Friend.user_id_1 == user_id) | (Friend.user_id_2 == user_id),
                Friend.requester_id != user_id,
            )
            .all()
        )


# =============================================================================
# FAVORITE GAMES
# =============================================================================

class FavoriteGameRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(FavoriteGame)

    def get(self, user_id, game_id):
        return FavoriteGame.query.filter_by(
            user_id=user_id, game_id=game_id
        ).first()

    def get_games_for_user(self, user_id):
        """Retourne les objets Game favoris d'un utilisateur via un JOIN direct."""
        return (
            db.session.query(Game)
            .join(FavoriteGame, Game.id == FavoriteGame.game_id)
            .filter(FavoriteGame.user_id == user_id)
            .all()
        )


# =============================================================================
# POSTS
# =============================================================================

class PostRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(Post)

    def get_recent(self, limit=20):
        """Retourne les posts les plus récents pour le fil d'actualité."""
        return (
            Post.query
            .options(joinedload(Post.author))
            .order_by(Post.created_at.desc())
            .limit(limit)
            .all()
        )


# =============================================================================
# REVIEWS
# =============================================================================

class ReviewRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(Review)

    def get_by_event(self, event_id):
        return Review.query.filter_by(event_id=event_id).all()

    def get_by_reviewed_user(self, reviewed_user_id):
        return Review.query.filter_by(reviewed_user_id=reviewed_user_id).all()
