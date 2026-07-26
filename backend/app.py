"""
SQLyse backend entrypoint.

Run with:
    python -m backend.app
or, from inside the backend/ directory with the package installed on path:
    python app.py   (see README section for the exact recommended commands)

SECURITY NOTE: real scanner mode (USE_MOCK_SCANNER=false) sends live SQL
injection probe payloads to targetUrl. Only ever point it at applications you
own or are explicitly authorised to test (e.g. a local DVWA instance).
"""
import os

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=Config.CORS_ORIGINS)

    app.register_blueprint(api)

    @app.errorhandler(404)
    def not_found(_err):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_err):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(_err):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "1").strip().lower() in ("1", "true", "yes", "on")
    # Binds to localhost only by default - this is a local development server,
    # not something to expose on a network. Set HOST=0.0.0.0 explicitly if you
    # really need LAN access (e.g. testing from another device), and never do
    # so with USE_MOCK_SCANNER=false unless you understand the exposure.
    host = os.getenv("HOST", "127.0.0.1")
    app.run(debug=debug, host=host, port=5000)
