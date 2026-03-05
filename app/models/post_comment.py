from datetime import datetime
from app import db


class PostComment(db.Model):
    """Commentaire laissé par un utilisateur sur un post."""

    __tablename__ = 'post_comments'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('posts.id'),  nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', foreign_keys=[user_id],
                             backref='post_comments_written', lazy='select')

    def to_dict(self):
        result = {
            "id":         self.id,
            "post_id":    self.post_id,
            "user_id":    self.user_id,
            "content":    self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if self.author and self.author.profile:
            result['username']          = self.author.profile.username
            result['profile_image_url'] = self.author.profile.profile_image_url
        return result
