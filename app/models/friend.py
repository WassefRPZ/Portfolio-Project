"""Modele Friend : relation d'amitie avec suivi du demandeur et de l'etat."""

from datetime import datetime, timezone
from app import db


class Friend(db.Model):
    """Relation d'amitie entre deux utilisateurs et son etat."""

    __tablename__ = 'friends'

    # Identifiant technique de la relation.
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Premiere borne normalisee de la paire d'utilisateurs.
    user_id_1    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Seconde borne normalisee de la paire d'utilisateurs.
    user_id_2    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Utilisateur qui a initie la demande.
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Etat de la relation: en attente ou acceptee.
    status       = db.Column(db.Enum('pending', 'accepted'), default='pending')
    # Date de creation de la demande.
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Empoche les doublons pour une meme paire d'utilisateurs.
    __table_args__ = (
        db.UniqueConstraint('user_id_1', 'user_id_2', name='uq_friendship'),
    )

    # Relations ORM vers les trois roles: user1, user2 et demandeur.
    user1     = db.relationship('User', foreign_keys=[user_id_1], lazy='select')
    user2     = db.relationship('User', foreign_keys=[user_id_2], lazy='select')
    requester = db.relationship('User', foreign_keys=[requester_id], lazy='select')

    def to_dict(self):
        """Retourne une representation standard de la relation d'amitie."""
        return {
            "id":           self.id,
            "user_id_1":    self.user_id_1,
            "user_id_2":    self.user_id_2,
            "requester_id": self.requester_id,
            "status":       self.status,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
        }
