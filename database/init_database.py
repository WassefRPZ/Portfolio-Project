import mysql.connector
import uuid

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'dev_user',
    'password': 'dev123',
    'database': 'boardgame_meetup'
}

# 5 jeux populaires avec game_id fixe
POPULAR_GAMES = [
    ("clue_001", "Clue", "Jeu d'enquete et de deduction", 3, 6, 60),
    ("catan_001", "Catan", "Jeu de strategie et de commerce", 3, 4, 90),
    ("pandemic_001", "Pandemic", "Jeu cooperatif contre les maladies", 2, 4, 45),
    ("carcassonne_001", "Carcassonne", "Jeu de placement de tuiles medieval", 2, 5, 45),
    ("azul_001", "Azul", "Jeu de placement de tuiles", 2, 4, 45)
]

def main():
    print("Initialisation de la base de donnees...")
    
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")
    
    # Création de la table users
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
    )
    """)
    
    # Création de la table games
    cursor.execute("""
    CREATE TABLE games (
        game_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        min_players INT NOT NULL,
        max_players INT NOT NULL,
        play_time INT NOT NULL,
        image_url VARCHAR(255)
    )
    """)
    
    print("Tables creees")
    
    # Insertion des utilisateurs de test
    cursor.execute("""
    INSERT INTO users (user_id, username, email, password_hash, city, region, bio) VALUES
    ('usr_001', 'Nina', 'nina@test.com', 'scrypt:32768:8:1$fakehash1', 'Saint Raphael', 'PACA', 'Passionnee de jeux'),
    ('usr_002', 'Wassef', 'wassef@test.com', 'scrypt:32768:8:1$fakehash2', 'Frejus', 'PACA', 'Dev et gamer'),
    ('usr_003', 'Warren', 'warren@test.com', 'scrypt:32768:8:1$fakehash3', 'Paris', 'IDF', 'Fan de strategie')
    """)
    
    print("Ajout de 5 jeux populaires...")
    for game_id, name, description, min_p, max_p, time in POPULAR_GAMES:
        cursor.execute("""
            INSERT INTO games (game_id, name, description, min_players, max_players, play_time, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (game_id, name, description, min_p, max_p, time, f"https://via.placeholder.com/300x300?text={name.replace(' ', '+')}"))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("=" * 60)
    print("Base de donnees creee avec succes!")
    print(f"Total: 3 utilisateurs, 5 jeux")
    print("=" * 60)

if __name__ == '__main__':
    main()