from app import create_app, db
from app.models import User, Game
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 1. Création des tables
    db.create_all()

    # CRÉATION DES ADMINS
    admins = [
        {"first_name": "Warren", "last_name": "Admin", "email": "warren@hb.com"},
        {"first_name": "Wassef", "last_name": "Admin", "email": "wassef@hb.com"},
        {"first_name": "Nina", "last_name": "Admin", "email": "nina@hb.com"}
    ]

    print("Gestion des Admins")
    for admin_data in admins:
        user = User.query.filter_by(email=admin_data["email"]).first()
        if not user:
            new_admin = User(
                first_name=admin_data["first_name"],
                last_name=admin_data["last_name"],
                email=admin_data["email"],
                password=generate_password_hash("password123"),
                is_admin=True
            )
            db.session.add(new_admin)
            print(f" Admin créé : {admin_data['first_name']} ({admin_data['email']})")
        else:
            print(f"ℹ  Admin existe déjà : {admin_data['first_name']}")

    # CRÉATION DES JEUX
    games_data = [
        {"title": "Catan", "description": "Commerce et stratégie.", "player_min": 3, "player_max": 4},
        {"title": "Dixit", "description": "Jeu d'imagination.", "player_min": 3, "player_max": 6},
        {"title": "Uno", "description": "Jeu de cartes rapide.", "player_min": 2, "player_max": 10},
        {"title": "Monopoly", "description": "Jeu immobilier classique.", "player_min": 2, "player_max": 8},
        {"title": "Ticket to Ride", "description": "Aventure ferroviaire.", "player_min": 2, "player_max": 5}
    ]

    print("\n Gestion des Jeux ")
    for game_info in games_data:
        game = Game.query.filter_by(title=game_info["title"]).first()
        if not game:
            new_game = Game(**game_info)
            db.session.add(new_game)
            print(f" Jeu ajouté : {game_info['title']}")
        else:
            print(f"  Jeu existe déjà : {game_info['title']}")

    # Validation finale en base de données
    db.session.commit()
    print("\n Initialisation de la base de données terminée avec succès.")
    