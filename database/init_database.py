"""
============================================
Board Game Meetup - Database
============================================
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

def create_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Error: {e}")
        return None

def execute_sql_script():
    connection = create_connection()
    if not connection: return False
    
    cursor = connection.cursor()
    try:
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")
    
        
        cursor.execute("""
        CREATE TABLE event_participants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            event_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE KEY unique_event_user (event_id, user_id)
        )""")

        cursor.execute("""
        CREATE TABLE posts (
            post_id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")

        # 5. comments
        cursor.execute("""
        CREATE TABLE comments (
            comment_id INT AUTO_INCREMENT PRIMARY KEY,
            event_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )""")

        # Users
        users = [
            ('usr_001', 'Nina', 'nina@ex.com', 'hash1', 'Saint Raphael', 'Bio'),
            ('usr_002', 'Wassef', 'wassef@ex.com', 'hash2', 'Frejus', 'Bio'),
            ('usr_003', 'Warren', 'warren@ex.com', 'hash3', 'Paris', 'Bio')
        ]
    
        for u in users:
            cursor.execute("INSERT INTO users (user_id, username, email, password_hash, city, bio) VALUES (%s, %s, %s, %s, %s, %s)", u)

        # Events
        events = [
            ('evt_001', 'usr_001', 'Catan Night', 'Fun', 'game_1', 'Catan', 'Paris', 'Bar', '2026-02-01', '19:00:00', 4)
        ]
        for e in events:
            cursor.execute("INSERT INTO events (event_id, creator_id, title, description, game_id, game_name, city, location, event_date, event_time, max_participants) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", e)

        connection.commit()
        print
        return True
    except Error as e:
        print(f"SQL Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
