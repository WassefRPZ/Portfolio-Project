from app.persistence.repository import Repository
from app.models import User, Event
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class BoardGameFacade:
    def __init__(self):
        self.repository = Repository()

    def register_user(self, data):
        if self.repository.get_user_by_email(data['email']):
            return None, "Email déjà utilisé"
        
        new_id = f"usr_{uuid.uuid4().hex[:8]}"
        hashed_pw = generate_password_hash(data['password'])
        
        user = User(
            user_id=new_id,
            username=data['username'],
            email=data['email'],
            password_hash=hashed_pw,
            city=data.get('city', ''),
            bio=data.get('bio', '')
        )
        self.repository.add(user)
        return user.to_dict(), None

    def login_user(self, email, password):
        user = self.repository.get_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            return user.to_dict()
        return None

    def create_event(self, data, creator_id):
        new_id = f"evt_{uuid.uuid4().hex[:8]}"
        event = Event(
            event_id=new_id,
            creator_id=creator_id,
            title=data['title'],
            description=data.get('description', ''),
            game_name=data['game_name'],
            city=data['city'],
            event_date=data['event_date'],
            event_time=data['event_time'],
            max_participants=data['max_participants']
        )
        self.repository.add(event)
        return event.to_dict()

    def get_events(self):
        events = self.repository.get_all_events()
        return [e.to_dict() for e in events]
    
    def get_user(self, user_id):
        user = self.repository.get_user_by_id(user_id)
        return user.to_dict() if user else None

    def update_user_profile(self, user_id, data):
        user = self.repository.update_user(user_id, data)
        return user.to_dict() if user else None

    def add_friend(self, requester_id, receiver_id):
        if requester_id == receiver_id:
            return None, "Vous ne pouvez pas vous ajouter vous-même."
        
        if not self.repository.get_user_by_id(receiver_id):
            return None, "Utilisateur introuvable."

        existing = self.repository.get_friendship(requester_id, receiver_id)
        if existing:
            return None, "Une relation existe déjà ou est en attente."

        from app.models import Friendship
        friendship = Friendship(requester_id=requester_id, receiver_id=receiver_id, status='pending')
        self.repository.add(friendship)
        return friendship.to_dict(), None

    def accept_friend(self, user_id, requester_id):
        friendship = self.repository.get_pending_request(requester_id, user_id)
        if not friendship:
            return None, "Aucune demande en attente trouvée."
        
        friendship.status = 'accepted'
        self.repository.add(friendship)
        return {"result": "Friend request accepted"}, None
