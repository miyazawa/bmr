from .bookmarks import bookmark_bp
from .auth import auth_bp
from .manage import manage_bp
from .tags import tag_bp
from .api import api_bp


def init_app(app):
    app.register_blueprint(bookmark_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(manage_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(api_bp)
