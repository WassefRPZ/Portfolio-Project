from app.models import db, User, Event, Friendship

class Repository:
    def add(self, entity):
        db.session.add(entity)
        db.session.commit()

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_all_events(self):
        return Event.query.all()

    def get_event_by_id(self, event_id):
        return Event.query.get(event_id)
    
    def update_user(self, user_id, data):
        user = self.get_user_by_id(user_id)
        if user:
            if 'username' in data: user.username = data['username']
            if 'city' in data: user.city = data['city']
            if 'bio' in data: user.bio = data['bio']
            db.session.commit()
        return user

    def get_friendship(self, user1_id, user2_id):
        return Friendship.query.filter(
            ((Friendship.requester_id == user1_id) & (Friendship.receiver_id == user2_id)) |
            ((Friendship.requester_id == user2_id) & (Friendship.receiver_id == user1_id))
        ).first()

    def get_pending_request(self, requester_id, receiver_id):
        return Friendship.query.filter_by(
            requester_id=requester_id, 
            receiver_id=receiver_id, 
            status='pending'
        ).first()
