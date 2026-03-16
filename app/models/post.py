"""Modele Post : publication du fil social (texte/image/news)."""

from datetime import datetime, timezone
from app import db


class Post(db.Model):
    """Publication du fil social: texte, image ou actualite."""

    __tablename__ = 'posts'

    # Identifiant du post.
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Auteur de la publication.
    author_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Type de contenu pour adapter l'affichage frontend.
    post_type  = db.Column(db.Enum('text', 'image', 'news'), nullable=False, default='text')
    # Corps texte (peut etre vide pour un post image).
    content    = db.Column(db.Text, nullable=True)
    # Image associee au post (optionnelle).
    image_url  = db.Column(db.String(255), nullable=True)
    # Date de publication.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relation vers l'utilisateur auteur.
    author = db.relationship('User', backref='posts', lazy='select')

    def to_dict(self):
        """Retourne le post avec infos de profil utiles a l'affichage."""
        return {
            "id":                self.id,
            "author_id":         self.author_id,
            "username":          self.author.profile.username if self.author and self.author.profile else None,
            "profile_image_url": self.author.profile.profile_image_url if self.author and self.author.profile else None,
            "post_type":         self.post_type,
            "content":           self.content,
            "image_url":         self.image_url,
            "created_at":        self.created_at.isoformat() if self.created_at else None,
        }
