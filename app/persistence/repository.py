from datetime import datetime
from math import radians, cos, sin, acos
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app import db
from app.models import (
    User, Profile, Game, Event, EventParticipant,
    EventComment, FavoriteGame, Friend, Post
)


class SQLAlchemyRepository:

    def save(self, obj):
        db.session.add(obj)
        db.session.commit()
        return obj

    def delete(self, obj):
        db.session.delete(obj)
        db.session.commit()

    def commit(self):
        db.session.commit()



class UserRepository(SQLAlchemyRepository):

    def get_by_id(self, user_id):
        return User.query.filter_by(id=user_id).first()

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def search(self, query, city=None):
        q = (
            User.query
            .join(Profile, User.id == Profile.user_id)
        )
        if query:
            safe_q = query.replace('%', r'\%').replace('_', r'\_')
            q = q.filter(Profile.username.like(f'%{safe_q}%'))
        if city:
            q = q.filter(Profile.city == city)
        return q.limit(20).all()



class ProfileRepository(SQLAlchemyRepository):

    def get_by_user_id(self, user_id):
        return Profile.query.filter_by(user_id=user_id).first()

    def get_by_username(self, username):
        return Profile.query.filter_by(username=username).first()



class GameRepository(SQLAlchemyRepository):

    def get_by_id(self, game_id):
        return Game.query.filter_by(id=game_id).first()

    def get_all(self, limit=50, offset=0):
        return Game.query.order_by(Game.name).offset(offset).limit(limit).all()

    def search(self, query, limit=20):
        safe_q = query.replace('%', r'\%').replace('_', r'\_')
        return (
            Game.query
            .filter(Game.name.like(f'%{safe_q}%'))
            .order_by(Game.name)
            .limit(limit)
            .all()
        )

    def count(self):
        return Game.query.count()



class EventRepository(SQLAlchemyRepository):

    def get_by_id(self, event_id):
        return Event.query.filter_by(id=event_id).first()

    def get_by_id_full(self, event_id):
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

    def get_open_events(self, city=None, date=None, limit=50, offset=0,
                         lat=None, lng=None, radius=10):
        base = Event.query.filter_by(status='open')

        if city:
            base = base.filter_by(city=city)

        if date:
            try:
                target = datetime.fromisoformat(date)
                base = base.filter(db.func.date(Event.date_time) == target.date())
            except (ValueError, TypeError):
                return None, 0, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25)"

        if lat is not None and lng is not None:
            lat_r  = radians(lat)
            haversine = (
                6371 * db.func.acos(
                    cos(lat_r)
                    * db.func.cos(db.func.radians(Event.latitude))
                    * db.func.cos(db.func.radians(Event.longitude) - radians(lng))
                    + sin(lat_r)
                    * db.func.sin(db.func.radians(Event.latitude))
                )
            )
            base = base.filter(
                Event.latitude.isnot(None),
                Event.longitude.isnot(None),
                haversine <= radius,
            )

        total_count = base.with_entities(func.count(Event.id)).scalar()
        events = (
            base
            .options(joinedload(Event.game_obj), joinedload(Event.participants))
            .order_by(Event.date_time)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return events, total_count, None

    def search(self, query):
        safe_q = query.replace('%', r'\%').replace('_', r'\_')
        pattern = f'%{safe_q}%'
        return (
            Event.query
            .filter(
                Event.status == 'open',
                db.or_(
                    Event.title.like(pattern),
                    Event.description.like(pattern),
                )
            )
            .order_by(Event.date_time)
            .limit(20)
            .all()
        )



class EventParticipantRepository(SQLAlchemyRepository):

    def get(self, event_id, user_id, status='confirmed'):
        return EventParticipant.query.filter_by(
            event_id=event_id, user_id=user_id, status=status
        ).first()

    def get_any(self, event_id, user_id):
        return EventParticipant.query.filter_by(
            event_id=event_id, user_id=user_id
        ).first()

    def count_confirmed(self, event_id):
        return EventParticipant.query.filter_by(
            event_id=event_id, status='confirmed'
        ).count()



class EventCommentRepository(SQLAlchemyRepository):

    def get_by_event(self, event_id, limit=50, offset=0):
        return (
            EventComment.query
            .options(joinedload(EventComment.author).joinedload(User.profile))
            .filter_by(event_id=event_id)
            .order_by(EventComment.created_at)
            .offset(offset)
            .limit(limit)
            .all()
        )



class FavoriteGameRepository(SQLAlchemyRepository):

    def get(self, user_id, game_id):
        return FavoriteGame.query.filter_by(
            user_id=user_id, game_id=game_id
        ).first()

    def get_games_for_user(self, user_id):
        return (
            db.session.query(Game)
            .join(FavoriteGame, Game.id == FavoriteGame.game_id)
            .filter(FavoriteGame.user_id == user_id)
            .all()
        )



class FriendRepository(SQLAlchemyRepository):

    def _sorted_ids(self, a, b):
        return (min(a, b), max(a, b))

    def get_friendship(self, user_a, user_b):
        u1, u2 = self._sorted_ids(user_a, user_b)
        return Friend.query.filter_by(user_id_1=u1, user_id_2=u2).first()

    def get_friends(self, user_id):
        return (
            Friend.query
            .filter(
                Friend.status == 'accepted',
                db.or_(
                    Friend.user_id_1 == user_id,
                    Friend.user_id_2 == user_id,
                )
            )
            .all()
        )

    def get_pending_received(self, user_id):
        return (
            Friend.query
            .filter(
                Friend.status == 'pending',
                Friend.requester_id != user_id,
                db.or_(
                    Friend.user_id_1 == user_id,
                    Friend.user_id_2 == user_id,
                )
            )
            .all()
        )

    def get_pending_sent(self, user_id):
        return (
            Friend.query
            .filter(
                Friend.status == 'pending',
                Friend.requester_id == user_id,
            )
            .all()
        )


class PostRepository(SQLAlchemyRepository):

    def get_by_id(self, post_id):
        return db.session.get(Post, post_id)

    def get_all(self, limit=50, offset=0):
        total = Post.query.count()
        posts = (
            Post.query
            .order_by(Post.created_at.desc())
            .offset(offset).limit(limit)
            .all()
        )
        return posts, total

    def get_by_author(self, author_id, limit=50, offset=0):
        total = Post.query.filter_by(author_id=author_id).count()
        posts = (
            Post.query
            .filter_by(author_id=author_id)
            .order_by(Post.created_at.desc())
            .offset(offset).limit(limit)
            .all()
        )
        return posts, total



