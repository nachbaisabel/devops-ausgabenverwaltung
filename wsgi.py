"""WSGI entrypoint. Gunicorn imports the module-level `app` object.

Production: `gunicorn --bind 0.0.0.0:8000 wsgi:app`
"""

from app import create_app

app = create_app()


if __name__ == "__main__":
    # Development only. Gunicorn serves the app in the container.
    app.run(host="127.0.0.1", port=8000, debug=True)

# to run the app in dev mode
# python wsgi.py
# open http://127.0.0.1:8000/health
