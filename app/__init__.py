import os

from flask import Flask, jsonify
from app.repository import InMemoryExpenseRepository, PostgresExpenseRepository

def create_app():
    # Create and configure the Flask application
    app = Flask(__name__)

    # every time the app is created, a new instance of the repository is created
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        app.extensions["repository"] = PostgresExpenseRepository(database_url)
    else:
        app.extensions["repository"] = InMemoryExpenseRepository()

    # Register the blueprint for the main routes
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
