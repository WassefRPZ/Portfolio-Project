from app import db


class PostLike(db.Model):
    """Like d'un utilisateur sur un post."""

    __tablename__ = 'post_likes'

    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id  = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id,
        }
