from datetime import datetime
from app import db


class Comment(db.Model):
    """Commentaire laissé par un utilisateur sur un événement BoardGame Hub."""

    __tablename__ = 'comments'

    comment_id = db.Column(db.String(50), primary_key=True)
    event_id   = db.Column(db.String(50), db.ForeignKey('events.event_id'), nullable=False)
    user_id    = db.Column(db.String(50), db.ForeignKey('users.user_id'),   nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers l'auteur du commentaire
    author = db.relationship('User', foreign_keys=[user_id],
                             backref='comments_written', lazy='select')

    def to_dict(self):
        """Sérialise le commentaire en dictionnaire JSON-compatible."""
        return {
            "comment_id": self.comment_id,
            "event_id":   self.event_id,
            "user_id":    self.user_id,
            "content":    self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
