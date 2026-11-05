from flask import Flask, jsonify
from app.repository import InMemoryExpenseRepository

def create_app():
    # Create and configure the Flask application
    app = Flask(__name__)

    # every time the app is created, a new instance of the repository is created
    app.extensions["repository"] = InMemoryExpenseRepository() # Use in-memory repository for now

    # Register the blueprint for the main routes
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
