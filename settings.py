import os
from pathlib import Path


class Config():
    """Dev config vars."""
    DEBUG = True
    TESTING = True
    DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    SECRET_KEY = 'dev'
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}/dev.db".format(
        Path.resolve(Path(__file__).parent / "instance"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # translations
    LANGUAGES = {
        'en': 'English',
        'ja': 'Japanese'
    }
    APPLICATION_ROOT = "/bmr"


class TestConfig():
    """Test config vars."""
    DEBUG = False
    TESTING = True
    SECRET_KEY = 'test'
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}/test.db".format(
        Path.resolve(Path(__file__).parent / "instance"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # translations
    LANGUAGES = {
        'en': 'English',
        'ja': 'Japanese'
    }
    ALEMBIC_INI = "{}/migrations/alembic.ini".format(
        Path.resolve(Path(__file__).parent))


settings = Config()
