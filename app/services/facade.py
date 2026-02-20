from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.event import Event

class HBnBFacade:
    """
    Facade Pattern : Cette classe sert d'interface unique entre la couche de présentation (API)
    et la couche de persistance (Repository).
    Elle contient toute la logique métier (Business Logic).
    """

    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.event_repo = InMemoryRepository()

    # Gestion des Utilisateurs

    def create_user(self, user_data):
        """Crée un nouvel utilisateur après validation."""
        # Vérification si l'email existe déjà
        existing_user = self.get_user_by_email(user_data.get('email'))
        if existing_user:
            raise ValueError("Email already registered")

        # Création de l'objet User
        user = User(**user_data)
        
        # Sauvegarde
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """Récupère un utilisateur par son ID."""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Récupère un utilisateur par son email (utile pour le login)."""
        return self.user_repo.get_by_attribute('email', email)

    def update_user(self, user_id, user_data):
        """
        Met à jour un utilisateur.
        Retourne l'objet mis à jour ou None si l'utilisateur n'existe pas.
        """
        # Mise à jour via le repository
        updated = self.user_repo.update(user_id, user_data)
        if not updated:
            return None
        return self.user_repo.get(user_id)

    # Gestion des Événements

    def create_event(self, event_data):
        """
        Crée un événement.
        Vérifie que l'organisateur (user_id) existe bien avant de créer l'événement.
        """
        user_id = event_data.get('user_id')
        organizer = self.user_repo.get(user_id)
        
        if not organizer:
            raise ValueError("Organizer (User) not found")

        # Création de l'objet Event
        event = Event(**event_data)
        
        # Sauvegarde
        self.event_repo.add(event)
        return event

    def get_event(self, event_id):
        """Récupère un événement par son ID."""
        return self.event_repo.get(event_id)

    def get_all_events(self):
        """Récupère la liste complète des événements."""
        return self.event_repo.get_all()
