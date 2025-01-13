import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY='sample_key'
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "models.db")

class LocalDevelopmentConfig(Config):
    DEBUG = True
