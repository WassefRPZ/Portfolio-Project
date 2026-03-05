from datetime import datetime
from app import db


class Post(db.Model):
    """Publication du fil d'actualité de la plateforme.
    Supporte 3 types : text, image, news.
    content et image_url sont tous deux optionnels mais au moins l'un doit être fourni.
    Supprimé automatiquement si l'auteur est supprimé.
    """

    __tablename__ = 'posts'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_type  = db.Column(db.Enum('text', 'image', 'news'), nullable=False, default='text')
    content    = db.Column(db.Text, nullable=True)
    image_url  = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations vers likes et commentaires
    author = db.relationship('User', foreign_keys=[author_id],
                             backref='posts', lazy='select')
    likes    = db.relationship('PostLike',    backref='post', lazy='dynamic',
                               cascade='all, delete-orphan',
                               foreign_keys='PostLike.post_id')
    comments = db.relationship('PostComment', backref='post', lazy='dynamic',
                               cascade='all, delete-orphan',
                               foreign_keys='PostComment.post_id')

    def to_dict(self, liked_by_user_id=None):
        """Sérialise le post en dictionnaire JSON-compatible."""
        result = {
            "id":            self.id,
            "author_id":     self.author_id,
            "post_type":     self.post_type,
            "content":       self.content or '',
            "image_url":     self.image_url,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
            "likes_count":   self.likes.count(),
            "comments_count": self.comments.count(),
            "liked_by_me":   False,
        }
        if liked_by_user_id:
            result['liked_by_me'] = self.likes.filter_by(user_id=liked_by_user_id).count() > 0
        if self.author and self.author.profile:
            result['username']          = self.author.profile.username
            result['profile_image_url'] = self.author.profile.profile_image_url
        return result
