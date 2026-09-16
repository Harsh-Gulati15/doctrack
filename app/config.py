import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database — DATABASE_URL takes precedence over individual MYSQL_* vars
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL:
        # Render provides postgres:// but SQLAlchemy needs postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif DATABASE_URL.startswith('postgresql://'):
            DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
        MYSQL_DB = os.environ.get('MYSQL_DB', 'doctrack_db')
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }

    # File uploads — local fallback
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 20971520))
    ALLOWED_EXTENSIONS = {'pdf', 'jpeg', 'jpg', 'png'}

    # Google Cloud Storage (set to enable cloud file storage)
    GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    # Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # SLA & AI
    SLA_HOURS = int(os.environ.get('SLA_HOURS', 48))
    AI_CONFIDENCE_THRESHOLD = float(os.environ.get('AI_CONFIDENCE_THRESHOLD', 0.75))

    # Tesseract OCR (auto-detected on Linux/Docker; configurable for Windows)
    TESSERACT_PATH = os.environ.get('TESSERACT_PATH', 'tesseract')
    POPPLER_PATH = os.environ.get('POPPLER_PATH')

    # Session security
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_SAMESITE = 'Lax'
