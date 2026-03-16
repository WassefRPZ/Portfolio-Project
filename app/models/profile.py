"""Modele Profile : informations publiques d'un utilisateur."""

from app import db


class Profile(db.Model):
    """Profil public associe a un compte utilisateur."""

    __tablename__ = 'profiles'

    # Identifiant interne du profil.
    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Lien OneToOne vers le compte User.
    user_id           = db.Column(db.Integer, db.ForeignKey('users.id'),
                                  nullable=False, unique=True)
    # Pseudonyme unique visible publiquement.
    username          = db.Column(db.String(50), unique=True, nullable=False)
    # Informations facultatives du profil.
    bio               = db.Column(db.Text)
    city              = db.Column(db.String(100))
    region            = db.Column(db.String(100))
    profile_image_url = db.Column(db.String(255))

    def to_dict(self):
        """Serialise le profil pour les reponses API."""
        return {
            "id":                self.id,
            "user_id":           self.user_id,
            "username":          self.username,
            "bio":               self.bio or '',
            "city":              self.city or '',
            "region":            self.region or '',
            "profile_image_url": self.profile_image_url,
        }
