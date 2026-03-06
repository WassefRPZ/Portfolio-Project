from datetime import datetime, timezone
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.Enum('user', 'admin'), nullable=False, default='user')
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    profile = db.relationship('Profile', backref='user', uselist=False,
                              lazy='select', cascade='all, delete-orphan')

    def to_dict(self):
        data = {
            "id":         self.id,
            "email":      self.email,
            "role":       self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if self.profile:
            data.update({
                "username":          self.profile.username,
                "bio":               self.profile.bio or '',
                "city":              self.profile.city or '',
                "region":            self.profile.region or '',
                "profile_image_url": self.profile.profile_image_url,
            })
        return data

    def to_public_dict(self):
        data = {
            "id":         self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if self.profile:
            data.update({
                "username":          self.profile.username,
                "bio":               self.profile.bio or '',
                "city":              self.profile.city or '',
                "region":            self.profile.region or '',
                "profile_image_url": self.profile.profile_image_url,
            })
        return data
