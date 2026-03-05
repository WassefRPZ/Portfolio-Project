from datetime import datetime
from app import db


class EventParticipant(db.Model):
    """
    Inscription d'un utilisateur à un événement.
    statut 'confirmed' = place confirmée.
    statut 'pending'   = en attente de confirmation de l'organisateur.
    Un utilisateur ne peut s'inscrire qu'une seule fois par événement (UNIQUE).
    """

    __tablename__ = 'event_participants'

    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id  = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    status    = db.Column(db.Enum('confirmed', 'pending'), default='confirmed')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_event_user'),
    )

    # Relation vers l'utilisateur inscrit
    user = db.relationship('User', foreign_keys=[user_id],
                           backref='participations', lazy='select')

    def to_dict(self):
        """Sérialise la participation en dictionnaire JSON-compatible."""
        return {
            "id":        self.id,
            "event_id":  self.event_id,
            "user_id":   self.user_id,
            "status":    self.status,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
        }
