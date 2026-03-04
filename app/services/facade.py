from datetime import datetime
import os
import re
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import (
    User, Profile, Game, Event, EventParticipant,
    EventComment, Friend, FavoriteGame, Post, Review
)
from app.persistence.repository import (
    UserRepository, ProfileRepository, GameRepository, EventRepository,
    EventParticipantRepository, EventCommentRepository,
    FriendRepository, FavoriteGameRepository,
    PostRepository, ReviewRepository,
)


class BoardGameFacade:
    """
    Couche métier centrale. Toutes les routes API passent par ici.
    """

    def __init__(self):
        self.users        = UserRepository()
        self.profiles     = ProfileRepository()
        self.games        = GameRepository()
        self.events       = EventRepository()
        self.participants = EventParticipantRepository()
        self.comments     = EventCommentRepository()
        self.friends      = FriendRepository()
        self.favorites    = FavoriteGameRepository()
        self.posts        = PostRepository()
        self.reviews      = ReviewRepository()

    # ==========================================
    # GÉOCODAGE (interne)
    # ==========================================

    def _geocode(self, location_text):
        """Appelle OpenCage Geocoding API pour obtenir lat, lng, city et region.
        Retourne (dict, None) en succès ou (None, "message d'erreur") en échec.
        """
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

    # ==========================================
    # AUTH
    # ==========================================

    def register_user(self, data):
        for field in ['username', 'email', 'password', 'city']:
            if not data.get(field):
                return None, f"Le champ '{field}' est requis"

        if len(data['password']) < 8:
            return None, "Le mot de passe doit contenir au minimum 8 caractères"

        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', data['email']):
            return None, "Format d'email invalide"

        if self.users.get_by_email(data['email']):
            return None, "Cet email est déjà utilisé"

        if self.profiles.get_by_username(data['username']):
            return None, "Ce nom d'utilisateur est déjà pris"

        # Création du compte d'authentification
        user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role='user',
        )
        db.session.add(user)
        db.session.flush()  # récupère user.id sans commit

        # Création du profil public associé
        profile = Profile(
            user_id=user.id,
            username=data['username'],
            bio=data.get('bio', ''),
            city=data['city'],
            region=data.get('region', ''),
        )
        db.session.add(profile)
        db.session.commit()

        # Rattacher le profil pour que to_dict() fonctionne
        user.profile = profile
        return user.to_dict(), None

    def login_user(self, email, password):
        user = self.users.get_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            return user.to_dict(), None
        return None, "Email ou mot de passe incorrect"

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

    def get_public_user(self, user_id):
        """Vue publique sans email ni rôle — utilisée pour GET /users/<id>."""
        user = self.users.get_by_id(user_id)
        if not user:
            return None
        user_data = user.to_public_dict()
        user_data['favorite_games'] = self.get_favorite_games(user_id)
        return user_data

    def update_user_profile(self, user_id, data):
        user = self.users.get_by_id(user_id)
        if not user:
            return None, "Utilisateur introuvable"

        profile = self.profiles.get_by_user_id(user_id)
        if not profile:
            return None, "Profil introuvable"

        if 'username' in data and data['username'] != profile.username:
            if self.profiles.get_by_username(data['username']):
                return None, "Ce nom d'utilisateur est déjà pris"

        for field in ['username', 'bio', 'city', 'region', 'profile_image_url']:
            if field in data:
                setattr(profile, field, data[field])

        self.profiles.commit()
        user.profile = profile
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

        # Déduplication par id INT
        all_events = {e.id: e for e in created + joined}
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
            if event.game_obj:
                event_data['game'] = event.game_obj.to_dict()
            result.append(event_data)
        return result, None

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
            event_data['creator'] = event.creator.to_dict()
        return event_data

    def create_event(self, data, creator_id):
        if not self.games.get_by_id(data['game_id']):
            return None, "Ce jeu n'existe pas"

        try:
            event_date_time = datetime.fromisoformat(data['date_time'])
        except (ValueError, TypeError):
            return None, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25T19:00:00)"

        if event_date_time <= datetime.utcnow():
            return None, "La date de l'événement doit être dans le futur"

        geo, error = self._geocode(data['location_text'])
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
            cover_url=data.get('cover_url'),
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

        # Si l'adresse change → re-géocoder pour mettre à jour lat/lng, city, region
        if 'location_text' in data and data['location_text'] != event.location_text:
            geo, error = self._geocode(data['location_text'])
            if error:
                return None, error
            event.location_text = data['location_text']
            event.city          = geo['city']
            event.region        = geo['region']
            event.latitude      = geo['latitude']
            event.longitude     = geo['longitude']

        for field in ['title', 'description', 'max_players', 'cover_url']:
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

        if event.status != 'open':
            return None, "Cet événement n'accepte plus de participants"

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
        participation = self.participants.get(event_id, user_id, status='confirmed')
        if not participation:
            return None, "Vous ne participez pas à cet événement"

        event = self.events.get_by_id(event_id)

        db.session.delete(participation)
        if event and event.status == 'full':
            event.status = 'open'
        db.session.commit()

        return {"success": True}, None

    # ==========================================
    # COMMENTAIRES D'ÉVÉNEMENTS
    # ==========================================

    def get_event_comments(self, event_id):
        comments = self.comments.get_by_event(event_id)
        result = []
        for comment in comments:
            comment_data = comment.to_dict()
            if comment.author and comment.author.profile:
                comment_data['username'] = comment.author.profile.username
            result.append(comment_data)
        return result

    def add_comment(self, event_id, user_id, content):
        comment = EventComment(
            event_id=event_id,
            user_id=user_id,
            content=content,
        )
        self.comments.save(comment)
        comment_data = comment.to_dict()
        if comment.author and comment.author.profile:
            comment_data['username'] = comment.author.profile.username
        return comment_data, None

    # ==========================================
    # AMIS
    # ==========================================

    def get_friends(self, user_id):
        friendships = self.friends.get_accepted(user_id)
        result = []
        for f in friendships:
            friend = f.user2 if f.user_id_1 == user_id else f.user1
            if friend:
                result.append(friend.to_dict())
        return result

    def get_pending_requests(self, user_id):
        pending = self.friends.get_pending_received(user_id)
        result = []
        for f in pending:
            requester = f.requester
            if requester:
                result.append({
                    "friendship": f.to_dict(),
                    "requester":  requester.to_dict(),
                })
        return result

    def add_friend(self, requester_id, receiver_id):
        if requester_id == receiver_id:
            return None, "Vous ne pouvez pas vous ajouter vous-même"

        if not self.users.get_by_id(receiver_id):
            return None, "Utilisateur introuvable"

        user_id_1, user_id_2 = sorted([requester_id, receiver_id])

        if self.friends.get(user_id_1, user_id_2):
            return None, "Une demande existe déjà entre vous"

        friendship = Friend(
            user_id_1=user_id_1,
            user_id_2=user_id_2,
            requester_id=requester_id,
            status='pending',
        )
        self.friends.save(friendship)
        return friendship.to_dict(), None

    def accept_friend(self, current_user_id, requester_id):
        user_id_1, user_id_2 = sorted([current_user_id, requester_id])
        friendship = self.friends.get_with_status(user_id_1, user_id_2, 'pending')

        if not friendship:
            return None, "Demande introuvable"

        friendship.status = 'accepted'
        self.friends.commit()
        return friendship.to_dict(), None

    def decline_friend(self, current_user_id, requester_id):
        user_id_1, user_id_2 = sorted([current_user_id, requester_id])
        friendship = self.friends.get_with_status(user_id_1, user_id_2, 'pending')

        if not friendship:
            return None, "Demande introuvable"

        self.friends.delete(friendship)
        return {"success": True}, None

    def remove_friend(self, current_user_id, friend_id):
        user_id_1, user_id_2 = sorted([current_user_id, friend_id])
        friendship = self.friends.get_with_status(user_id_1, user_id_2, 'accepted')

        if not friendship:
            return None, "Cet utilisateur n'est pas dans vos amis"

        self.friends.delete(friendship)
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
    # PUBLICATIONS
    # ==========================================

    def create_post(self, author_id, content):
        if not content or not content.strip():
            return None, "Le contenu ne peut pas être vide"

        post = Post(author_id=author_id, content=content.strip())
        self.posts.save(post)
        return post.to_dict(), None

    def delete_post(self, post_id, user_id):
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            return None, "Publication introuvable"

        if post.author_id != user_id:
            return None, "Vous ne pouvez supprimer que vos propres publications"

        self.posts.delete(post)
        return {"success": True}, None

    # ==========================================
    # AVIS
    # ==========================================

    def create_review(self, reviewer_id, data):
        rating = data.get('rating')
        event_id = data.get('event_id')
        reviewed_user_id = data.get('reviewed_user_id')

        if rating is None:
            return None, "Le champ 'rating' est requis"

        if not isinstance(rating, int) or not (1 <= rating <= 5):
            return None, "La note doit être un entier entre 1 et 5"

        # Exactement une cible doit être fournie
        if event_id and reviewed_user_id:
            return None, "Un avis ne peut cibler qu'un événement OU un joueur, pas les deux"

        if not event_id and not reviewed_user_id:
            return None, "Un avis doit cibler un événement (event_id) ou un joueur (reviewed_user_id)"

        if event_id:
            if not self.events.get_by_id(event_id):
                return None, "Événement introuvable"

        if reviewed_user_id:
            if reviewed_user_id == reviewer_id:
                return None, "Vous ne pouvez pas vous noter vous-même"
            if not self.users.get_by_id(reviewed_user_id):
                return None, "Utilisateur introuvable"

        review = Review(
            reviewer_id=reviewer_id,
            event_id=event_id,
            reviewed_user_id=reviewed_user_id,
            rating=rating,
            comment=data.get('comment', ''),
        )
        self.reviews.save(review)
        return review.to_dict(), None

    def get_reviews_by_user(self, user_id):
        if not self.users.get_by_id(user_id):
            return None, "Utilisateur introuvable"

        reviews = self.reviews.get_by_reviewed_user(user_id)
        return [r.to_dict() for r in reviews], None

    def get_reviews_by_event(self, event_id):
        if not self.events.get_by_id(event_id):
            return None, "Événement introuvable"

        reviews = self.reviews.get_by_event(event_id)
        return [r.to_dict() for r in reviews], None

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

    def get_game_by_api_id(self, id_api):
        game = self.games.get_by_api_id(id_api)
        return game.to_dict() if game else None

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
        if data['min_players'] < 1 or data['max_players'] < 1:
            return None, "min_players et max_players doivent être supérieurs ou égaux à 1"

        if data['min_players'] > data['max_players']:
            return None, "min_players ne peut pas dépasser max_players"

        game = Game(
            id_api=data['id_api'],
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

        for field in ['name', 'description', 'min_players', 'max_players',
                      'play_time_minutes', 'image_url', 'id_api']:
            if field in data:
                setattr(game, field, data[field])

        self.games.commit()
        return game.to_dict(), None

    def get_events_by_game(self, game_id):
        return [e.to_dict() for e in self.events.get_by_game(game_id)]
