"""
============================================
Board Game Meetup - Seed Database
============================================
"""
from app import create_app, db
from app.models import User, Game, Event, EventParticipant
import uuid
import bcrypt
from datetime import datetime, timedelta

# Initialiser l'application pour avoir accès au contexte et à la base de données
app = create_app()

def seed_database():
    with app.app_context():
        print("  Suppression des anciennes tables...")
        db.drop_all()
        
        print("  Création des nouvelles tables...")
        db.create_all()
        
        print(" Démarrage du remplissage (Seeding)...")

        # 1. CRÉATION DES UTILISATEURS
        print("   -> Création des utilisateurs")
        
        # Génère un hash de mot de passe commun pour les tests
        password = "password123"
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_nina = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            username="Nina",
            email="nina@example.com",
            password_hash=hashed_pw,
            city="Saint Raphael",
            region="PACA",
            bio="Joueuse passionnée de jeux de gestion.",
            profile_image_url="https://i.pravatar.cc/150?u=nina"
        )

        user_wassef = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            username="Wassef",
            email="wassef@example.com",
            password_hash=hashed_pw,
            city="Frejus",
            region="PACA",
            bio="Grand fan de Catan et de stratégie.",
            profile_image_url="https://i.pravatar.cc/150?u=wassef"
        )

        user_warren = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            username="Warren",
            email="warren@example.com",
            password_hash=hashed_pw,
            city="Paris",
            region="IDF",
            bio="Grand habituer des jeux de role.",
            profile_image_url="https://i.pravatar.cc/150?u=warren"
        )

        db.session.add_all([user_nina, user_wassef, user_warren])
        db.session.commit()

        # 2. CRÉATION DES JEUX
        print("   -> Création des jeux")

        game_catan = Game(
            game_id=f"game_{uuid.uuid4().hex[:8]}",
            name="Catan",
            description="Le jeu de commerce et de construction culte.",
            min_players=3,
            max_players=4,
            play_time=90,
            image_url="https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?auto=format&fit=crop&w=500&q=60"
        )

        game_dnd = Game(
            game_id=f"game_{uuid.uuid4().hex[:8]}",
            name="Dungeons & Dragons",
            description="Le jeu de rôle le plus connu au monde.",
            min_players=2,
            max_players=6,
            play_time=180,
            image_url="https://images.unsplash.com/photo-1612404730960-5c71579fca2c?auto=format&fit=crop&w=500&q=60"
        )

        game_uno = Game(
            game_id=f"game_{uuid.uuid4().hex[:8]}",
            name="Uno",
            description="Jeu de cartes rapide et amusant.",
            min_players=2,
            max_players=10,
            play_time=20,
            image_url="https://images.unsplash.com/photo-1605218427335-3a4dd884564e?auto=format&fit=crop&w=500&q=60"
        )

        db.session.add_all([game_catan, game_dnd, game_uno])
        db.session.commit()

        # 3. CRÉATION DES ÉVÉNEMENTS
        print("   -> Création des événements")

        # Événement 1 
        event_1 = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            creator_id=user_nina.user_id,
            game_id=game_catan.game_id,
            title="Soirée Catan détente",
            description="On cherche 2 joueurs pour une partie relax.",
            city="Saint Raphael",
            location_text="Le Bar à Jeux du Port",
            event_start=datetime.now() + timedelta(days=1, hours=2), # Demain
            max_participants=4,
            status='open'
        )

        # Événement 2 :
        event_2 = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            creator_id=user_wassef.user_id,
            game_id=game_dnd.game_id,
            title="Initiation D&D 5e",
            description="Débutants bienvenus pour une courte aventure.",
            city="Frejus",
            location_text="Chez Wassef",
            event_start=datetime.now() + timedelta(days=3, hours=5),
            max_participants=5,
            status='open'
        )

        db.session.add_all([event_1, event_2])
        db.session.commit()

        # 4. CRÉATION DES PARTICIPATIONS
        print("   -> Ajout des participants")

        part_1 = EventParticipant(
            participant_id=f"prt_{uuid.uuid4().hex[:8]}",
            event_id=event_1.event_id,
            user_id=user_wassef.user_id,
            status='confirmed'
        )

        part_2 = EventParticipant(
            participant_id=f"prt_{uuid.uuid4().hex[:8]}",
            event_id=event_1.event_id,
            user_id=user_warren.user_id,
            status='confirmed'
        )

        db.session.add_all([part_1, part_2])
        db.session.commit()

        print(" Base de données initialisée avec succès !")
        print("   Utilisateurs créés (Mot de passe: password123) :")
        print(f"   - {user_nina.email}")
        print(f"   - {user_wassef.email}")
        print(f"   - {user_warren.email}")

if __name__ == "__main__":
    seed_database()
