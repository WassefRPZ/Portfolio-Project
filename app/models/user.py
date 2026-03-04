from datetime import datetime
from app import db


class User(db.Model):
    """Compte utilisateur de BoardGame Hub."""

    __tablename__ = 'users'

    user_id           = db.Column(db.String(50), primary_key=True)
    username          = db.Column(db.String(50), unique=True, nullable=False)
    email             = db.Column(db.String(100), unique=True, nullable=False)
    password_hash     = db.Column(db.String(255), nullable=False)
    first_name        = db.Column(db.String(100), default='')
    last_name         = db.Column(db.String(100), default='')
    city              = db.Column(db.String(100), nullable=False)
    region            = db.Column(db.String(100), default='')
    bio               = db.Column(db.Text)
    is_admin          = db.Column(db.Boolean, nullable=False, default=False)
    profile_image_url = db.Column(db.String(255))
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Sérialise l'utilisateur en dictionnaire JSON-compatible."""
        return {
            "user_id":           self.user_id,
            "username":          self.username,
            "email":             self.email,
            "first_name":        self.first_name or '',
            "last_name":         self.last_name or '',
            "city":              self.city,
            "region":            self.region or '',
            "bio":               self.bio or '',
            "is_admin":          bool(self.is_admin),
            "profile_image_url": self.profile_image_url,
            "created_at":        self.created_at.isoformat() if self.created_at else None,
        }
