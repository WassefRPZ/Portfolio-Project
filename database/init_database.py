import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'dev_user',
    'password': '',
    'database': 'boardgame_meetup'
}

def main():
    print("  Initialisation de la base de données...")
    
    # Connexion sans spécifier la database
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    
    # Supprimer et recréer la database
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")
    
    # Table users
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
    
    # Table games
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
    
    # Table events
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
    )
    """)
    
    # Table event_participants
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
    )
    """)
    
    # Table comments
    cursor.execute("""
    CREATE TABLE comments (
        comment_id VARCHAR(50) PRIMARY KEY,
        event_id VARCHAR(50) NOT NULL,
        user_id VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)
    
    # Table friendships
    cursor.execute("""
    CREATE TABLE friendships (
        user_id_1 VARCHAR(50) NOT NULL,
        user_id_2 VARCHAR(50) NOT NULL,
        action_user_id VARCHAR(50) NOT NULL,
        status ENUM('pending', 'accepted', 'declined', 'blocked') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id_1, user_id_2),
        CONSTRAINT chk_users_order CHECK (user_id_1 < user_id_2),
        FOREIGN KEY (user_id_1) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id_2) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (action_user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)
    
    # Table favorite_games
    cursor.execute("""
    CREATE TABLE favorite_games (
        user_id VARCHAR(50) NOT NULL,
        game_id VARCHAR(50) NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, game_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
    )
    """)
    
    # Données de test
    cursor.execute("""
    INSERT INTO users (user_id, username, email, password_hash, city, region, bio) VALUES
    ('usr_001', 'Nina', 'nina@test.com', 'password123', 'Saint Raphael', 'PACA', 'Passionnée de jeux'),
    ('usr_002', 'Wassef', 'wassef@test.com', 'password123', 'Frejus', 'PACA', 'Dev et gamer'),
    ('usr_003', 'Warren', 'warren@test.com', 'password123', 'Paris', 'IDF', 'Fan de stratégie')
    """)
    
    cursor.execute("""
    INSERT INTO games (game_id, name, description, min_players, max_players, play_time, image_url) VALUES
    ('game_001', 'Catan', 'Jeu de stratégie et de commerce', 3, 4, 90, 'https://example.com/catan.jpg'),
    ('game_002', 'Azul', 'Jeu de placement de tuiles', 2, 4, 45, 'https://example.com/azul.jpg'),
    ('game_003', '7 Wonders', 'Développement de civilisation', 2, 7, 30, 'https://example.com/7wonders.jpg')
    """)
    
    cursor.execute("""
    INSERT INTO events (event_id, creator_id, game_id, title, description, city, location_text, event_start, max_participants) VALUES
    ('evt_001', 'usr_001', 'game_001', 'Soirée Catan', 'On cherche 2 joueurs', 'Saint Raphael', 'Bar à Jeux', '2026-03-15 19:00:00', 4)
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Base de données créée avec succès!")

if __name__ == '__main__':
    main()