from datetime import datetime, timezone
from app import db


class Post(db.Model):
    __tablename__ = 'posts'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_type  = db.Column(db.Enum('text', 'image', 'news'), nullable=False, default='text')
    content    = db.Column(db.Text, nullable=True)
    image_url  = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    author = db.relationship('User', backref='posts', lazy='select')

    def to_dict(self):
        return {
            "id":         self.id,
            "author_id":  self.author_id,
            "post_type":  self.post_type,
            "content":    self.content,
            "image_url":  self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
