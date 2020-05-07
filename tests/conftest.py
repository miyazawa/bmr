import os, sys
import tempfile
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig

from bmr import create_app


@pytest.fixture(scope='session')
def app():
    app = create_app('settings.TestConfig')
    yield app


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
        session_factory = sessionmaker(bind=engine)
        _db = {
            'engine': engine,
            'session_factory': session_factory,
        }
        alembic_config = AlembicConfig(app.config['ALEMBIC_INI'])
        alembic_config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])
        alembic_upgrade(alembic_config, 'head')

        yield _db

        engine.dispose()


@pytest.fixture(scope='session')
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
