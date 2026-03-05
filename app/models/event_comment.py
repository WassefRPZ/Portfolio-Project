from datetime import datetime, timezone
from app import db


class EventComment(db.Model):
    """Commentaire laissé par un utilisateur sur un événement BoardGame Hub."""

    __tablename__ = 'event_comments'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id   = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relation vers l'auteur du commentaire
    author = db.relationship('User', foreign_keys=[user_id],
                             backref='event_comments_written', lazy='select')

    def to_dict(self):
        """Sérialise le commentaire en dictionnaire JSON-compatible."""
        result = {
            "id":         self.id,
            "event_id":   self.event_id,
            "user_id":    self.user_id,
            "content":    self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if self.author and self.author.profile:
            result['username']          = self.author.profile.username
            result['profile_image_url'] = self.author.profile.profile_image_url
        return result
