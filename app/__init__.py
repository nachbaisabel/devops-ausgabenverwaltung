from flask import Flask, jsonify

def create_app():
    # Create and configure the Flask application
    app = Flask(__name__)

    # Define a simple health check endpoint to verify that the application is running
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app
