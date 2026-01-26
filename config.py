import os
from dotenv import load_dotenv

# Charge les variables du fichier
load_dotenv()

class Config:
    # Clé de sécurité pour les sessions
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    
    # Récupération des variables d'environnement
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = 'boardgame_meetup'

    # Construction de l'URI de connexion MySQL pour SQLAlchemy
    # Ajout de ?charset=utf8mb4 pour bien gérer les emojis et accents
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
    
    # Désactive le tracking des modifications pour économiser de la mémoire
    SQLALCHEMY_TRACK_MODIFICATIONS = False
