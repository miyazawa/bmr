import os
from flask import Flask, request
from flask_cors import CORS
from flask_babel import Babel
# from settings import settings


def create_app(config="settings.settings"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # enable cors
    CORS(app)

    # enable babel
    babel = Babel(app)
    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

    from . import routes, models  # , services
    models.init_app(app)
    routes.init_app(app)
    app.add_url_rule('/', endpoint='index')
    # services.init_app(app)

    # cli
    from . import cli
    cli.init_app(app)

    return app
