"""Modele Event : structure de l'evenement et relations ORM associees."""

from datetime import datetime, timezone
from app import db


class Event(db.Model):
    """Evenement organise autour d'un jeu, avec capacite et participants."""

    __tablename__ = 'events'

    # Identifiant technique de l'evenement.
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Createur de l'evenement (utilisateur organisateur).
    creator_id    = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    # Jeu associe a la session.
    game_id       = db.Column(db.Integer, db.ForeignKey('games.id'),  nullable=False)
    # Titre visible dans les listes et details.
    title         = db.Column(db.String(200), nullable=False)
    # Description libre (optionnelle).
    description   = db.Column(db.Text)
    # Localisation textuelle principale.
    city          = db.Column(db.String(100), nullable=False)
    # Region optionnelle pour filtrage geographique.
    region        = db.Column(db.String(100), nullable=True, default=None)
    # Adresse/detail du lieu (bar, asso, domicile, etc.).
    location_text = db.Column(db.String(255), nullable=False)
    # Date et heure planifiees.
    date_time     = db.Column(db.DateTime,    nullable=False)
    # Nombre maximum de places.
    max_players   = db.Column(db.Integer,     nullable=False)
    # Etat de l'evenement dans son cycle de vie.
    status        = db.Column(
        db.Enum('open', 'full', 'cancelled', 'completed'),
        default='open'
    )
    # Image de couverture optionnelle.
    cover_url     = db.Column(db.String(255))    
    # Coordonnees geographiques optionnelles.
    latitude      = db.Column(db.Float)
    longitude     = db.Column(db.Float)
    # Date de creation de l'enregistrement.
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relations ORM pour naviguer facilement entre les entites.
    creator      = db.relationship('User',             foreign_keys=[creator_id],
                                   backref='events_created', lazy='select')
    game_obj     = db.relationship('Game',             foreign_keys=[game_id],
                                   backref='events',         lazy='select')
    participants = db.relationship('EventParticipant', backref='event',
                                   lazy='select', cascade='all, delete-orphan')
    event_comments = db.relationship('EventComment',   backref='event',
                                     lazy='select', cascade='all, delete-orphan')

    def to_dict(self, include_participants=False):
        """Serialise l'evenement en dictionnaire API.

        include_participants=True ajoute la liste des participants confirmes.
        """
        # On ne compte que les inscriptions confirmees.
        confirmed = [p for p in self.participants if p.status == 'confirmed']

        data = {
            "id":              self.id,
            "creator_id":      self.creator_id,
            "game_id":         self.game_id,
            "title":           self.title,
            "description":     self.description or '',
            "city":            self.city,
            "region":          self.region or '',
            "location_text":   self.location_text,
            "date_time":       self.date_time.isoformat() if self.date_time else None,
            "max_players":     self.max_players,
            "status":          self.status,
            "cover_url":       self.cover_url,
            "latitude":        self.latitude,
            "longitude":       self.longitude,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
            "current_players": len(confirmed),
        }

        if include_participants:
            # Retour detaille utilise par les vues detail evenement.
            data["participants"] = [p.to_dict() for p in confirmed]

        return data
