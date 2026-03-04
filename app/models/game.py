from app import db


class Game(db.Model):
    """Jeu de société disponible dans le catalogue BoardGame Hub."""

    __tablename__ = 'games'

    game_id           = db.Column(db.String(50), primary_key=True)
    name              = db.Column(db.String(200), nullable=False)
    description       = db.Column(db.Text)
    min_players       = db.Column(db.Integer, nullable=False)
    max_players       = db.Column(db.Integer, nullable=False)
    play_time_minutes = db.Column(db.Integer, nullable=False)
    image_url         = db.Column(db.String(255))

    def to_dict(self):
        """Sérialise le jeu en dictionnaire JSON-compatible."""
        return {
            "game_id":           self.game_id,
            "name":              self.name,
            "description":       self.description or '',
            "min_players":       self.min_players,
            "max_players":       self.max_players,
            "play_time_minutes": self.play_time_minutes,
            "image_url":         self.image_url,
        }
