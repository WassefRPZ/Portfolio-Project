from datetime import datetime, timezone
from app import db


class Friend(db.Model):
    """
    Relation d'amitié entre deux utilisateurs.
    Convention : user_id_1 < user_id_2 (enforcer côté applicatif)
    pour éviter les doublons (A,B) et (B,A).
    requester_id : ID réel de l'expéditeur (indépendant du tri).
    Statuts : pending → accepted. Refus = suppression de la ligne.
    """

    __tablename__ = 'friends'

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id_1    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id_2    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status       = db.Column(db.Enum('pending', 'accepted'), default='pending')
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id_1', 'user_id_2', name='uq_friendship'),
    )

    user1     = db.relationship('User', foreign_keys=[user_id_1], lazy='select')
    user2     = db.relationship('User', foreign_keys=[user_id_2], lazy='select')
    requester = db.relationship('User', foreign_keys=[requester_id], lazy='select')

    def to_dict(self):
        """Sérialise la relation d'amitié en dictionnaire JSON-compatible."""
        return {
            "id":           self.id,
            "user_id_1":    self.user_id_1,
            "user_id_2":    self.user_id_2,
            "requester_id": self.requester_id,
            "status":       self.status,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
        }
