"""Modele User : donnees de compte et authentification."""

from datetime import datetime, timezone
from app import db


class User(db.Model):
    """Compte utilisateur servant a l'authentification et au profil public."""

    __tablename__ = 'users'

    # Identifiant principal du compte.
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Email unique utilise pour la connexion.
    email         = db.Column(db.String(150), unique=True, nullable=False)
    # Mot de passe stocke sous forme de hash.
    password_hash = db.Column(db.String(255), nullable=False)
    # Role applicatif (utilisateur standard ou admin).
    role          = db.Column(db.Enum('user', 'admin'), nullable=False, default='user')
    # Date de creation du compte.
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Profil public lie en relation one-to-one.
    profile = db.relationship('Profile', backref='user', uselist=False,
                              lazy='select', cascade='all, delete-orphan')

    def to_dict(self):
        """Serialise le compte avec email et informations de profil si presentes."""
        data = {
            "id":         self.id,
            "email":      self.email,
            "role":       self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        # Fusionne les champs de profil quand le profil existe.
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
        """Serialise la vue publique sans exposer l'email."""
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
