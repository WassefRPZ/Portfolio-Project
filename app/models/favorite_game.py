"""Modele FavoriteGame : table pivot utilisateur-jeu pour les favoris."""

from datetime import datetime, timezone
from app import db


class FavoriteGame(db.Model):
    """Table pivot des jeux marques en favoris par les utilisateurs."""

    __tablename__ = 'favorite_games'

    # Cle composite: un favori est unique pour un couple (utilisateur, jeu).
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'),  primary_key=True)
    game_id  = db.Column(db.Integer, db.ForeignKey('games.id'),  primary_key=True)
    # Date d'ajout au moment du clic favori.
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relations utilitaires pour naviguer des favoris vers User et Game.
    user = db.relationship('User', foreign_keys=[user_id],
                           backref='favorite_game_entries', lazy='select')
    game = db.relationship('Game', foreign_keys=[game_id],
                           backref='favorited_by',          lazy='select')
