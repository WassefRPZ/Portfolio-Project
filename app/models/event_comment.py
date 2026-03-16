"""Modele EventComment : commentaires d'evenements et lien avec l'auteur."""

from datetime import datetime, timezone
from app import db


class EventComment(db.Model):
    """Commentaire laisse par un utilisateur sur un evenement."""

    __tablename__ = 'event_comments'

    # Identifiant technique du commentaire.
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Evenement cible du commentaire.
    event_id   = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    # Auteur (utilisateur) qui a publie le commentaire.
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    # Contenu texte saisi par l'utilisateur.
    content    = db.Column(db.Text, nullable=False)
    # Horodatage de creation en UTC.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relation pratique pour acceder rapidement a l'auteur depuis un commentaire.
    author = db.relationship('User', foreign_keys=[user_id],
                             backref='event_comments_written', lazy='select')

    def to_dict(self):
        """Retourne une representation JSON-friendly du commentaire."""
        result = {
            "id":         self.id,
            "event_id":   self.event_id,
            "user_id":    self.user_id,
            "content":    self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        # Ajoute des infos de profil si la relation auteur/profil est disponible.
        if self.author and self.author.profile:
            result['username']          = self.author.profile.username
            result['profile_image_url'] = self.author.profile.profile_image_url
        return result
