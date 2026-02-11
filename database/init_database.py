"""
============================================
Board Game Meetup - Database
============================================
"""
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': '127.0.0.1',       # Adresse serveur
    'user': 'dev_user',            # Utilisateur
    'password': '',            # Mot de passe
    'database': 'boardgame_meetup'  # Nom de la base à créer
}

def create_connection():
    try:
        # On se connecte
        conn_config = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
        return mysql.connector.connect(**conn_config)
    except Error as e:
        print(f" Connection Error: {e}")
        return None

def main():
    connection = create_connection()
    if not connection: return

    cursor = connection.cursor()
    try:
        print(" Initialisation de la base de données...")
        
        # 1. Création de la base de données
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # 2. Création des tables
        
        # TABLE: Users
        print(" Table: users")
        cursor.execute("""
        CREATE TABLE users (
            user_id VARCHAR(50) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') DEFAULT 'user',
            city VARCHAR(100) NOT NULL,
            region VARCHAR(100),
            bio TEXT,
            profile_image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # TABLE: Games
        print(" Table: games")
        cursor.execute("""
        CREATE TABLE games (
            game_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            min_players INT NOT NULL,
            max_players INT NOT NULL,
            play_time INT NOT NULL,
            image_url VARCHAR(255)
        )""")
        
        # TABLE: Events
        print(" Table: events")
        cursor.execute("""
        CREATE TABLE events (
            event_id VARCHAR(50) PRIMARY KEY,
            creator_id VARCHAR(50) NOT NULL,
            game_id VARCHAR(50) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            city VARCHAR(100) NOT NULL,
            location_text VARCHAR(255) NOT NULL,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            event_start DATETIME NOT NULL, 
            max_participants INT NOT NULL,
            status ENUM('open', 'full', 'cancelled', 'completed') DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        )""")

        # TABLE: Event Participants
        print(" Table: event_participants")
        cursor.execute("""
        CREATE TABLE event_participants (
            participant_id VARCHAR(50) PRIMARY KEY,
            event_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            status ENUM('confirmed', 'waitlist', 'cancelled') DEFAULT 'confirmed',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE KEY unique_participation (event_id, user_id)
        )""")

        # TABLE: Comments
        print(" Table: comments")
        cursor.execute("""
        CREATE TABLE comments (
            comment_id VARCHAR(50) PRIMARY KEY,
            event_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")

        # TABLE: Friendships
        print(" Table: friendships")
        cursor.execute("""
        CREATE TABLE friendships (
             user_id_1 VARCHAR(50) NOT NULL,
            user_id_2 VARCHAR(50) NOT NULL,
            action_user_id VARCHAR(50) NOT NULL, -- INDISPENSABLE : Qui a fait la dernière action (demande/blocage)
             status ENUM('pending', 'accepted', 'declined', 'blocked') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
            PRIMARY KEY (user_id_1, user_id_2),
    
            -- Contrainte pour éviter les doublons A-B et B-A (tri alphabétique forcé)
            CONSTRAINT chk_users_order CHECK (user_id_1 < user_id_2),
    
            FOREIGN KEY (user_id_1) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id_2) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (action_user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")

        # Table Favorite Games 
        print(" Table: favorite_games")
        cursor.execute("""
        CREATE TABLE favorite_games (
            user_id VARCHAR(50) NOT NULL,
            game_id VARCHAR(50) NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, game_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
        )""")

        # Table Reviews
        print(" Table: reviews")
        cursor.execute("""
        CREATE TABLE reviews (
            review_id VARCHAR(50) PRIMARY KEY,
            event_id VARCHAR(50) NOT NULL,
            reviewer_id VARCHAR(50) NOT NULL,
            target_user_id VARCHAR(50), 
            rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
            FOREIGN KEY (reviewer_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (target_user_id) REFERENCES users(user_id) ON DELETE SET NULL
        )""")
        
        # TABLE: Notifications
        print(" Table: notifications")
        cursor.execute("""
        CREATE TABLE notifications (
            notification_id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            type VARCHAR(50) NOT NULL,
            message VARCHAR(255) NOT NULL,
            reference_id VARCHAR(50),
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")

        # 3. Insertion des données de test
        print(" Seeding data...")

        # Insert Users
        users_data = [
            ('usr_001', 'Nina', 'nina@ex.com', 'hash1', 'Saint Raphael', 'PACA', 'Bio de Nina'),
            ('usr_002', 'Wassef', 'wassef@ex.com', 'hash2', 'Frejus', 'PACA', 'Bio de Wassef'),
            ('usr_003', 'Warren', 'warren@ex.com', 'hash3', 'Paris', 'IDF', 'Bio de Warren')
        ]
        cursor.executemany("""
            INSERT INTO users (user_id, username, email, password_hash, city, region, bio) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, users_data)

        # Insert Games
        games_data = [
            ('game_cat_01', 'Catan', 'Le jeu de stratégie', 3, 4, 90, 'http://img/catan.jpg'),
            ('game_dnd_01', 'Dungeons & Dragons', 'Jeu de rôle', 2, 6, 180, 'http://img/dnd.jpg')
        ]
        cursor.executemany("""
            INSERT INTO games (game_id, name, description, min_players, max_players, play_time, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, games_data)

        # Insert Events
        events_data = [
            ('evt_001', 'usr_001', 'game_cat_01', 'Soirée Catan', 'On cherche 2 joueurs', 'Saint Raphael', 'Le Bar à Jeux', 43.42, 6.76, '2026-02-01 19:00:00', 4)
        ]
        cursor.executemany("""
            INSERT INTO events (event_id, creator_id, game_id, title, description, city, location_text, latitude, longitude, event_start, max_participants) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, events_data)

        connection.commit()
        print(" Base de données installée avec succès !")

    except Error as e:
        print(f" SQL Error: {e}")
        if connection:
            connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
