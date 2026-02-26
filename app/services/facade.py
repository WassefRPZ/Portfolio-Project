import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Event, Game, EventParticipant, Comment, Friendship, FavoriteGame


class BoardGameFacade:

    # ==========================================
    # AUTH
    # ==========================================

    def register_user(self, data):
        # Vérifier les champs obligatoires
        for field in ['username', 'email', 'password', 'city']:
            if not data.get(field):
                return None, f"Le champ '{field}' est requis"

        # Vérifier que l'email n'est pas déjà pris
        if User.query.filter_by(email=data['email']).first():
            return None, "Cet email est déjà utilisé"

        # Vérifier que le username n'est pas déjà pris
        if User.query.filter_by(username=data['username']).first():
            return None, "Ce nom d'utilisateur est déjà pris"

        # Créer l'utilisateur
        user = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            city=data['city'],
            region=data.get('region', ''),
            bio=data.get('bio', '')
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), None

    def login_user(self, email, password):
        user = User.query.filter_by(email=email).first()

        # Vérifier que l'utilisateur existe et que le mot de passe est correct
        if user and check_password_hash(user.password_hash, password):
            return user.to_dict()
        return None

    # ==========================================
    # UTILISATEURS
    # ==========================================

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def get_user(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return None

        # Récupérer ses jeux favoris en même temps
        user_data = user.to_dict()
        favorites = FavoriteGame.query.filter_by(user_id=user_id).all()
        user_data['favorite_games'] = []
        for fav in favorites:
            game = Game.query.filter_by(game_id=fav.game_id).first()
            if game:
                user_data['favorite_games'].append(game.to_dict())

        return user_data

    def update_user_profile(self, user_id, data):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return None

        # On met à jour seulement les champs autorisés
        for field in ['username', 'city', 'region', 'bio', 'profile_image_url']:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()
        return user.to_dict()

    def search_users(self, query, city=None):
        # On cherche dans le username
        results = User.query
        if query:
            results = results.filter(User.username.like(f'%{query}%'))
        if city:
            results = results.filter_by(city=city)

        return [u.to_dict() for u in results.limit(20).all()]

    def get_user_events(self, user_id):
        # Événements créés par l'utilisateur
        created = Event.query.filter_by(creator_id=user_id).all()

        # Événements rejoints par l'utilisateur
        participations = EventParticipant.query.filter_by(user_id=user_id).all()
        joined_ids = [p.event_id for p in participations]
        joined = Event.query.filter(Event.event_id.in_(joined_ids)).all() if joined_ids else []

        # On combine les deux sans doublons
        all_events = {e.event_id: e for e in created + joined}
        return [e.to_dict() for e in all_events.values()]

    # ==========================================
    # ÉVÉNEMENTS
    # ==========================================

    def get_events(self, city=None, date=None):
        events = Event.query.filter_by(status='open')

        if city:
            events = events.filter_by(city=city)
        if date:
            target = datetime.fromisoformat(date)
            events = events.filter(
                db.func.date(Event.event_start) == target.date()
            )

        events = events.order_by(Event.event_start).limit(50).all()

        # On ajoute les infos du jeu pour chaque event
        result = []
        for event in events:
            event_data = event.to_dict()
            game = Game.query.filter_by(game_id=event.game_id).first()
            if game:
                event_data['game'] = game.to_dict()
            result.append(event_data)

        return result

    def get_event_details(self, event_id):
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            return None

        # Détails complets avec participants, jeu et créateur
        event_data = event.to_dict(include_participants=True)

        game = Game.query.filter_by(game_id=event.game_id).first()
        if game:
            event_data['game'] = game.to_dict()

        creator = User.query.filter_by(user_id=event.creator_id).first()
        if creator:
            event_data['creator'] = creator.to_dict()

        return event_data

    def create_event(self, data, creator_id):
        # Vérifier que le jeu existe
        game = Game.query.filter_by(game_id=data['game_id']).first()
        if not game:
            return {"error": "Ce jeu n'existe pas"}

        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            creator_id=creator_id,
            game_id=data['game_id'],
            title=data['title'],
            description=data.get('description', ''),
            city=data['city'],
            location_text=data['location_text'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            event_start=datetime.fromisoformat(data['event_start']),
            max_participants=data['max_participants']
        )
        db.session.add(event)
        db.session.commit()
        return event.to_dict()

    def update_event(self, event_id, data):
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            return None

        for field in ['title', 'description', 'city', 'location_text', 'max_participants']:
            if field in data:
                setattr(event, field, data[field])

        # event_start a besoin d'une conversion
        if 'event_start' in data:
            event.event_start = datetime.fromisoformat(data['event_start'])

        db.session.commit()
        return event.to_dict()

    def cancel_event(self, event_id, user_id):
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            return None, "Événement introuvable"

        if event.creator_id != user_id:
            return None, "Vous n'êtes pas le créateur"

        event.status = 'cancelled'
        db.session.commit()
        return event.to_dict(), None

    def join_event(self, event_id, user_id):
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            return None, "Événement introuvable"

        # Vérifier que l'utilisateur ne participe pas déjà
        already_in = EventParticipant.query.filter_by(
            event_id=event_id, user_id=user_id
        ).first()
        if already_in:
            return None, "Vous participez déjà à cet événement"

        # Vérifier qu'il reste de la place
        count = EventParticipant.query.filter_by(event_id=event_id).count()
        if count >= event.max_participants:
            return None, "Événement complet"

        participation = EventParticipant(
            participant_id=f"prt_{uuid.uuid4().hex[:8]}",
            event_id=event_id,
            user_id=user_id,
            status='confirmed'
        )
        db.session.add(participation)

        # Si c'est le dernier spot, on passe l'event en "full"
        if count + 1 >= event.max_participants:
            event.status = 'full'

        db.session.commit()
        return participation.to_dict(), None

    def leave_event(self, event_id, user_id):
        participation = EventParticipant.query.filter_by(
            event_id=event_id, user_id=user_id
        ).first()
        if not participation:
            return None, "Vous ne participez pas à cet événement"

        db.session.delete(participation)

        # Si l'event était full, on le remet en open
        event = Event.query.filter_by(event_id=event_id).first()
        if event and event.status == 'full':
            event.status = 'open'

        db.session.commit()
        return {"success": True}, None

    # ==========================================
    # COMMENTAIRES
    # ==========================================

    def get_event_comments(self, event_id):
        comments = Comment.query.filter_by(event_id=event_id)\
                                .order_by(Comment.created_at).all()
        result = []
        for comment in comments:
            comment_data = comment.to_dict()
            # Ajouter le username de l'auteur
            author = User.query.filter_by(user_id=comment.user_id).first()
            if author:
                comment_data['username'] = author.username
            result.append(comment_data)
        return result

    def add_comment(self, event_id, user_id, content):
        comment = Comment(
            comment_id=f"cmt_{uuid.uuid4().hex[:8]}",
            event_id=event_id,
            user_id=user_id,
            content=content
        )
        db.session.add(comment)
        db.session.commit()

        comment_data = comment.to_dict()
        author = User.query.filter_by(user_id=user_id).first()
        if author:
            comment_data['username'] = author.username
        return comment_data, None

    # ==========================================
    # AMIS
    # ==========================================

    def get_friends(self, user_id):
        # Récupérer toutes les amitiés acceptées
        friendships = Friendship.query.filter(
            Friendship.status == 'accepted'
        ).filter(
            (Friendship.user_id_1 == user_id) | (Friendship.user_id_2 == user_id)
        ).all()

        friends = []
        for f in friendships:
            # L'ami c'est l'autre personne
            friend_id = f.user_id_2 if f.user_id_1 == user_id else f.user_id_1
            friend = User.query.filter_by(user_id=friend_id).first()
            if friend:
                friends.append(friend.to_dict())
        return friends

    def get_pending_requests(self, user_id):
        # Demandes reçues en attente (l'autre a envoyé, pas moi)
        pending = Friendship.query.filter(
            Friendship.status == 'pending',
            Friendship.action_user_id != user_id
        ).filter(
            (Friendship.user_id_1 == user_id) | (Friendship.user_id_2 == user_id)
        ).all()

        result = []
        for f in pending:
            requester = User.query.filter_by(user_id=f.action_user_id).first()
            if requester:
                result.append({
                    "friendship": f.to_dict(),
                    "requester": requester.to_dict()
                })
        return result

    def add_friend(self, requester_id, receiver_id):
        if requester_id == receiver_id:
            return None, "Vous ne pouvez pas vous ajouter vous-même"

        # Vérifier que le destinataire existe
        if not User.query.filter_by(user_id=receiver_id).first():
            return None, "Utilisateur introuvable"

        # Ordre alphabétique pour éviter les doublons A-B et B-A
        user_id_1, user_id_2 = sorted([requester_id, receiver_id])

        if Friendship.query.filter_by(user_id_1=user_id_1, user_id_2=user_id_2).first():
            return None, "Une demande existe déjà"

        friendship = Friendship(
            user_id_1=user_id_1,
            user_id_2=user_id_2,
            action_user_id=requester_id,
            status='pending'
        )
        db.session.add(friendship)
        db.session.commit()
        return friendship.to_dict(), None

    def accept_friend(self, current_user_id, requester_id):
        user_id_1, user_id_2 = sorted([current_user_id, requester_id])

        friendship = Friendship.query.filter_by(
            user_id_1=user_id_1, user_id_2=user_id_2, status='pending'
        ).first()

        if not friendship:
            return None, "Demande introuvable"

        if friendship.action_user_id == current_user_id:
            return None, "Vous ne pouvez pas accepter votre propre demande"

        friendship.status = 'accepted'
        db.session.commit()
        return friendship.to_dict(), None

    def decline_friend(self, current_user_id, requester_id):
        user_id_1, user_id_2 = sorted([current_user_id, requester_id])

        friendship = Friendship.query.filter_by(
            user_id_1=user_id_1, user_id_2=user_id_2, status='pending'
        ).first()

        if not friendship:
            return None, "Demande introuvable"

        if friendship.action_user_id == current_user_id:
            return None, "Vous ne pouvez pas refuser votre propre demande"

        friendship.status = 'declined'
        db.session.commit()
        return friendship.to_dict(), None

    def remove_friend(self, current_user_id, friend_id):
        user_id_1, user_id_2 = sorted([current_user_id, friend_id])

        friendship = Friendship.query.filter_by(
            user_id_1=user_id_1, user_id_2=user_id_2, status='accepted'
        ).first()

        if not friendship:
            return None, "Cet utilisateur n'est pas dans vos amis"

        db.session.delete(friendship)
        db.session.commit()
        return {"success": True}, None

    # ==========================================
    # JEUX FAVORIS
    # ==========================================

    def get_favorite_games(self, user_id):
        favorites = FavoriteGame.query.filter_by(user_id=user_id).all()
        result = []
        for fav in favorites:
            game = Game.query.filter_by(game_id=fav.game_id).first()
            if game:
                result.append(game.to_dict())
        return result

    def add_favorite_game(self, user_id, game_id):
        if not Game.query.filter_by(game_id=game_id).first():
            return None, "Jeu introuvable"

        if FavoriteGame.query.filter_by(user_id=user_id, game_id=game_id).first():
            return None, "Jeu déjà dans vos favoris"

        favorite = FavoriteGame(user_id=user_id, game_id=game_id)
        db.session.add(favorite)
        db.session.commit()
        return favorite.to_dict(), None

    def remove_favorite_game(self, user_id, game_id):
        favorite = FavoriteGame.query.filter_by(
            user_id=user_id, game_id=game_id
        ).first()

        if not favorite:
            return None, "Ce jeu n'est pas dans vos favoris"

        db.session.delete(favorite)
        db.session.commit()
        return {"success": True}, None

    # ==========================================
    # JEUX
    # ==========================================

    def get_all_games(self):
        games = Game.query.order_by(Game.name).all()
        return [g.to_dict() for g in games]

    def get_game(self, game_id):
        game = Game.query.filter_by(game_id=game_id).first()
        return game.to_dict() if game else None

    def get_game_by_name(self, name):
        return Game.query.filter_by(name=name).first()

    def search_games(self, query):
        games = Game.query.filter(Game.name.like(f'%{query}%')).limit(10).all()
        return [g.to_dict() for g in games]

    def get_popular_games(self):
        # Les jeux les plus utilisés dans les événements
        from sqlalchemy import func
        results = db.session.query(
            Game, func.count(Event.event_id).label('total')
        ).join(Event, Game.game_id == Event.game_id)\
         .group_by(Game.game_id)\
         .order_by(func.count(Event.event_id).desc())\
         .limit(10).all()

        popular = []
        for game, total in results:
            game_data = game.to_dict()
            game_data['event_count'] = total
            popular.append(game_data)
        return popular

    def create_game(self, data):
        game = Game(
            game_id=f"game_{uuid.uuid4().hex[:8]}",
            name=data['name'],
            description=data.get('description', ''),
            min_players=data['min_players'],
            max_players=data['max_players'],
            play_time=data['play_time'],
            image_url=data.get('image_url', '')
        )
        db.session.add(game)
        db.session.commit()
        return game.to_dict()

    def update_game(self, game_id, data):
        game = Game.query.filter_by(game_id=game_id).first()
        if not game:
            return None

        for field in ['name', 'description', 'min_players', 'max_players', 'play_time', 'image_url']:
            if field in data:
                setattr(game, field, data[field])

        db.session.commit()
        return game.to_dict()

    def get_events_by_game(self, game_id):
        events = Event.query.filter_by(game_id=game_id, status='open')\
                            .order_by(Event.event_start).all()
        return [e.to_dict() for e in events]
