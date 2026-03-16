
"""
Modèle EventParticipant :
Représente l'association entre un utilisateur et un événement, ainsi que le statut de participation.
"""

from datetime import datetime, timezone
from app import db



class EventParticipant(db.Model):
    __tablename__ = 'event_participants'  # Nom de la table dans la base de données


    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Identifiant unique de la participation
    event_id  = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)  # Référence à l'événement
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)  # Référence à l'utilisateur
    status    = db.Column(db.Enum('confirmed', 'pending'), default='confirmed')  # Statut de participation
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Date d'inscription à l'événement


    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_event_user'),  # Unicité : un utilisateur ne peut participer qu'une fois à un événement
    )


    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        backref='participations',
        lazy='select'
    )  # Relation ORM vers l'utilisateur participant


    def to_dict(self):
        """
        Retourne un dictionnaire représentant la participation à l'événement.
        Inclut les informations principales et, si disponible, des détails sur l'utilisateur.
        """
        data = {
            "id":        self.id,  # Identifiant de la participation
            "event_id":  self.event_id,  # Identifiant de l'événement
            "user_id":   self.user_id,   # Identifiant de l'utilisateur
            "status":    self.status,    # Statut de participation
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,  # Date d'inscription
        }
        # Ajoute des informations utilisateur si la relation est chargée
        if self.user and self.user.profile:
            data["username"] = self.user.profile.username  # Nom d'utilisateur
            data["profile_image_url"] = self.user.profile.profile_image_url  # URL de l'avatar
            data["city"] = self.user.profile.city or ""  # Ville de l'utilisateur
        return data
