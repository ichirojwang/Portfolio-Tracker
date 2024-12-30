import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('PG_FLASK_TRACKER')


class TestConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    SERVER_NAME = "localhost"
    WTF_CSRF_ENABLED = False
