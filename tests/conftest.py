import pytest

from app import create_app

# fixture to create a test client for the Flask application
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()
