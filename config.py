"""Configuration centrale de l'application.

Charge les variables d'environnement, valide les valeurs obligatoires
et construit la configuration Flask/SQLAlchemy.
"""

import os
from dotenv import load_dotenv
from datetime import timedelta


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _require(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variable d'environnement manquante : {name} (vérifier le fichier .env)")
    return value


class Config:
    """
    Classe de configuration pour Flask.
    
    Tous les paramètres Flaskse définissent en majuscules
    et sont lus via app.config.from_object(Config).
    
    Sections:
    - Sécurité: SECRET_KEY, JWT_*
    - Base de données: SQLALCHEMY_*
    - CORS: CORS_ORIGINS
    - Intégrations: OPENCAGE_API_KEY, CLOUDINARY_*
    - Rate limiting: RATELIMIT_ENABLED
    """

    # ═══════════════════════════════════════════════════════════════════════
    # SÉCURITÉ: Authentification et signatures
    # ═══════════════════════════════════════════════════════════════════════
    SECRET_KEY               = _require("SECRET_KEY")  # Clé pour chiffrer les sessions
    JWT_SECRET_KEY           = _require("JWT_SECRET_KEY")  # Clé pour signer les tokens JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Durée de vie des tokens: 24 heures

    # ═══════════════════════════════════════════════════════════════════════
    # BASE DE DONNÉES: Connexion MySQL
    # ═══════════════════════════════════════════════════════════════════════
    DB_HOST     = os.getenv("DB_HOST", "127.0.0.1")  # Serveur MySQL (défaut: localhost)
    DB_USER     = _require("DB_USER")  # Utilisateur MySQL (obligatoire)
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")  # Mot de passe (défaut: vide)
    DB_NAME     = _require("DB_NAME")  # Nom de la BD (obligatoire)

    # URI de connexion MySQL pour SQLAlchemy
    # Format: mysql+mysqlconnector://user:password@host/database
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Désactive les avertissements de modifcation

    # ═══════════════════════════════════════════════════════════════════════
    # CORS: Autorisations croisées entre domaines
    # ═══════════════════════════════════════════════════════════════════════
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # Origines autorisées (défaut: qui conque)

    # ═══════════════════════════════════════════════════════════════════════
    # INTÉGRATIONS EXTERNES
    # ═══════════════════════════════════════════════════════════════════════
    OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY", "")  # Clé pour géocodage d'adresses

    # Clés Cloudinary pour upload et stockage d'images
    CLOUDINARY_CLOUD_NAME  = os.getenv("CLOUDINARY_CLOUD_NAME", "")  # Nom du compte cloud
    CLOUDINARY_API_KEY     = os.getenv("CLOUDINARY_API_KEY", "")  # Clé API
    CLOUDINARY_API_SECRET  = os.getenv("CLOUDINARY_API_SECRET", "")  # Clé secrète

    # ═══════════════════════════════════════════════════════════════════════
    # RATE LIMITING: Protection contre les abus
    # ═══════════════════════════════════════════════════════════════════════
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "True").lower() != "false"
