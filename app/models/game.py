"""Modele Game : catalogue de jeux utilise par les evenements et les favoris."""

from app import db


class Game(db.Model):
    """Jeu de societe reference dans le catalogue de l'application."""

    __tablename__ = 'games'

    # Identifiant du jeu.
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Nom unique affiche dans les recherches et listes.
    name            = db.Column(db.String(200), nullable=False, unique=True)
    # Description libre (optionnelle).
    description     = db.Column(db.Text)
    # Bornes de joueurs supportees.
    min_players     = db.Column(db.Integer, nullable=False)
    max_players     = db.Column(db.Integer, nullable=False)
    # Duree moyenne d'une partie en minutes.
    play_time_minutes = db.Column('play_time_min', db.Integer, nullable=False)
    # URL d'illustration du jeu.
    image_url       = db.Column(db.String(255))

    def to_dict(self):
        """Serialise le jeu au format dictionnaire pour l'API."""
        return {
            "id":               self.id,
            "name":             self.name,
            "description":      self.description or '',
            "min_players":      self.min_players,
            "max_players":      self.max_players,
            "play_time_minutes": self.play_time_minutes,
            "image_url":        self.image_url,
        }
