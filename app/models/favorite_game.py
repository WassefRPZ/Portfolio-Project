from datetime import datetime, timezone
from app import db


class FavoriteGame(db.Model):
    """
    Table de liaison entre un utilisateur et ses jeux favoris.
    Clé primaire composite (user_id, game_id).
    """

    __tablename__ = 'favorite_games'

    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'),  primary_key=True)
    game_id  = db.Column(db.Integer, db.ForeignKey('games.id'),  primary_key=True)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relations pour accéder à l'objet User ou Game directement
    user = db.relationship('User', foreign_keys=[user_id],
                           backref='favorite_game_entries', lazy='select')
    game = db.relationship('Game', foreign_keys=[game_id],
                           backref='favorited_by',          lazy='select')
