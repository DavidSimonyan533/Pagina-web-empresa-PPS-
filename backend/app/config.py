import os
from datetime import timedelta
from urllib.parse import quote_plus


def _database_uri():
    """Construye la URL de PostgreSQL a partir de las variables del .env."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    name = os.environ.get("POSTGRES_DB")
    host = os.environ.get("DB_HOST", "db")
    if not (user and password and name):
        return None
    return f"postgresql+psycopg2://{quote_plus(user)}:{quote_plus(password)}@{host}:5432/{name}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookies de sesión
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 64 * 1024  # Rechaza peticiones de más de 64 KB
    RATELIMIT_STORAGE_URI = "memory://"
