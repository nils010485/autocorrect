from flask import Flask
from .routes import bp

def create_app():
    """Crée et configure l'application Flask."""
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
