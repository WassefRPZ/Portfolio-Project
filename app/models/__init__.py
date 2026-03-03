from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'admin'), default='user')
    city = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role if self.role else None,
            "city": self.city,
            "region": self.region,
            "bio": self.bio,
            "profile_image_url": self.profile_image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Game(db.Model):
    __tablename__ = 'games'
    
    game_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    min_players = db.Column(db.Integer, nullable=False)
    max_players = db.Column(db.Integer, nullable=False)
    play_time = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255))
    
    def to_dict(self):
        return {
            "game_id": self.game_id,
            "name": self.name,
            "description": self.description,
            "min_players": self.min_players,
            "max_players": self.max_players,
            "play_time": self.play_time,
            "image_url": self.image_url
        }


class Event(db.Model):
    __tablename__ = 'events'
    
    event_id = db.Column(db.String(50), primary_key=True)
    creator_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    game_id = db.Column(db.String(50), db.ForeignKey('games.game_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    city = db.Column(db.String(100), nullable=False)
    location_text = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    event_start = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('open', 'full', 'cancelled', 'completed'), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    participants = db.relationship('EventParticipant', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_participants=False):
        data = {
            "event_id": self.event_id,
            "creator_id": self.creator_id,
            "game_id": self.game_id,
            "title": self.title,
            "description": self.description,
            "city": self.city,
            "location_text": self.location_text,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "event_start": self.event_start.isoformat() if self.event_start else None,
            "max_participants": self.max_participants,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "current_participants": len(self.participants)
        }
        
        if include_participants:
            data["participants"] = [p.to_dict() for p in self.participants]
            
        return data


class EventParticipant(db.Model):
    __tablename__ = 'event_participants'
    
    participant_id = db.Column(db.String(50), primary_key=True)
    event_id = db.Column(db.String(50), db.ForeignKey('events.event_id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.Enum('confirmed', 'waitlist', 'cancelled'), default='confirmed')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "participant_id": self.participant_id,
            "event_id": self.event_id,
            "user_id": self.user_id,
            "status": self.status,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None
        }


class Comment(db.Model):
    __tablename__ = 'comments'
    
    comment_id = db.Column(db.String(50), primary_key=True)
    event_id = db.Column(db.String(50), db.ForeignKey('events.event_id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "comment_id": self.comment_id,
            "event_id": self.event_id,
            "user_id": self.user_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Friendship(db.Model):
    __tablename__ = 'friendships'
    
    user_id_1 = db.Column(db.String(50), db.ForeignKey('users.user_id'), primary_key=True)
    user_id_2 = db.Column(db.String(50), db.ForeignKey('users.user_id'), primary_key=True)
    action_user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'declined', 'blocked'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "user_id_1": self.user_id_1,
            "user_id_2": self.user_id_2,
            "action_user_id": self.action_user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FavoriteGame(db.Model):
    __tablename__ = 'favorite_games'
    
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), primary_key=True)
    game_id = db.Column(db.String(50), db.ForeignKey('games.game_id'), primary_key=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "game_id": self.game_id,
            "added_at": self.added_at.isoformat() if self.added_at else None
        }