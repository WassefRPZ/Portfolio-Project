from datetime import datetime
from app import db


class Post(db.Model):
    """
    Publication communautaire rédigée par un utilisateur.
    Sert de tableau d'affichage : annonces, questions sur un jeu,
    recherche de partenaires de jeu, etc.
    """

    __tablename__ = 'posts'

    post_id    = db.Column(db.String(50), primary_key=True)
    author_id  = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    title      = db.Column(db.String(200), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relation vers l'auteur de la publication
    author = db.relationship('User', foreign_keys=[author_id],
                             backref='posts', lazy='select')

    def to_dict(self):
        """Sérialise la publication en dictionnaire JSON-compatible."""
        return {
            "post_id":    self.post_id,
            "author_id":  self.author_id,
            "title":      self.title,
            "content":    self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
