from datetime import datetime
from app import db


class Friendship(db.Model):
    """
    Relation d'amitié entre deux utilisateurs.
    La clé primaire est composite (user_id_1, user_id_2).
    Par convention, user_id_1 < user_id_2 (trié alphabétiquement)
    pour éviter les doublons (A,B) et (B,A).
    action_user_id = celui qui a envoyé la demande.
    Statuts : pending → accepted / declined.
    """

    __tablename__ = 'friendships'

    user_id_1      = db.Column(db.String(50), db.ForeignKey('users.user_id'), primary_key=True)
    user_id_2      = db.Column(db.String(50), db.ForeignKey('users.user_id'), primary_key=True)
    action_user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    status         = db.Column(db.Enum('pending', 'accepted', 'declined'), default='pending')
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user1       = db.relationship('User', foreign_keys=[user_id_1],      lazy='select')
    user2       = db.relationship('User', foreign_keys=[user_id_2],      lazy='select')
    action_user = db.relationship('User', foreign_keys=[action_user_id], lazy='select')

    def to_dict(self):
        """Sérialise la relation d'amitié en dictionnaire JSON-compatible."""
        return {
            "user_id_1":      self.user_id_1,
            "user_id_2":      self.user_id_2,
            "action_user_id": self.action_user_id,
            "status":         self.status,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
            "updated_at":     self.updated_at.isoformat() if self.updated_at else None,
        }
