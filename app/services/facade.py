import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Game, Event, EventParticipant, Comment, Friendship, FavoriteGame
from app.persistence.repository import (
    UserRepository, GameRepository, EventRepository,
    EventParticipantRepository, CommentRepository,
    FriendshipRepository, FavoriteGameRepository,
)


class BoardGameFacade:
    """
    Couche métier centrale. Toutes les routes API passent par ici.

    """

    def __init__(self):
        self.users        = UserRepository()
        self.games        = GameRepository()
        self.events       = EventRepository()
        self.participants = EventParticipantRepository()
        self.comments     = CommentRepository()
        self.friendships  = FriendshipRepository()
        self.favorites    = FavoriteGameRepository()

    # ==========================================
    # AUTH
    # ==========================================

    def register_user(self, data):
        for field in ['username', 'email', 'password', 'city']:
            if not data.get(field):
                return None, f"Le champ '{field}' est requis"

        if self.users.get_by_email(data['email']):
            return None, "Cet email est déjà utilisé"

        if self.users.get_by_username(data['username']):
            return None, "Ce nom d'utilisateur est déjà pris"

        user = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            city=data['city'],
            region=data.get('region', ''),
            bio=data.get('bio', ''),
        )
        self.users.save(user)
        return user.to_dict(), None

    def login_user(self, email, password):
        user = self.users.get_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            return user.to_dict()
        return None

    # ==========================================
    # UTILISATEURS
    # ==========================================

    def get_user(self, user_id):
        user = self.users.get_by_id(user_id)
        if not user:
            return None
        user_data = user.to_dict()
        user_data['favorite_games'] = self.get_favorite_games(user_id)
        return user_data

    def update_user_profile(self, user_id, data):
        user = self.users.get_by_id(user_id)
        if not user:
            return None, "Utilisateur introuvable"

        if 'username' in data and data['username'] != user.username:
            if self.users.get_by_username(data['username']):
                return None, "Ce nom d'utilisateur est déjà pris"

        for field in ['username', 'first_name', 'last_name', 'city', 'region', 'bio', 'profile_image_url']:
            if field in data:
                setattr(user, field, data[field])

        self.users.commit()
        return user.to_dict(), None

    def search_users(self, query, city=None):
        return [u.to_dict() for u in self.users.search(query, city)]

    def get_user_events(self, user_id):
        # Événements créés
        created = self.events.get_by_creator(user_id)

        # Événements rejoints
        participations = self.participants.get_confirmed_by_user(user_id)
        joined_ids = [p.event_id for p in participations]
        joined = self.events.get_by_ids(joined_ids)

        # Déduplication
        all_events = {e.event_id: e for e in created + joined}
        return [e.to_dict() for e in all_events.values()]

    # ==========================================
    # ÉVÉNEMENTS
    # ==========================================

    def get_events(self, city=None, date=None):
        events, error = self.events.get_open_events(city=city, date=date)
        if error:
            return [], error

        result = []
        for event in events:
            event_data = event.to_dict()
            # game_obj déjà chargé via joinedload
            if event.game_obj:
                event_data['game'] = event.game_obj.to_dict()
            result.append(event_data)
        return result, None

    def get_event_details(self, event_id):
        event = self.events.get_by_id_full(event_id)
        if not event:
            return None

        event_data = event.to_dict(include_participants=True)
        if event.game_obj:
            event_data['game'] = event.game_obj.to_dict()
        if event.creator:
            event_data['creator'] = event.creator.to_dict()
        return event_data

    def create_event(self, data, creator_id):
        if not self.games.get_by_id(data['game_id']):
            return None, "Ce jeu n'existe pas"

        try:
            event_date_time = datetime.fromisoformat(data['date_time'])
        except (ValueError, TypeError):
            return None, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25T19:00:00)"

        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            creator_id=creator_id,
            game_id=data['game_id'],
            title=data['title'],
            description=data.get('description', ''),
            city=data['city'],
            region=data.get('region', ''),
            location_text=data['location_text'],
            date_time=event_date_time,
            max_players=data['max_players'],
        )
        self.events.save(event)
        return event.to_dict(), None

    def update_event(self, event_id, data):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"

        if 'max_players' in data:
            current_count = self.participants.count_confirmed(event_id)
            if data['max_players'] < current_count:
                return None, (
                    f"Impossible de réduire à {data['max_players']} : "
                    f"{current_count} participants sont déjà confirmés"
                )

        for field in ['title', 'description', 'city', 'region', 'location_text', 'max_players']:
            if field in data:
                setattr(event, field, data[field])

        if 'date_time' in data:
            try:
                event.date_time = datetime.fromisoformat(data['date_time'])
            except (ValueError, TypeError):
                return None, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25T19:00:00)"

        self.events.commit()
        return event.to_dict(), None

    def cancel_event(self, event_id):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"
        if event.status == 'cancelled':
            return None, "Cet événement est déjà annulé"

        event.status = 'cancelled'
        self.events.commit()
        return event.to_dict(), None

    def join_event(self, event_id, user_id):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"

        if self.participants.get(event_id, user_id, status='confirmed'):
            return None, "Vous participez déjà à cet événement"

        count = self.participants.count_confirmed(event_id)
        if count >= event.max_players:
            return None, "Événement complet"

        participation = EventParticipant(
            participant_id=f"prt_{uuid.uuid4().hex[:8]}",
            event_id=event_id,
            user_id=user_id,
            status='confirmed',
        )
        # Ajout de la participation
        db.session.add(participation)
        if count + 1 >= event.max_players:
            event.status = 'full'
        db.session.commit()

        return participation.to_dict(), None

    def leave_event(self, event_id, user_id):
        participation = self.participants.get(event_id, user_id, status='confirmed')
        if not participation:
            return None, "Vous ne participez pas à cet événement"

        event = self.events.get_by_id(event_id)

        # Suppression de la participation
        db.session.delete(participation)
        if event and event.status == 'full':
            event.status = 'open'
        db.session.commit()

        return {"success": True}, None

    # ==========================================
    # COMMENTAIRES
    # ==========================================

    def get_event_comments(self, event_id):
        comments = self.comments.get_by_event(event_id)
        result = []
        for comment in comments:
            comment_data = comment.to_dict()
            if comment.author:
                comment_data['username'] = comment.author.username
            result.append(comment_data)
        return result

    def add_comment(self, event_id, user_id, content):
        comment = Comment(
            comment_id=f"cmt_{uuid.uuid4().hex[:8]}",
            event_id=event_id,
            user_id=user_id,
            content=content,
        )
        self.comments.save(comment)
        comment_data = comment.to_dict()
        if comment.author:
            comment_data['username'] = comment.author.username
        return comment_data, None

    # ==========================================
    # AMIS
    # ==========================================

    def get_friends(self, user_id):
        friendships = self.friendships.get_accepted(user_id)
        friends = []
        for f in friendships:
            friend = f.user2 if f.user_id_1 == user_id else f.user1
            if friend:
                friends.append(friend.to_dict())
        return friends

    def get_pending_requests(self, user_id):
        pending = self.friendships.get_pending_received(user_id)
        result = []
        for f in pending:
            if f.action_user:
                result.append({
                    "friendship": f.to_dict(),
                    "requester":  f.action_user.to_dict(),
                })
        return result

    def add_friend(self, requester_id, receiver_id):
        if requester_id == receiver_id:
            return None, "Vous ne pouvez pas vous ajouter vous-même"

        if not self.users.get_by_id(receiver_id):
            return None, "Utilisateur introuvable"

        user_id_1, user_id_2 = sorted([requester_id, receiver_id])

        if self.friendships.get(user_id_1, user_id_2):
            return None, "Une demande existe déjà entre vous"

        friendship = Friendship(
            user_id_1=user_id_1,
            user_id_2=user_id_2,
            action_user_id=requester_id,
            status='pending',
        )
        self.friendships.save(friendship)
        return friendship.to_dict(), None

    def accept_friend(self, current_user_id, requester_id):
        user_id_1, user_id_2 = sorted([current_user_id, requester_id])
        friendship = self.friendships.get_with_status(user_id_1, user_id_2, 'pending')

        if not friendship:
            return None, "Demande introuvable"
        if friendship.action_user_id == current_user_id:
            return None, "Vous ne pouvez pas accepter votre propre demande"

        friendship.status = 'accepted'
        self.friendships.commit()
        return friendship.to_dict(), None

    def decline_friend(self, current_user_id, requester_id):
        user_id_1, user_id_2 = sorted([current_user_id, requester_id])
        friendship = self.friendships.get_with_status(user_id_1, user_id_2, 'pending')

        if not friendship:
            return None, "Demande introuvable"
        if friendship.action_user_id == current_user_id:
            return None, "Vous ne pouvez pas refuser votre propre demande"

        friendship.status = 'declined'
        self.friendships.commit()
        return friendship.to_dict(), None

    def remove_friend(self, current_user_id, friend_id):
        user_id_1, user_id_2 = sorted([current_user_id, friend_id])
        friendship = self.friendships.get_with_status(user_id_1, user_id_2, 'accepted')

        if not friendship:
            return None, "Cet utilisateur n'est pas dans vos amis"

        self.friendships.delete(friendship)
        return {"success": True}, None

    # ==========================================
    # JEUX FAVORIS
    # ==========================================

    def get_favorite_games(self, user_id):
        return [g.to_dict() for g in self.favorites.get_games_for_user(user_id)]

    def add_favorite_game(self, user_id, game_id):
        if not self.games.get_by_id(game_id):
            return None, "Jeu introuvable"
        if self.favorites.get(user_id, game_id):
            return None, "Jeu déjà dans vos favoris"

        favorite = FavoriteGame(user_id=user_id, game_id=game_id)
        self.favorites.save(favorite)
        return favorite.to_dict(), None

    def remove_favorite_game(self, user_id, game_id):
        favorite = self.favorites.get(user_id, game_id)
        if not favorite:
            return None, "Ce jeu n'est pas dans vos favoris"

        self.favorites.delete(favorite)
        return {"success": True}, None

    # ==========================================
    # JEUX
    # ==========================================

    def get_all_games(self):
        return [g.to_dict() for g in self.games.get_all_ordered()]

    def get_game(self, game_id):
        game = self.games.get_by_id(game_id)
        return game.to_dict() if game else None

    def get_game_by_name(self, name):
        return self.games.get_by_name(name)

    def search_games(self, query):
        return [g.to_dict() for g in self.games.search(query)]

    def get_popular_games(self):
        popular = []
        for game, total in self.games.get_popular():
            game_data = game.to_dict()
            game_data['event_count'] = total
            popular.append(game_data)
        return popular

    def create_game(self, data):
        if data['min_players'] > data['max_players']:
            return None, "min_players ne peut pas dépasser max_players"

        game = Game(
            game_id=f"game_{uuid.uuid4().hex[:8]}",
            name=data['name'],
            description=data.get('description', ''),
            min_players=data['min_players'],
            max_players=data['max_players'],
            play_time_minutes=data['play_time_minutes'],
            image_url=data.get('image_url', ''),
        )
        self.games.save(game)
        return game.to_dict(), None

    def update_game(self, game_id, data):
        game = self.games.get_by_id(game_id)
        if not game:
            return None, "Jeu introuvable"

        min_p = data.get('min_players', game.min_players)
        max_p = data.get('max_players', game.max_players)
        if min_p > max_p:
            return None, "min_players ne peut pas dépasser max_players"

        for field in ['name', 'description', 'min_players', 'max_players', 'play_time_minutes', 'image_url']:
            if field in data:
                setattr(game, field, data[field])

        self.games.commit()
        return game.to_dict(), None

    def get_events_by_game(self, game_id):
        return [e.to_dict() for e in self.events.get_by_game(game_id)]
