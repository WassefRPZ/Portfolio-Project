from datetime import datetime, timezone
from app import db


class Event(db.Model):
    """
    Événement de jeu de société organisé par un utilisateur.
    Un événement est lié à un jeu et se tient dans une ville.
    Statuts possibles : open → full → cancelled / completed.
    city / region / location_text : données issues de OpenCage Geocoding API.
    """

    __tablename__ = 'events'

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creator_id    = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    game_id       = db.Column(db.Integer, db.ForeignKey('games.id'),  nullable=False)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text)
    city          = db.Column(db.String(100), nullable=False)
    region        = db.Column(db.String(100), nullable=True, default=None)
    location_text = db.Column(db.String(255), nullable=False)
    date_time     = db.Column(db.DateTime,    nullable=False)
    max_players   = db.Column(db.Integer,     nullable=False)
    status        = db.Column(
        db.Enum('open', 'full', 'cancelled', 'completed'),
        default='open'
    )
    cover_url     = db.Column(db.String(255))    
    latitude      = db.Column(db.Float)                # latitude  (OpenCage Geocoding)
    longitude     = db.Column(db.Float)                # longitude (OpenCage Geocoding)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    creator      = db.relationship('User',             foreign_keys=[creator_id],
                                   backref='events_created', lazy='select')
    game_obj     = db.relationship('Game',             foreign_keys=[game_id],
                                   backref='events',         lazy='select')
    participants = db.relationship('EventParticipant', backref='event',
                                   lazy='select', cascade='all, delete-orphan')
    event_comments = db.relationship('EventComment',   backref='event',
                                     lazy='select', cascade='all, delete-orphan')

    def to_dict(self, include_participants=False):
        """Sérialise l'événement. include_participants=True ajoute la liste des inscrits."""
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
            data["participants"] = [p.to_dict() for p in confirmed]

        return data
