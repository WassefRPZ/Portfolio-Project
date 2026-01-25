"""
============================================
Board Game Meetup - Database Setup
============================================
Script Python pour initialiser la base de données MySQL
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_sql_script():
    """Execute all SQL commands to initialize database"""
    connection = create_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Create database
        cursor.execute("DROP DATABASE IF EXISTS boardgame_meetup")
        cursor.execute("CREATE DATABASE boardgame_meetup CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE boardgame_meetup")
        
        # TABLE: users
        cursor.execute("""
        CREATE TABLE users (
            user_id VARCHAR(50) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            city VARCHAR(100) NOT NULL,
            bio TEXT,
            profile_image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_city (city)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Table 'users' créée")
        
        # TABLE: favorite_games
        cursor.execute("""
        CREATE TABLE favorite_games (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            game_id VARCHAR(50) NOT NULL,
            game_name VARCHAR(200) NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_game (user_id, game_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Table 'favorite_games' créée")
        
        # TABLE: events
        cursor.execute("""
        CREATE TABLE events (
            event_id VARCHAR(50) PRIMARY KEY,
            creator_id VARCHAR(50) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            game_id VARCHAR(50) NOT NULL,
            game_name VARCHAR(200) NOT NULL,
            city VARCHAR(100) NOT NULL,
            location VARCHAR(255) NOT NULL,
            event_date DATE NOT NULL,
            event_time TIME NOT NULL,
            max_participants INT NOT NULL,
            current_participants INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE,
            INDEX idx_city (city),
            INDEX idx_date (event_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Table 'events' créée")
        
        # TABLE: event_participants
        cursor.execute("""
        CREATE TABLE event_participants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            event_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE KEY unique_event_user (event_id, user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Table 'event_participants' créée")
        
        # TABLE: event_comments
        cursor.execute("""
        CREATE TABLE event_comments (
            comment_id VARCHAR(50) PRIMARY KEY,
            event_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            comment_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Table 'event_comments' créée")
        
        # TABLE: friendships
        cursor.execute("""
        CREATE TABLE friendships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            requester_id VARCHAR(50) NOT NULL,
            receiver_id VARCHAR(50) NOT NULL,
            status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (requester_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE KEY unique_friendship (requester_id, receiver_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Table 'friendships' créée")
        
        # TABLE: posts
        cursor.execute("""
        CREATE TABLE posts (
            post_id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Table 'posts' créée")
        
        # ============================================
        # INSERT SAMPLE DATA
        # ============================================
        
        # Add users
        users = [
            ('usr_001', 'Nina_Gamer', 'nina@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lNZfJ3fGZWVW', 'Paris', 'Passionnée de jeux de stratégie'),
            ('usr_002', 'Wassef_Player', 'wassef@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lNZfJ3fGZWVW', 'Paris', 'Fan de jeux japonais'),
            ('usr_003', 'Warren_Dice', 'warren@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lNZfJ3fGZWVW', 'Lyon', 'Amateur de jeux compétitifs')
        ]
        
        for user in users:
            cursor.execute("""
            INSERT INTO users (user_id, username, email, password_hash, city, bio)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, user)
        print("3 utilisateurs insérés")
        
        # Add favorite games
        games = [
            ('usr_001', 'TAAifFP590', 'Catan'),
            ('usr_001', 'AuBvbISHR6', '7 Wonders'),
            ('usr_002', 'yqR4PtpO8X', 'Pandemic')
        ]
        
        for user_id, game_id, game_name in games:
            cursor.execute("""
            INSERT INTO favorite_games (user_id, game_id, game_name)
            VALUES (%s, %s, %s)
            """, (user_id, game_id, game_name))
        print("3 jeux favoris insérés")
        
        # Add events
        events = [
            ('evt_001', 'usr_001', 'Soirée Catan entre amis', 'Soirée détendue autour de Catan. Tous niveaux bienvenus!', 'TAAifFP590', 'Catan', 'Paris', 'Café des Jeux, 15 rue du Jeu', '2026-02-01', '19:00:00', 4, 2),
            ('evt_002', 'usr_002', 'Session Pandemic', 'Partie coopérative de Pandemic.', 'yqR4PtpO8X', 'Pandemic', 'Paris', 'Appartement privé', '2026-02-05', '14:00:00', 4, 1)
        ]
        
        for event in events:
            cursor.execute("""
            INSERT INTO events (event_id, creator_id, title, description, game_id, game_name, city, location, event_date, event_time, max_participants, current_participants)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, event)
        print("2 événements insérés")
        
        # Add event participants
        participants = [
            ('evt_001', 'usr_001'),
            ('evt_001', 'usr_003'),
            ('evt_002', 'usr_002')
        ]
        
        for event_id, user_id in participants:
            cursor.execute("""
            INSERT INTO event_participants (event_id, user_id)
            VALUES (%s, %s)
            """, (event_id, user_id))
        print("Participants aux événements ajoutés")
        
        # Add a comment
        cursor.execute("""
        INSERT INTO event_comments (comment_id, event_id, user_id, comment_text)
        VALUES (%s, %s, %s, %s)
        """, ('cmt_001', 'evt_001', 'usr_003', "J'ai hâte!"))
        print("Commentaire ajouté")
        
        # Add friendships
        friendships = [
            ('usr_001', 'usr_002', 'accepted'),
            ('usr_002', 'usr_003', 'pending')
        ]
        
        for requester_id, receiver_id, status in friendships:
            cursor.execute("""
            INSERT INTO friendships (requester_id, receiver_id, status)
            VALUES (%s, %s, %s)
            """, (requester_id, receiver_id, status))
        print("Relations d'amitié ajoutées")
        
        # Add a post
        cursor.execute("""
        INSERT INTO posts (post_id, user_id, content)
        VALUES (%s, %s, %s)
        """, ('post_001', 'usr_001', 'Qui veut organiser une partie de Catan ce weekend?'))
        print("Publication ajoutée")
        
        # Commit changes
        connection.commit()
        print("\nBase de données initialisée avec succès!")
        return True
        
    except Error as e:
        print(f"Erreur lors de l'exécution du script SQL: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def main():
    """Main function"""
    print("Initialisation de la base de données...")
    if execute_sql_script():
        print("Opération réussie!")
    else:
        print("Erreur lors de l'initialisation")

if __name__ == "__main__":
    main()