from datetime import datetime
from app import db


class Post(db.Model):
    """Publication du fil d'actualité de la plateforme.
    Chaque post est lié à un auteur (author_id → users).
    Supprimé automatiquement si l'auteur est supprimé.
    """

    __tablename__ = 'posts'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers l'auteur
    author = db.relationship('User', foreign_keys=[author_id],
                             backref='posts', lazy='select')

    def to_dict(self):
        """Sérialise le post en dictionnaire JSON-compatible."""
        return {
            "id":         self.id,
            "author_id":  self.author_id,
            "content":    self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
