from app import db


class Profile(db.Model):
    """Profil public d'un membre BoardGame Hub.
    city / region     : renseignés lors de l'inscription, modifiables ensuite.
    """

    __tablename__ = 'profiles'

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('users.id'),
                                  nullable=False, unique=True)  # 1 seul profil par utilisateur
    username          = db.Column(db.String(50), unique=True, nullable=False)
    bio               = db.Column(db.Text)
    city              = db.Column(db.String(100))
    region            = db.Column(db.String(100))
    profile_image_url = db.Column(db.String(255))  # URL Cloudinary

    def to_dict(self):
        """Sérialise le profil en dictionnaire JSON-compatible."""
        return {
            "id":                self.id,
            "user_id":           self.user_id,
            "username":          self.username,
            "bio":               self.bio or '',
            "city":              self.city or '',
            "region":            self.region or '',
            "profile_image_url": self.profile_image_url,
        }
