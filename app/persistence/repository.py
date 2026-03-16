"""Repositories SQLAlchemy centralisant l'acces aux donnees.

Ce module fournit:
- une base generique (save/delete/commit)
- des repositories specialises par modele
- des requetes optimisees pour les besoins de l'API
"""
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
    """Repository de base qui expose les operations generiques save, delete et commit.
    Toutes les classes repository specialisees heritent de cette base.
    """

    def save(self, obj):
        """Persiste un objet ORM (nouveau ou modifie) dans la base de donnees."""
        # Choix d'implementation: un save valide immediatement la transaction.
        # Les operations multi-etapes sont orchestrees dans la couche service.
        db.session.add(obj)
        db.session.commit()
        return obj

    def delete(self, obj):
        """Supprime un objet ORM de la base de donnees."""
        db.session.delete(obj)
        db.session.commit()

    def commit(self):
        """Valide les changements en attente sans ajouter explicitement d'objet."""
        db.session.commit()



class UserRepository(SQLAlchemyRepository):
    """Centralise toutes les operations SQL sur le modele User."""

    def get_by_id(self, user_id):
        """Recupere un utilisateur via sa cle primaire."""
        return User.query.filter_by(id=user_id).first()

    def get_by_email(self, email):
        """Recupere un utilisateur via son email (utilise pour la connexion)."""
        return User.query.filter_by(email=email).first()

    def search(self, query, city=None):
        """Recherche des utilisateurs par pseudo (match partiel), avec filtre ville optionnel.
        Les jokers SQL LIKE (%, _) sont echappes pour eviter les recherches parasites.
        Le resultat est limite a 20 lignes pour contenir le volume de donnees.
        """
        q = (
            User.query
            .join(Profile, User.id == Profile.user_id)
        )
        if query:
            # Echappe les caracteres speciaux de LIKE avant de construire le motif
            safe_q = query.replace('%', r'\%').replace('_', r'\_')
            q = q.filter(Profile.username.like(f'%{safe_q}%'))
        if city:
            q = q.filter(Profile.city == city)
        return q.limit(20).all()



class ProfileRepository(SQLAlchemyRepository):
    """Operations SQL liees aux profils utilisateurs (relation 1-1 avec User)."""

    def get_by_user_id(self, user_id):
        """Recupere le profil associe a un utilisateur."""
        return Profile.query.filter_by(user_id=user_id).first()

    def get_by_username(self, username):
        """Verifie si un pseudo existe deja (utile a l'inscription)."""
        return Profile.query.filter_by(username=username).first()



class GameRepository(SQLAlchemyRepository):
    """Operations de lecture sur le catalogue de jeux."""

    def get_by_id(self, game_id):
        """Recupere un jeu par sa cle primaire."""
        return Game.query.filter_by(id=game_id).first()

    def get_all(self, limit=50, offset=0):
        """Retourne une liste paginee de jeux triee par ordre alphabetique."""
        return Game.query.order_by(Game.name).offset(offset).limit(limit).all()

    def search(self, query, limit=20):
        """Recherche partielle sur le nom des jeux, avec limite configurable."""
        safe_q = query.replace('%', r'\%').replace('_', r'\_')
        return (
            Game.query
            .filter(Game.name.like(f'%{safe_q}%'))
            .order_by(Game.name)
            .limit(limit)
            .all()
        )

    def count(self):
        """Retourne le nombre total de jeux (utile pour la pagination)."""
        return Game.query.count()



class EventRepository(SQLAlchemyRepository):
    """Operations SQL sur les evenements, dont les filtres geographiques."""

    def get_by_id(self, event_id):
        """Recuperation simple d'un evenement (sans prechargement des relations)."""
        return Event.query.filter_by(id=event_id).first()

    def get_by_id_full(self, event_id):
        """Recupere un evenement avec ses relations prechargees en une seule passe:
        profil du createur, jeu associe, participants et profils des participants.
        L'usage de joinedload evite le probleme N+1 lors de la serialisation.
        """
        return (
            Event.query
            .options(
                joinedload(Event.creator).joinedload(User.profile),
                joinedload(Event.game_obj),
                joinedload(Event.participants)
                    .joinedload(EventParticipant.user)
                    .joinedload(User.profile),
            )
            .filter_by(id=event_id)
            .first()
        )

    def get_open_events(self, city=None, date=None, limit=50, offset=0,
                         lat=None, lng=None, radius=10):
        """Retourne les evenements ouverts avec pagination et filtres optionnels:
        - city: egalite exacte sur la ville
        - date: date ISO 8601, comparee sur le jour calendaire
        - lat/lng/radius: filtre geographique via la loi des cosinus spherique
        Renvoie un tuple (events, total_count, error).
        """
        base = Event.query.filter_by(status='open')

        if city:
            base = base.filter_by(city=city)

        if date:
            try:
                target = datetime.fromisoformat(date)
                # Compare uniquement le jour, sans tenir compte de l'heure
                base = base.filter(db.func.date(Event.date_time) == target.date())
            except (ValueError, TypeError):
                # Le contrat de retour reste stable: (events, total, error).
                return None, 0, "Format de date invalide. Utiliser ISO 8601 (ex: 2024-12-25)"

        if lat is not None and lng is not None:
            # Loi des cosinus spherique: calcule une distance en km entre deux coordonnees.
            # lat_r est la latitude de reference en radians (constante pour la requete).
            lat_r  = radians(lat)
            haversine = (
                6371 * db.func.acos(         # Rayon moyen de la Terre (km)
                    cos(lat_r)
                    * db.func.cos(db.func.radians(Event.latitude))
                    * db.func.cos(db.func.radians(Event.longitude) - radians(lng))
                    + sin(lat_r)
                    * db.func.sin(db.func.radians(Event.latitude))
                )
            )
            # Ne conserve que les evenements geolocalises dans le rayon demande
            base = base.filter(
                Event.latitude.isnot(None),
                Event.longitude.isnot(None),
                haversine <= radius,
            )

        # Compte total avant pagination pour renvoyer un total coherent au client
        total_count = base.with_entities(func.count(Event.id)).scalar()
        events = (
            base
            .options(joinedload(Event.game_obj), joinedload(Event.participants))
            .order_by(Event.date_time)   # Tri chronologique (prochains evenements d'abord)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return events, total_count, None

    def search(self, query):
        """Recherche partielle sur le titre et la description des evenements.
        Seuls les evenements ouverts sont retournes, tries par date, limites a 20.
        """
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
    """Gere les inscriptions des utilisateurs aux evenements."""

    def get(self, event_id, user_id, status='confirmed'):
        """Recupere une inscription pour un triplet (event, user, status).
        Sert principalement a verifier si un utilisateur est deja inscrit.
        """
        return EventParticipant.query.filter_by(
            event_id=event_id, user_id=user_id, status=status
        ).first()

    def get_any(self, event_id, user_id):
        """Recupere une inscription quel que soit son statut (pending, confirmed, ...)."""
        return EventParticipant.query.filter_by(
            event_id=event_id, user_id=user_id
        ).first()

    def count_confirmed(self, event_id):
        """Compte les participants confirmes d'un evenement (controle de max_players)."""
        return EventParticipant.query.filter_by(
            event_id=event_id, status='confirmed'
        ).count()



class EventCommentRepository(SQLAlchemyRepository):
    """Recuperation des commentaires associes aux evenements."""

    def get_by_event(self, event_id, limit=50, offset=0):
        """Retourne les commentaires d'un evenement avec pagination, du plus ancien au plus recent.
        Le profil de l'auteur est precharge pour eviter les requetes N+1 au rendu.
        """
        return (
            EventComment.query
            .options(joinedload(EventComment.author).joinedload(User.profile))
            .filter_by(event_id=event_id)
            .order_by(EventComment.created_at)   # Ordre chronologique (anciens vers recents)
            .offset(offset)
            .limit(limit)
            .all()
        )



class FavoriteGameRepository(SQLAlchemyRepository):
    """Gere la relation plusieurs-a-plusieurs entre utilisateurs et jeux favoris."""

    def get(self, user_id, game_id):
        """Verifie si un jeu est deja dans les favoris d'un utilisateur."""
        return FavoriteGame.query.filter_by(
            user_id=user_id, game_id=game_id
        ).first()

    def get_games_for_user(self, user_id):
        """Retourne la liste complete des objets Game favoris d'un utilisateur.
        Utilise un join explicite via la table pivot FavoriteGame.
        """
        # On retourne directement des objets Game pour simplifier la serialisation API.
        return (
            db.session.query(Game)
            .join(FavoriteGame, Game.id == FavoriteGame.game_id)
            .filter(FavoriteGame.user_id == user_id)
            .all()
        )



class FriendRepository(SQLAlchemyRepository):
    """Gere le graphe d'amitie entre utilisateurs.
    Les paires sont stockees avec un ordre canonique (petit id puis grand id)
    pour garantir une seule ligne par duo, quel que soit le demandeur.
    """

    def _sorted_ids(self, a, b):
        """Retourne (id_min, id_max) pour imposer un ordre de paire stable.
        Cela garantit la coherence de l'unicite sur (user_id_1, user_id_2).
        """
        return (min(a, b), max(a, b))

    def get_friendship(self, user_a, user_b):
        """Cherche la relation d'amitie entre deux utilisateurs, sans dependre de l'ordre."""
        u1, u2 = self._sorted_ids(user_a, user_b)
        return Friend.query.filter_by(user_id_1=u1, user_id_2=u2).first()

    def get_friends(self, user_id):
        """Retourne toutes les relations acceptees d'un utilisateur.
        Un utilisateur peut apparaitre en user_id_1 ou user_id_2, les deux cas sont testes.
        """
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
        """Retourne les demandes recues encore en attente.
        Le filtre requester_id != user_id exclut les demandes envoyees par l'utilisateur lui-meme.
        """
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
        """Retourne les demandes envoyees par l'utilisateur et non encore traitees."""
        return (
            Friend.query
            .filter(
                Friend.status == 'pending',
                Friend.requester_id == user_id,
            )
            .all()
        )


class PostRepository(SQLAlchemyRepository):
    """Operations SQL sur les posts du fil d'actualite."""

    def get_by_id(self, post_id):
        """Recupere un post par cle primaire via l'API session SQLAlchemy 2.x."""
        return db.session.get(Post, post_id)

    def get_all(self, limit=50, offset=0):
        """Retourne tous les posts (du plus recent au plus ancien) avec pagination.
        Le profil auteur est precharge pour eviter les requetes N+1.
        """
        total = Post.query.count()
        posts = (
            Post.query
            .options(joinedload(Post.author).joinedload(User.profile))
            .order_by(Post.created_at.desc())   # Plus recents en premier
            .offset(offset).limit(limit)
            .all()
        )
        # Convention commune: (liste, total) pour les endpoints pagines.
        return posts, total

    def get_by_author(self, author_id, limit=50, offset=0):
        """Retourne les posts d'un auteur, tries du plus recent au plus ancien."""
        total = Post.query.filter_by(author_id=author_id).count()
        posts = (
            Post.query
            .filter_by(author_id=author_id)
            .options(joinedload(Post.author).joinedload(User.profile))
            .order_by(Post.created_at.desc())
            .offset(offset).limit(limit)
            .all()
        )
        # Convention commune: (liste, total) pour les endpoints pagines.
        return posts, total



