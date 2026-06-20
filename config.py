import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


def get_database_url():
    """Handle Railway's postgres:// vs SQLAlchemy's postgresql://"""
    url = os.environ.get('DATABASE_URL') or \
          'sqlite:///' + os.path.join(basedir, 'transport.db')
    # Railway gives postgres:// but SQLAlchemy needs postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bus-transport-secret-key-2024-change-in-production'
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'images', 'uploads')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
