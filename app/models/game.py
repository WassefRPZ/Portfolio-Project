from app import db


class Game(db.Model):
    """Jeu de société disponible dans le catalogue BoardGame Hub."""

    __tablename__ = 'games'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name            = db.Column(db.String(200), nullable=False, unique=True)
    description     = db.Column(db.Text)
    min_players     = db.Column(db.Integer, nullable=False)
    max_players     = db.Column(db.Integer, nullable=False)
    play_time_minutes = db.Column('play_time_min', db.Integer, nullable=False)
    image_url       = db.Column(db.String(255))

    def to_dict(self):
        """Sérialise le jeu en dictionnaire JSON-compatible."""
        return {
            "id":               self.id,
            "name":             self.name,
            "description":      self.description or '',
            "min_players":      self.min_players,
            "max_players":      self.max_players,
            "play_time_minutes": self.play_time_minutes,
            "image_url":        self.image_url,
        }
