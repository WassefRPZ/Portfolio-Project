import os
import re
from datetime import datetime, timezone

import requests
import cloudinary.uploader
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User, Profile, Event, EventParticipant, EventComment, FavoriteGame, Friend, Post
from app.persistence.repository import (
    UserRepository, ProfileRepository, GameRepository,
    EventRepository, EventParticipantRepository,
    EventCommentRepository, FavoriteGameRepository, FriendRepository,
    PostRepository,
)


class BoardGameFacade:

    def __init__(self):
        self.users = UserRepository()
        self.profiles = ProfileRepository()
        self.games = GameRepository()
        self.events = EventRepository()
        self.participants = EventParticipantRepository()
        self.comments = EventCommentRepository()
        self.favorites = FavoriteGameRepository()
        self.friends = FriendRepository()
        self.posts = PostRepository()

    # ── Auth ──────────────────────────────────────────────────────────────

    def register_user(self, data):
        for field in ['username', 'email', 'password', 'city']:
            if not data.get(field):
                return None, f"Le champ '{field}' est requis"

        if len(data['password']) < 8:
            return None, "Le mot de passe doit contenir au minimum 8 caractères"
        if not re.search(r'[A-Z]', data['password']):
            return None, "Le mot de passe doit contenir au moins une lettre majuscule"
        if not re.search(r'[a-z]', data['password']):
            return None, "Le mot de passe doit contenir au moins une lettre minuscule"
        if not re.search(r'\d', data['password']):
            return None, "Le mot de passe doit contenir au moins un chiffre"
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]', data['password']):
            return None, "Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*…)"

        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', data['email']):
            return None, "Format d'email invalide"

        if self.users.get_by_email(data['email']):
            return None, "Cet email est déjà utilisé"

        if self.profiles.get_by_username(data['username']):
            return None, "Ce nom d'utilisateur est déjà pris"

        user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role='user',
        )
        db.session.add(user)
        db.session.flush()

        profile = Profile(
            user_id=user.id,
            username=data['username'],
            bio=data.get('bio', ''),
            city=data['city'],
            region=data.get('region', ''),
        )
        db.session.add(profile)
        db.session.commit()

        user.profile = profile
        return user.to_dict(), None

    def login_user(self, email, password):
        user = self.users.get_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            return user.to_dict(), None
        return None, "Email ou mot de passe incorrect"

    # ── Users ─────────────────────────────────────────────────────────────

    def get_user(self, user_id):
        user = self.users.get_by_id(user_id)
        if not user:
            return None
        user_data = user.to_dict()
        user_data['favorite_games'] = self.get_favorite_games(user_id)
        return user_data

    def update_user_profile(self, user_id, data, image_file=None):
        user = self.users.get_by_id(user_id)
        if not user:
            return None, "Utilisateur introuvable"

        profile = self.profiles.get_by_user_id(user_id)
        if not profile:
            return None, "Profil introuvable"

        if 'username' in data:
            if not data['username'].strip():
                return None, "Le nom d'utilisateur ne peut pas être vide"
            if data['username'] != profile.username:
                if self.profiles.get_by_username(data['username']):
                    return None, "Ce nom d'utilisateur est déjà pris"

        if image_file:
            url, error = self._upload_to_cloudinary(image_file, folder='profiles')
            if error:
                return None, error
            data['profile_image_url'] = url
        else:
            data.pop('profile_image_url', None)

        for field in ['username', 'bio', 'city', 'region', 'profile_image_url']:
            if field in data:
                setattr(profile, field, data[field])

        self.profiles.commit()
        user.profile = profile
        return user.to_dict(), None

    def search_users(self, query, city=None):
        return [u.to_public_dict() for u in self.users.search(query, city)]

    def get_public_user(self, user_id):
        user = self.users.get_by_id(user_id)
        if not user:
            return None
        user_data = user.to_public_dict()
        user_data['favorite_games'] = self.get_favorite_games(user_id)
        return user_data

    # ── Games ─────────────────────────────────────────────────────────────

    def list_games(self, limit=50, offset=0):
        games = self.games.get_all(limit=limit, offset=offset)
        total = self.games.count()
        return [g.to_dict() for g in games], total

    def search_games(self, query):
        return [g.to_dict() for g in self.games.search(query)]

    def get_favorite_games(self, user_id):
        return [g.to_dict() for g in self.favorites.get_games_for_user(user_id)]

    def add_favorite_game(self, user_id, game_id):
        game = self.games.get_by_id(game_id)
        if not game:
            return None, "Jeu introuvable"
        if self.favorites.get(user_id, game_id):
            return None, "Jeu déjà dans vos favoris"

        favorite = FavoriteGame(user_id=user_id, game_id=game_id)
        self.favorites.save(favorite)
        return game.to_dict(), None

    def remove_favorite_game(self, user_id, game_id):
        favorite = self.favorites.get(user_id, game_id)
        if not favorite:
            return None, "Ce jeu n'est pas dans vos favoris"

        self.favorites.delete(favorite)
        return {"success": True}, None

    # ── Events ────────────────────────────────────────────────────────────

    def _geocode(self, location_text):
        api_key = os.getenv('OPENCAGE_API_KEY')
        if not api_key:
            return None, "Clé API OpenCage manquante (OPENCAGE_API_KEY)"

        try:
            response = requests.get(
                'https://api.opencagedata.com/geocode/v1/json',
                params={
                    'q':        location_text,
                    'key':      api_key,
                    'language': 'fr',
                    'limit':    1,
                },
                timeout=5,
            )
            response.raise_for_status()
            body = response.json()
        except requests.exceptions.Timeout:
            return None, "Délai dépassé lors de la requête à OpenCage"
        except requests.exceptions.RequestException:
            return None, "Erreur réseau lors de la requête à OpenCage"

        results = body.get('results', [])
        if not results:
            return None, f"Adresse introuvable : '{location_text}'"

        geometry   = results[0]['geometry']
        components = results[0].get('components', {})

        city = (
            components.get('city')
            or components.get('town')
            or components.get('village')
            or components.get('municipality', '')
        )
        region = components.get('state') or components.get('county', '')

        return {
            'latitude':  geometry['lat'],
            'longitude': geometry['lng'],
            'city':      city,
            'region':    region,
        }, None

    def _upload_to_cloudinary(self, file, folder=None):
        options = {'resource_type': 'image'}
        if folder:
            options['folder'] = folder

        try:
            result = cloudinary.uploader.upload(file, **options)
        except cloudinary.exceptions.Error as exc:
            return None, f"Cloudinary : {str(exc)}"
        except Exception as exc:
            return None, f"Erreur lors de l'upload : {str(exc)}"

        url = result.get('secure_url')
        if not url:
            return None, "Cloudinary n'a pas retourné d'URL"

        return url, None

    def get_events(self, city=None, date=None, limit=50, offset=0, lat=None, lng=None, radius=10):
        events_list, total_count, error = self.events.get_open_events(
            city=city, date=date, limit=limit, offset=offset,
            lat=lat, lng=lng, radius=radius,
        )
        if error:
            return [], 0, error

        result = []
        for event in events_list:
            event_data = event.to_dict()
            if event.game_obj:
                event_data['game'] = event.game_obj.to_dict()
            result.append(event_data)
        return result, total_count, None

    def get_event(self, event_id):
        event = self.events.get_by_id(event_id)
        return event.to_dict() if event else None

    def get_event_details(self, event_id):
        event = self.events.get_by_id_full(event_id)
        if not event:
            return None

        event_data = event.to_dict(include_participants=True)
        if event.game_obj:
            event_data['game'] = event.game_obj.to_dict()
        if event.creator:
            event_data['creator'] = event.creator.to_public_dict()
        return event_data

    def create_event(self, data, creator_id, image_file=None):
        if not self.games.get_by_id(data['game_id']):
            return None, "Ce jeu n'existe pas"

        if isinstance(data['max_players'], bool) or not isinstance(data['max_players'], int) or data['max_players'] < 2:
            return None, "max_players doit être un entier supérieur ou égal à 2"

        if not data.get('title', '').strip():
            return None, "Le titre ne peut pas être vide"

        try:
            event_date_time = datetime.fromisoformat(data['date_time'])
        except (ValueError, TypeError):
            return None, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25T19:00:00)"

        now_utc = datetime.now(timezone.utc)
        if event_date_time.tzinfo:
            if event_date_time <= now_utc:
                return None, "La date de l'événement doit être dans le futur"
        else:
            if event_date_time <= now_utc.replace(tzinfo=None):
                return None, "La date de l'événement doit être dans le futur"

        geo, error = self._geocode(data['location_text'])
        if error:
            return None, error

        cover_url = None
        if image_file:
            cover_url, error = self._upload_to_cloudinary(image_file, folder='events')
            if error:
                return None, error

        event = Event(
            creator_id=creator_id,
            game_id=data['game_id'],
            title=data['title'],
            description=data.get('description', ''),
            city=geo['city'],
            region=geo['region'],
            location_text=data['location_text'],
            latitude=geo['latitude'],
            longitude=geo['longitude'],
            date_time=event_date_time,
            max_players=data['max_players'],
            cover_url=cover_url,
        )
        db.session.add(event)
        db.session.flush()

        creator_participation = EventParticipant(
            event_id=event.id,
            user_id=creator_id,
            status='confirmed',
        )
        db.session.add(creator_participation)

        db.session.commit()

        return event.to_dict(), None

    def update_event(self, event_id, user_id, data):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"

        if event.creator_id != user_id:
            return None, "forbidden"

        if event.status in ('cancelled', 'completed'):
            return None, "Impossible de modifier un événement annulé ou terminé"

        current_count = None
        if 'max_players' in data:
            if isinstance(data['max_players'], bool) or not isinstance(data['max_players'], int) or data['max_players'] < 2:
                return None, "max_players doit être un entier supérieur ou égal à 2"
            current_count = self.participants.count_confirmed(event_id)
            if data['max_players'] < current_count:
                return None, (
                    f"Impossible de réduire à {data['max_players']} : "
                    f"{current_count} participants sont déjà confirmés"
                )

        if 'location_text' in data and data['location_text'] != event.location_text:
            geo, error = self._geocode(data['location_text'])
            if error:
                return None, error
            event.location_text = data['location_text']
            event.city          = geo['city']
            event.region        = geo['region']
            event.latitude      = geo['latitude']
            event.longitude     = geo['longitude']

        if 'title' in data and not data['title'].strip():
            return None, "Le titre ne peut pas être vide"

        for field in ['title', 'description', 'max_players']:
            if field in data:
                setattr(event, field, data[field])

        if 'date_time' in data:
            try:
                new_dt = datetime.fromisoformat(data['date_time'])
            except (ValueError, TypeError):
                return None, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25T19:00:00)"

            now_utc = datetime.now(timezone.utc)
            if new_dt.tzinfo:
                if new_dt <= now_utc:
                    return None, "La date de l'événement doit être dans le futur"
            else:
                if new_dt <= now_utc.replace(tzinfo=None):
                    return None, "La date de l'événement doit être dans le futur"
            event.date_time = new_dt

        if current_count is not None:
            if current_count >= event.max_players:
                event.status = 'full'
            elif event.status == 'full':
                event.status = 'open'

        self.events.commit()
        return event.to_dict(), None

    def cancel_event(self, event_id, user_id):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"

        if event.creator_id != user_id:
            return None, "forbidden"

        if event.status in ('cancelled', 'completed'):
            return None, "Impossible d'annuler un événement annulé ou terminé"

        event.status = 'cancelled'
        self.events.commit()
        return event.to_dict(), None

    def join_event(self, event_id, user_id):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"

        if event.status != 'open':
            return None, "Cet événement n'accepte plus de participants"

        if event.creator_id == user_id:
            return None, "Le créateur ne peut pas rejoindre son propre événement"

        if self.participants.get_any(event_id, user_id):
            return None, "Vous participez déjà à cet événement"

        count = self.participants.count_confirmed(event_id)
        if count >= event.max_players:
            return None, "Événement complet"

        participation = EventParticipant(
            event_id=event_id,
            user_id=user_id,
            status='confirmed',
        )
        db.session.add(participation)
        if count + 1 >= event.max_players:
            event.status = 'full'
        self.events.commit()

        return participation.to_dict(), None

    def leave_event(self, event_id, user_id):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"

        if event.status in ('cancelled', 'completed'):
            return None, "Impossible de quitter un événement annulé ou terminé"

        if event.creator_id == user_id:
            return None, "Le créateur ne peut pas quitter son propre événement"

        participation = self.participants.get(event_id, user_id, status='confirmed')
        if not participation:
            return None, "Vous ne participez pas à cet événement"

        db.session.delete(participation)
        if event and event.status == 'full':
            event.status = 'open'
        db.session.commit()

        return {"success": True}, None

    def get_event_comments(self, event_id, limit=50, offset=0):
        return [c.to_dict() for c in self.comments.get_by_event(event_id, limit=limit, offset=offset)]

    def add_comment(self, event_id, user_id, content):
        comment = EventComment(
            event_id=event_id,
            user_id=user_id,
            content=content,
        )
        self.comments.save(comment)
        return comment.to_dict(), None

    # ── Search ────────────────────────────────────────────────────────────

    def global_search(self, query):
        found_users  = [u.to_public_dict() for u in self.users.search(query)]
        found_events = [e.to_dict() for e in self.events.search(query)]
        return {"users": found_users, "events": found_events}

    # ── Posts ──────────────────────────────────────────────────────────────

    def create_post(self, author_id, data, image_file=None):
        content = (data.get('content') or '').strip()
        post_type = data.get('post_type', 'text')

        if post_type not in ('text', 'image', 'news'):
            return None, "Type de post invalide (text, image, news)"

        image_url = None
        if image_file:
            image_url, err = self._upload_to_cloudinary(image_file)
            if err:
                return None, err
            if not post_type or post_type == 'text':
                post_type = 'image'

        if not content and not image_url:
            return None, "Le post doit contenir du texte ou une image"

        post = Post(
            author_id=author_id,
            post_type=post_type,
            content=content or None,
            image_url=image_url,
        )
        self.posts.save(post)
        return post.to_dict(), None

    def get_post(self, post_id):
        post = self.posts.get_by_id(post_id)
        if not post:
            return None, "Post introuvable"
        return post.to_dict(), None

    def update_post(self, current_user_id, post_id, data):
        post = self.posts.get_by_id(post_id)
        if not post:
            return None, "Post introuvable"
        if post.author_id != current_user_id:
            return None, "forbidden"

        content = data.get('content')
        if content is not None:
            content = content.strip()
            if not content and not post.image_url:
                return None, "Le post doit contenir du texte ou une image"
            post.content = content or None

        self.posts.commit()
        return post.to_dict(), None

    def delete_post(self, current_user_id, post_id):
        post = self.posts.get_by_id(post_id)
        if not post:
            return None, "Post introuvable"
        if post.author_id != current_user_id:
            return None, "forbidden"

        self.posts.delete(post)
        return {"success": True}, None

    def list_posts(self, limit=50, offset=0):
        posts, total = self.posts.get_all(limit=limit, offset=offset)
        return [p.to_dict() for p in posts], total

    def list_user_posts(self, user_id, limit=50, offset=0):
        posts, total = self.posts.get_by_author(user_id, limit=limit, offset=offset)
        return [p.to_dict() for p in posts], total

    # ── Friends ───────────────────────────────────────────────────────────

    def send_friend_request(self, requester_id, receiver_id):
        if requester_id == receiver_id:
            return None, "Impossible de s'ajouter soi-même en ami"

        if not self.users.get_by_id(receiver_id):
            return None, "Utilisateur introuvable"

        existing = self.friends.get_friendship(requester_id, receiver_id)
        if existing:
            if existing.status == 'accepted':
                return None, "Vous êtes déjà amis"
            return None, "Une demande d'ami est déjà en cours"

        u1, u2 = min(requester_id, receiver_id), max(requester_id, receiver_id)
        friendship = Friend(
            user_id_1=u1,
            user_id_2=u2,
            requester_id=requester_id,
        )
        self.friends.save(friendship)
        return friendship.to_dict(), None

    def accept_friend_request(self, current_user_id, requester_id):
        friendship = self.friends.get_friendship(current_user_id, requester_id)
        if not friendship:
            return None, "Aucune demande d'ami trouvée"

        if friendship.status == 'accepted':
            return None, "Vous êtes déjà amis"

        if friendship.requester_id == current_user_id:
            return None, "Vous ne pouvez pas accepter votre propre demande"

        friendship.status = 'accepted'
        self.friends.commit()
        return friendship.to_dict(), None

    def reject_friend_request(self, current_user_id, requester_id):
        friendship = self.friends.get_friendship(current_user_id, requester_id)
        if not friendship:
            return None, "Aucune demande d'ami trouvée"

        if friendship.status == 'accepted':
            return None, "Vous êtes déjà amis, utilisez supprimer"

        if friendship.requester_id == current_user_id:
            return None, "Vous ne pouvez pas refuser votre propre demande"

        self.friends.delete(friendship)
        return {"success": True}, None

    def remove_friend(self, current_user_id, other_user_id):
        friendship = self.friends.get_friendship(current_user_id, other_user_id)
        if not friendship:
            return None, "Aucune relation d'amitié trouvée"

        self.friends.delete(friendship)
        return {"success": True}, None

    def get_friends_list(self, user_id):
        friendships = self.friends.get_friends(user_id)
        result = []
        for f in friendships:
            friend_id = f.user_id_2 if f.user_id_1 == user_id else f.user_id_1
            user = self.users.get_by_id(friend_id)
            if user:
                result.append(user.to_public_dict())
        return result

    def get_pending_requests(self, user_id):
        received = self.friends.get_pending_received(user_id)
        result = []
        for f in received:
            user = self.users.get_by_id(f.requester_id)
            if user:
                entry = user.to_public_dict()
                entry['friendship_id'] = f.id
                entry['requested_at'] = f.created_at.isoformat() if f.created_at else None
                result.append(entry)
        return result

    def get_sent_requests(self, user_id):
        sent = self.friends.get_pending_sent(user_id)
        result = []
        for f in sent:
            other_id = f.user_id_2 if f.user_id_1 == user_id else f.user_id_1
            user = self.users.get_by_id(other_id)
            if user:
                entry = user.to_public_dict()
                entry['friendship_id'] = f.id
                entry['requested_at'] = f.created_at.isoformat() if f.created_at else None
                result.append(entry)
        return result
