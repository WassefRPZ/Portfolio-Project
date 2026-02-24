import uuid
from datetime import datetime

class User:
    """
    Classe représentant un utilisateur dans l'application Board Game Hub.
    """
    def __init__(self, email, password, first_name, last_name, username, city="", bio="", is_admin=False):
        self.id = str(uuid.uuid4())
        self.email = email
        self.password = password  # TODO:
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.city = city
        self.bio = bio
        self.is_admin = is_admin
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        """
        Retourne l'objet sous forme de dictionnaire pour l'API.
        Convertit les objets datetime en chaînes de caractères (ISO format).
        """
        return {
            "user_id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "city": self.city,
            "bio": self.bio,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def update(self, data):
        """
        Met à jour les attributs de l'utilisateur et actualise updated_at.
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
