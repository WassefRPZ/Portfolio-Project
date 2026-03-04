from datetime import datetime
from app import db


class EventParticipant(db.Model):
    """
    Inscription d'un utilisateur à un événement.
    statut 'confirmed' = place confirmée.
    statut 'waitlist'  = réservé pour une future liste d'attente.
    """

    __tablename__ = 'event_participants'

    participant_id = db.Column(db.String(50), primary_key=True)
    event_id       = db.Column(db.String(50), db.ForeignKey('events.event_id'), nullable=False)
    user_id        = db.Column(db.String(50), db.ForeignKey('users.user_id'),   nullable=False)
    status         = db.Column(db.Enum('confirmed', 'waitlist'), default='confirmed')
    joined_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers l'utilisateur inscrit
    user = db.relationship('User', foreign_keys=[user_id],
                           backref='participations', lazy='select')

    def to_dict(self):
        """Sérialise la participation en dictionnaire JSON-compatible."""
        return {
            "participant_id": self.participant_id,
            "event_id":       self.event_id,
            "user_id":        self.user_id,
            "status":         self.status,
            "joined_at":      self.joined_at.isoformat() if self.joined_at else None,
        }
