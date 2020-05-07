from .task1 import task1_bp


def init_app(app):
    app.register_blueprint(task1_bp)
    