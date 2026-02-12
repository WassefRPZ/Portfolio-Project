"""
============================================
Board Game Meetup - Facade Pattern
============================================
Façade centrale qui coordonne tous les services
"""
import uuid
import bcrypt
from datetime import datetime
from app import db
from app.models import User, Event, Game, EventParticipant, Comment, Friendship, FavoriteGame, Review, Notification
from sqlalchemy import or_, and_

class BoardGameFacade:
    """
    Façade principale qui expose toutes les opérations métier
    du système de rencontres de jeux de société
    """
    
    # ==========================================
    # AUTHENTIFICATION
    # ==========================================
    
    def register_user(self, data):
        """
        Créer un nouveau compte utilisateur
        """
        try:
            # Validation basique
            required_fields = ['username', 'email', 'password', 'city']
            for field in required_fields:
                if field not in data or not data[field]:
                    return None, f"Le champ {field} est requis"
            
            # Vérifier si l'email existe déjà
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return None, "Cet email est déjà utilisé"
            
            # Vérifier si le username existe déjà
            existing_username = User.query.filter_by(username=data['username']).first()
            if existing_username:
                return None, "Ce nom d'utilisateur est déjà pris"
            
            # Hash le mot de passe
            password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Créer le nouvel utilisateur
            new_user = User(
                user_id=f"usr_{uuid.uuid4().hex[:8]}",
                username=data['username'],
                email=data['email'],
                password_hash=password_hash,
                city=data['city'],
                region=data.get('region', ''),
                bio=data.get('bio', '')
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return new_user.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Erreur lors de l'inscription: {str(e)}"
    
    def login_user(self, email, password):
        """
        Connecter un utilisateur
        """
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return None
            
            # Vérifier le mot de passe
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return user.to_dict()
            
            return None
            
        except Exception as e:
            print(f"Erreur login: {e}")
            return None
    
    # ==========================================
    # GESTION DES UTILISATEURS
    # ==========================================
    
    def get_user(self, user_id):
        """
        Récupérer les infos d'un utilisateur
        """
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user_data = user.to_dict()
            # Ajouter les jeux favoris
            favorite_games = FavoriteGame.query.filter_by(user_id=user_id).all()
            user_data['favorite_games'] = [
                Game.query.filter_by(game_id=fg.game_id).first().to_dict() 
                for fg in favorite_games
            ]
            return user_data
        return None
    
    def update_user_profile(self, user_id, data):
        """
        Mettre à jour le profil d'un utilisateur
        """
        try:
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return None
            
            # Mise à jour des champs autorisés
            allowed_fields = ['username', 'city', 'region', 'bio', 'profile_image_url']
            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            db.session.commit()
            return user.to_dict()
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur update profil: {e}")
            return None
    
    def search_users(self, query, city=None):
        """
        Rechercher des utilisateurs
        """
        try:
            filters = []
            
            if query:
                filters.append(or_(
                    User.username.like(f'%{query}%'),
                    User.bio.like(f'%{query}%')
                ))
            
            if city:
                filters.append(User.city == city)
            
            users = User.query.filter(*filters).limit(20).all()
            return [u.to_dict() for u in users]
            
        except Exception as e:
            print(f"Erreur search users: {e}")
            return []
    
    # ==========================================
    # GESTION DES ÉVÉNEMENTS
    # ==========================================
    
    def create_event(self, data, creator_id):
        """
        Créer un nouvel événement
        """
        try:
            # Validation
            required_fields = ['title', 'game_id', 'city', 'location_text', 'event_start', 'max_participants']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Champ {field} manquant"}
            
            # Vérifier que le jeu existe
            game = Game.query.filter_by(game_id=data['game_id']).first()
            if not game:
                return {"error": "Ce jeu n'existe pas"}
            
            # Créer l'événement
            new_event = Event(
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
            
            db.session.add(new_event)
            db.session.commit()
            
            return new_event.to_dict()
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur création event: {e}")
            return {"error": str(e)}
    
    def get_events(self, city=None, date=None, limit=50):
        """
        Récupérer la liste des événements avec filtres optionnels
        """
        try:
            query = Event.query.filter(Event.status == 'open')
            
            if city:
                query = query.filter(Event.city == city)
            
            if date:
                # Filtrer par date (même jour)
                target_date = datetime.fromisoformat(date)
                query = query.filter(
                    db.func.date(Event.event_start) == target_date.date()
                )
            
            # Trier par date de l'événement
            events = query.order_by(Event.event_start).limit(limit).all()
            
            # Enrichir avec les infos du jeu
            result = []
            for event in events:
                event_data = event.to_dict()
                game = Game.query.filter_by(game_id=event.game_id).first()
                if game:
                    event_data['game'] = game.to_dict()
                result.append(event_data)
            
            return result
            
        except Exception as e:
            print(f"Erreur get events: {e}")
            return []
    
    def get_event_details(self, event_id):
        """
        Récupérer les détails complets d'un événement
        """
        try:
            event = Event.query.filter_by(event_id=event_id).first()
            if not event:
                return None
            
            event_data = event.to_dict(include_participants=True)
            
            # Ajouter les infos du jeu
            game = Game.query.filter_by(game_id=event.game_id).first()
            if game:
                event_data['game'] = game.to_dict()
            
            # Ajouter les infos du créateur
            creator = User.query.filter_by(user_id=event.creator_id).first()
            if creator:
                event_data['creator'] = creator.to_dict()
            
            return event_data
            
        except Exception as e:
            print(f"Erreur get event details: {e}")
            return None
    
    def join_event(self, event_id, user_id):
        """
        Rejoindre un événement
        """
        try:
            # Vérifier que l'événement existe
            event = Event.query.filter_by(event_id=event_id).first()
            if not event:
                return None, "Événement introuvable"
            
            # Vérifier que l'utilisateur n'est pas déjà participant
            existing = EventParticipant.query.filter_by(
                event_id=event_id,
                user_id=user_id
            ).first()
            
            if existing:
                return None, "Vous participez déjà à cet événement"
            
            # Vérifier qu'il reste de la place
            current_count = EventParticipant.query.filter_by(event_id=event_id).count()
            if current_count >= event.max_participants:
                return None, "Événement complet"
            
            # Créer la participation
            participation = EventParticipant(
                participant_id=f"prt_{uuid.uuid4().hex[:8]}",
                event_id=event_id,
                user_id=user_id,
                status='confirmed'
            )
            
            db.session.add(participation)
            
            # Mettre à jour le statut de l'événement si complet
            if current_count + 1 >= event.max_participants:
                event.status = 'full'
            
            db.session.commit()
            
            return participation.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur join event: {e}")
            return None, str(e)
    
    def leave_event(self, event_id, user_id):
        """
        Quitter un événement
        """
        try:
            participation = EventParticipant.query.filter_by(
                event_id=event_id,
                user_id=user_id
            ).first()
            
            if not participation:
                return None, "Vous ne participez pas à cet événement"
            
            db.session.delete(participation)
            
            # Remettre l'événement en "open" si il était full
            event = Event.query.filter_by(event_id=event_id).first()
            if event and event.status == 'full':
                event.status = 'open'
            
            db.session.commit()
            
            return {"success": True}, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur leave event: {e}")
            return None, str(e)
    
    # ==========================================
    # GESTION DES AMIS
    # ==========================================
    
    def add_friend(self, requester_id, receiver_id):
        """
        Envoyer une demande d'ami
        """
        try:
            # Éviter de s'ajouter soi-même
            if requester_id == receiver_id:
                return None, "Vous ne pouvez pas vous ajouter vous-même"
            
            # Normaliser l'ordre (user_id_1 < user_id_2)
            user_id_1, user_id_2 = sorted([requester_id, receiver_id])
            
            # Vérifier si une relation existe déjà
            existing = Friendship.query.filter_by(
                user_id_1=user_id_1,
                user_id_2=user_id_2
            ).first()
            
            if existing:
                return None, "Une demande existe déjà"
            
            # Créer la demande
            friendship = Friendship(
                user_id_1=user_id_1,
                user_id_2=user_id_2,
                action_user_id=requester_id,
                status='pending'
            )
            
            db.session.add(friendship)
            db.session.commit()
            
            return friendship.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur add friend: {e}")
            return None, str(e)
    
    def accept_friend(self, current_user_id, requester_id):
        """
        Accepter une demande d'ami
        """
        try:
            # Normaliser l'ordre
            user_id_1, user_id_2 = sorted([current_user_id, requester_id])
            
            friendship = Friendship.query.filter_by(
                user_id_1=user_id_1,
                user_id_2=user_id_2
            ).first()
            
            if not friendship:
                return None, "Demande introuvable"
            
            # Vérifier que c'est bien le destinataire qui accepte
            if friendship.action_user_id == current_user_id:
                return None, "Vous ne pouvez pas accepter votre propre demande"
            
            friendship.status = 'accepted'
            db.session.commit()
            
            return friendship.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur accept friend: {e}")
            return None, str(e)
    
    def get_friends(self, user_id):
        """
        Récupérer la liste des amis d'un utilisateur
        """
        try:
            friendships = Friendship.query.filter(
                and_(
                    or_(
                        Friendship.user_id_1 == user_id,
                        Friendship.user_id_2 == user_id
                    ),
                    Friendship.status == 'accepted'
                )
            ).all()
            
            friends = []
            for f in friendships:
                friend_id = f.user_id_2 if f.user_id_1 == user_id else f.user_id_1
                friend = User.query.filter_by(user_id=friend_id).first()
                if friend:
                    friends.append(friend.to_dict())
            
            return friends
            
        except Exception as e:
            print(f"Erreur get friends: {e}")
            return []
    
    # ==========================================
    # GESTION DES JEUX FAVORIS
    # ==========================================
    
    def add_favorite_game(self, user_id, game_id):
        """
        Ajouter un jeu aux favoris
        """
        try:
            # Vérifier que le jeu existe
            game = Game.query.filter_by(game_id=game_id).first()
            if not game:
                return None, "Jeu introuvable"
            
            # Vérifier si déjà en favori
            existing = FavoriteGame.query.filter_by(
                user_id=user_id,
                game_id=game_id
            ).first()
            
            if existing:
                return None, "Jeu déjà dans vos favoris"
            
            favorite = FavoriteGame(
                user_id=user_id,
                game_id=game_id
            )
            
            db.session.add(favorite)
            db.session.commit()
            
            return favorite.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur add favorite: {e}")
            return None, str(e)
    
    def remove_favorite_game(self, user_id, game_id):
        """
        Retirer un jeu des favoris
        """
        try:
            favorite = FavoriteGame.query.filter_by(
                user_id=user_id,
                game_id=game_id
            ).first()
            
            if not favorite:
                return None, "Ce jeu n'est pas dans vos favoris"
            
            db.session.delete(favorite)
            db.session.commit()
            
            return {"success": True}, None
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur remove favorite: {e}")
            return None, str(e)
    
    # ==========================================
    # RECHERCHE DE JEUX (via BoardGameAtlas API)
    # ==========================================
    
    def search_games(self, query):
        """
        Rechercher des jeux (d'abord en local, sinon API externe)
        """
        try:
            # Chercher d'abord en local
            local_games = Game.query.filter(
                Game.name.like(f'%{query}%')
            ).limit(10).all()
            
            if local_games:
                return [g.to_dict() for g in local_games]
            
            # TODO: Si pas de résultats locaux, appeler l'API BoardGameAtlas
            # Pour le MVP, on retourne juste la recherche locale
            return []
            
        except Exception as e:
            print(f"Erreur search games: {e}")
            return []


