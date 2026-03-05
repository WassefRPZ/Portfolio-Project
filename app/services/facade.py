from datetime import datetime, timezone
import os
import re
import requests
import cloudinary.uploader
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import (
    User, Profile, Game, Event, EventParticipant,
    EventComment, Friend, FavoriteGame, Post, PostLike, PostComment, Review
)
from app.persistence.repository import (
    UserRepository, ProfileRepository, GameRepository, EventRepository,
    EventParticipantRepository, EventCommentRepository,
    FriendRepository, FavoriteGameRepository,
    PostRepository, PostLikeRepository, PostCommentRepository, ReviewRepository,
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
        self.post_likes   = PostLikeRepository()
        self.post_comments = PostCommentRepository()
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
    # CLOUDINARY (interne)
    # ==========================================

    def _upload_to_cloudinary(self, file, folder=None):
        """Envoie un fichier image vers Cloudinary et retourne l'URL sécurisée.
        Retourne (url, None) en succès ou (None, "message d'erreur") en échec.
        """
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

    # ==========================================
    # AUTH
    # ==========================================

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

    def update_user_profile(self, user_id, data, image_file=None):
        user = self.users.get_by_id(user_id)
        if not user:
            return None, "Utilisateur introuvable"

        profile = self.profiles.get_by_user_id(user_id)
        if not profile:
            return None, "Profil introuvable"

        if 'username' in data and data['username'] != profile.username:
            if self.profiles.get_by_username(data['username']):
                return None, "Ce nom d'utilisateur est déjà pris"

        # Upload image de profil si fournie
        if image_file:
            url, error = self._upload_to_cloudinary(image_file, folder='profiles')
            if error:
                return None, error
            data['profile_image_url'] = url

        for field in ['username', 'bio', 'city', 'region', 'profile_image_url']:
            if field in data:
                setattr(profile, field, data[field])

        self.profiles.commit()
        user.profile = profile
        return user.to_dict(), None

    def search_users(self, query, city=None):
        return [u.to_public_dict() for u in self.users.search(query, city)]

    def global_search(self, query):
        """Recherche simultanée dans les utilisateurs (username) et les événements ouverts (title/description)."""
        users  = [u.to_public_dict() for u in self.users.search(query)]
        events = [e.to_dict() for e in self.events.search(query)]
        return {"users": users, "events": events}

    def get_user_events(self, user_id, limit=50, offset=0):
        # Événements créés
        created = self.events.get_by_creator(user_id)

        # Événements rejoints
        participations = self.participants.get_confirmed_by_user(user_id)
        joined_ids = [p.event_id for p in participations]
        joined = self.events.get_by_ids(joined_ids)

        # Déduplication par id INT
        all_events = {e.id: e for e in created + joined}
        events_list = sorted(all_events.values(), key=lambda e: e.date_time or e.created_at, reverse=True)
        return [e.to_dict() for e in events_list[offset:offset + limit]]

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

    def create_event(self, data, creator_id, image_file=None):
        if not self.games.get_by_id(data['game_id']):
            return None, "Ce jeu n'existe pas"

        try:
            event_date_time = datetime.fromisoformat(data['date_time'])
        except (ValueError, TypeError):
            return None, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25T19:00:00)"

        if event_date_time <= datetime.now(timezone.utc).replace(tzinfo=None):
            return None, "La date de l'événement doit être dans le futur"

        geo, error = self._geocode(data['location_text'])
        if error:
            return None, error

        # Upload image de couverture si fournie
        cover_url = data.get('cover_url')
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

        # Le créateur est automatiquement participant
        creator_participation = EventParticipant(
            event_id=event.id,
            user_id=creator_id,
            status='confirmed',
        )
        db.session.add(creator_participation)
        db.session.commit()

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

    def get_event_comments(self, event_id, limit=50, offset=0):
        comments = self.comments.get_by_event(event_id, limit=limit, offset=offset)
        return [comment.to_dict() for comment in comments]

    def add_comment(self, event_id, user_id, content):
        comment = EventComment(
            event_id=event_id,
            user_id=user_id,
            content=content,
        )
        self.comments.save(comment)
        return comment.to_dict(), None

    # ==========================================
    # AMIS
    # ==========================================

    def get_friends(self, user_id):
        friendships = self.friends.get_accepted(user_id)
        result = []
        for f in friendships:
            friend = f.user2 if f.user_id_1 == user_id else f.user1
            if friend:
                result.append(friend.to_public_dict())
        return result

    def get_pending_requests(self, user_id):
        pending = self.friends.get_pending_received(user_id)
        result = []
        for f in pending:
            requester = f.requester
            if requester:
                result.append({
                    "friendship": f.to_dict(),
                    "requester":  requester.to_public_dict(),
                })
        return result

    def get_sent_requests(self, user_id):
        """Demandes envoyées par user_id encore en attente."""
        sent = self.friends.get_pending_sent(user_id)
        result = []
        for f in sent:
            receiver = f.user2 if f.user_id_1 == user_id else f.user1
            if receiver:
                result.append({
                    "friendship": f.to_dict(),
                    "receiver":   receiver.to_public_dict(),
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
        if current_user_id == requester_id:
            return None, "Vous ne pouvez pas accepter votre propre demande"

        user_id_1, user_id_2 = sorted([current_user_id, requester_id])
        friendship = self.friends.get_with_status(user_id_1, user_id_2, 'pending')

        if not friendship:
            return None, "Demande introuvable"

        if friendship.requester_id == current_user_id:
            return None, "Vous ne pouvez pas accepter votre propre demande"

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

    # ==========================================
    # PUBLICATIONS
    # ==========================================

    def create_post(self, author_id, content=None, image_file=None, post_type='text'):
        VALID_TYPES = ('text', 'image', 'news')
        if post_type not in VALID_TYPES:
            return None, f"Type de post invalide. Valeurs acceptées : {', '.join(VALID_TYPES)}"

        image_url = None
        if image_file:
            image_url, error = self._upload_to_cloudinary(image_file, folder='posts')
            if error:
                return None, error

        content = content.strip() if content else None

        if not content and not image_url:
            return None, "Un post doit contenir au moins un texte ou une image"

        post = Post(
            author_id=author_id,
            post_type=post_type,
            content=content,
            image_url=image_url,
        )
        self.posts.save(post)
        return post.to_dict(), None

    def get_feed(self, limit=20, offset=0, current_user_id=None):
        posts = self.posts.get_recent(limit=limit, offset=offset)
        return [p.to_dict(liked_by_user_id=current_user_id) for p in posts]

    def like_post(self, user_id, post_id):
        post = self.posts.get_by_id(post_id)
        if not post:
            return None, "Post introuvable"
        if self.post_likes.get(user_id, post_id):
            return None, "Vous avez déjà liké ce post"
        like = PostLike(user_id=user_id, post_id=post_id)
        self.post_likes.save(like)
        return {"likes_count": post.likes.count()}, None

    def unlike_post(self, user_id, post_id):
        like = self.post_likes.get(user_id, post_id)
        if not like:
            return None, "Vous n'avez pas liké ce post"
        self.post_likes.delete(like)
        post = self.posts.get_by_id(post_id)
        return {"likes_count": post.likes.count()}, None

    def add_post_comment(self, user_id, post_id, content):
        if not content or not content.strip():
            return None, "Le commentaire ne peut pas être vide"
        if not self.posts.get_by_id(post_id):
            return None, "Post introuvable"
        comment = PostComment(
            post_id=post_id,
            user_id=user_id,
            content=content.strip(),
        )
        self.post_comments.save(comment)
        return comment.to_dict(), None

    def get_post_comments(self, post_id):
        if not self.posts.get_by_id(post_id):
            return None, "Post introuvable"
        return [c.to_dict() for c in self.post_comments.get_by_post(post_id)], None

    def delete_post_comment(self, comment_id, user_id):
        comment = self.post_comments.get_by_id(comment_id)
        if not comment:
            return None, "Commentaire introuvable"
        if comment.user_id != user_id:
            return None, "Vous ne pouvez supprimer que vos propres commentaires"
        self.post_comments.delete(comment)
        return {"success": True}, None

    def kick_participant(self, event_id, user_id_to_kick):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"

        participation = self.participants.get_any(event_id, user_id_to_kick)
        if not participation:
            return None, "Ce joueur ne participe pas à cet événement"

        db.session.delete(participation)
        if event.status == 'full':
            event.status = 'open'
        db.session.commit()
        return {"success": True}, None

    def close_event(self, event_id):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"
        if event.status == 'cancelled':
            return None, "Impossible de fermer un événement annulé"
        if event.status == 'completed':
            return None, "Cet événement est déjà terminé"

        event.status = 'completed'
        self.events.commit()
        return event.to_dict(), None

    def open_event(self, event_id):
        event = self.events.get_by_id(event_id)
        if not event:
            return None, "Événement introuvable"
        if event.status == 'cancelled':
            return None, "Impossible de rouvrir un événement annulé"
        if event.status == 'open':
            return None, "Cet événement est déjà ouvert"

        event.status = 'open'
        self.events.commit()
        return event.to_dict(), None

    def delete_post(self, post_id, user_id):
        post = self.posts.get_by_id(post_id)
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
            if self.reviews.get_by_reviewer_and_event(reviewer_id, event_id):
                return None, "Vous avez déjà noté cet événement"

        if reviewed_user_id:
            if reviewed_user_id == reviewer_id:
                return None, "Vous ne pouvez pas vous noter vous-même"
            if not self.users.get_by_id(reviewed_user_id):
                return None, "Utilisateur introuvable"
            if self.reviews.get_by_reviewer_and_user(reviewer_id, reviewed_user_id):
                return None, "Vous avez déjà noté ce joueur"

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

    def delete_review(self, review_id, user_id):
        review = self.reviews.get_by_id(review_id)
        if not review:
            return None, "Avis introuvable"
        if review.reviewer_id != user_id:
            return None, "Vous ne pouvez supprimer que vos propres avis"
        self.reviews.delete(review)
        return {"success": True}, None

    # ==========================================
    # JEUX
    # ==========================================

    def get_all_games(self):
        return [g.to_dict() for g in self.games.get_all_ordered()]

    def get_game(self, game_id):
        game = self.games.get_by_id(game_id)
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
        for field in ['name', 'min_players', 'max_players', 'play_time_minutes']:
            if data.get(field) is None:
                return None, f"Le champ '{field}' est requis"

        if self.games.get_by_name(data['name']):
            return None, "Un jeu avec ce nom existe déjà"

        game = Game(
            name=data['name'],
            description=data.get('description', ''),
            min_players=int(data['min_players']),
            max_players=int(data['max_players']),
            play_time_minutes=int(data['play_time_minutes']),
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
                      'play_time_minutes', 'image_url']:
            if field in data:
                setattr(game, field, data[field])

        self.games.commit()
        return game.to_dict(), None

    def get_events_by_game(self, game_id):
        return [e.to_dict() for e in self.events.get_by_game(game_id)]
