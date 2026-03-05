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

    SECRET_KEY               = _require("SECRET_KEY")
    JWT_SECRET_KEY           = _require("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    DB_HOST     = os.getenv("DB_HOST", "127.0.0.1")
    DB_USER     = _require("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME     = _require("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY", "")

    CLOUDINARY_CLOUD_NAME  = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY     = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET  = os.getenv("CLOUDINARY_API_SECRET", "")

    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "True").lower() != "false"
