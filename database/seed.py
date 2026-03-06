import sys
import os

# Permet d'executer ce script depuis le dossier database/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Profile, Game

app = create_app()

SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD")
if not SEED_ADMIN_PASSWORD:
    raise RuntimeError(
        "Variable d'environnement manquante : SEED_ADMIN_PASSWORD (vérifier le fichier .env)"
    )

with app.app_context():

    admins = [
        {"username": "WarrenAdmin", "email": "warren@hb.com", "city": "Paris"},
        {"username": "WassefAdmin", "email": "wassef@hb.com", "city": "Frejus"},
        {"username": "NinaAdmin",   "email": "nina@hb.com",   "city": "Marseille"},
    ]

    print("\n--- Gestion des Admins ---")
    for admin_data in admins:
        if not User.query.filter_by(email=admin_data["email"]).first():

            new_user = User(
                email=admin_data["email"],
                password_hash=generate_password_hash(SEED_ADMIN_PASSWORD),
                role='admin',
            )
            db.session.add(new_user)
            db.session.flush()

            new_profile = Profile(
                user_id=new_user.id,
                username=admin_data["username"],
                bio="Compte administrateur système",
                city=admin_data["city"],
                region='',
            )
            db.session.add(new_profile)
            print(f"  Admin créé : {admin_data['username']}")
        else:
            print(f"  Admin existe déjà : {admin_data['username']}")

    games_data = [
        {
            "name": "Catan",
            "description": "Commerce et stratégie.",
            "min_players": 3, "max_players": 4, "play_time_minutes": 90,
        },
        {
            "name": "Dixit",
            "description": "Jeu d'imagination.",
            "min_players": 3, "max_players": 6, "play_time_minutes": 30,
        },
        {
            "name": "Uno",
            "description": "Jeu de cartes rapide.",
            "min_players": 2, "max_players": 10, "play_time_minutes": 15,
        },
        {
            "name": "Monopoly",
            "description": "Jeu immobilier classique.",
            "min_players": 2, "max_players": 8, "play_time_minutes": 120,
        },
        {
            "name": "Ticket to Ride",
            "description": "Aventure ferroviaire.",
            "min_players": 2, "max_players": 5, "play_time_minutes": 60,
        },
    ]

    print("\n--- Gestion des Jeux ---")
    for game_info in games_data:
        if not Game.query.filter_by(name=game_info["name"]).first():
            new_game = Game(
                name=game_info["name"],
                description=game_info["description"],
                min_players=game_info["min_players"],
                max_players=game_info["max_players"],
                play_time_minutes=game_info["play_time_minutes"],
                image_url=None,
            )
            db.session.add(new_game)
            print(f"  Jeu ajouté : {game_info['name']}")
        else:
            print(f"  Jeu existe déjà : {game_info['name']}")

    # COMMIT
    try:
        db.session.commit()
        print("\nSUCCESS: Base de données initialisée.")
    except Exception as e:
        db.session.rollback()
        print(f"\nERROR: Impossible d'enregistrer : {e}")
