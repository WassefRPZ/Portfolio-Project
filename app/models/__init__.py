from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
            "city": self.city,
            "bio": self.bio
        }

class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.String(50), primary_key=True)
    creator_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    game_name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.event_id,
            "title": self.title,
            "game": self.game_name,
            "city": self.city,
            "date": self.event_date.isoformat() if self.event_date else None,
            "time": self.event_time.strftime("%H:%M:%S") if self.event_time else None
        }

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requester_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "requester_id": self.requester_id,
            "receiver_id": self.receiver_id,
            "status": self.status
        }
