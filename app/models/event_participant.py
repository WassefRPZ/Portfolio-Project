from datetime import datetime, timezone
from app import db


class EventParticipant(db.Model):
    __tablename__ = 'event_participants'

    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id  = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    status    = db.Column(db.Enum('confirmed', 'pending'), default='confirmed')
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_event_user'),
    )

    user = db.relationship('User', foreign_keys=[user_id],
                           backref='participations', lazy='select')

    def to_dict(self):
        data = {
            "id":        self.id,
            "event_id":  self.event_id,
            "user_id":   self.user_id,
            "status":    self.status,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
        }
        # Include user info when the relationship is loaded
        if self.user and self.user.profile:
            data["username"] = self.user.profile.username
            data["profile_image_url"] = self.user.profile.profile_image_url
            data["city"] = self.user.profile.city or ""
        return data
