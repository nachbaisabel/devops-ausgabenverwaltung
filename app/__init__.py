import os

from flask import Flask
from prometheus_client import CollectorRegistry
from prometheus_flask_exporter import PrometheusMetrics

from app.repository import InMemoryExpenseRepository, PostgresExpenseRepository


def create_app():
    # Create and configure the Flask application
    app = Flask(__name__)
    app.logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

    # Prometheus metrics
    # makes app metrics available at '/metrics'
    # CollectorRegistry prevents duplicate metric-registrations
    metrics = PrometheusMetrics(app, registry=CollectorRegistry())
    metrics.info(
        "expenses_info",
        "Application info",
        version=os.getenv("APP_VERSION", "0.0.0-dev"),
    )

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
