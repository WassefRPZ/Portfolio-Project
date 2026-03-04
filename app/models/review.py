from datetime import datetime
from app import db


class Review(db.Model):
    """Avis laissé sur un événement OU sur un autre joueur.
    Les deux cibles sont mutuellement exclusives (enforcer côté applicatif) :
    - event_id renseigné + reviewed_user_id NULL  → review d'événement
    - event_id NULL + reviewed_user_id renseigné  → review de joueur
    rating : note de 1 à 5.
    """

    __tablename__ = 'reviews'

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reviewer_id      = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    event_id         = db.Column(db.Integer, db.ForeignKey('events.id'),  nullable=True)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=True)
    rating           = db.Column(db.SmallInteger, nullable=False)   # 1 à 5
    comment          = db.Column(db.Text)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    reviewer      = db.relationship('User',  foreign_keys=[reviewer_id],
                                    backref='reviews_written', lazy='select')
    event         = db.relationship('Event', foreign_keys=[event_id],
                                    backref='reviews',         lazy='select')
    reviewed_user = db.relationship('User',  foreign_keys=[reviewed_user_id],
                                    backref='reviews_received', lazy='select')

    def to_dict(self):
        """Sérialise l'avis en dictionnaire JSON-compatible."""
        return {
            "id":               self.id,
            "reviewer_id":      self.reviewer_id,
            "event_id":         self.event_id,
            "reviewed_user_id": self.reviewed_user_id,
            "rating":           self.rating,
            "comment":          self.comment or '',
            "created_at":       self.created_at.isoformat() if self.created_at else None,
        }
