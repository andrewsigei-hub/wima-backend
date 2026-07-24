"""
Flask application factory for WIMA Serenity Gardens backend.
"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(config_name="development"):
    """
    Application factory pattern.

    Args:
        config_name: Configuration environment (development, production, testing)

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(f"app.config.{config_name.capitalize()}Config")

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Import models to register with SQLAlchemy
    from app.models import room, inquiry, event_inquiry, package

    # Initialize logging (do this early so other modules can use it)
    from app.utils.logger import configure_logging

    configure_logging(app)

    # Initialize error handlers
    from app.utils.errors import register_error_handlers

    register_error_handlers(app)

    # Initialize rate limiter
    from app.utils.rate_limit import init_rate_limiter

    init_rate_limiter(app)

    # Configure CORS
    # CORS_ORIGINS: comma-separated list of allowed frontend origins.
    # Falls back to local dev origins when unset.
    cors_origins = os.getenv("CORS_ORIGINS")
    allowed_origins = (
        [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
        if cors_origins
        else ["http://localhost:5173", "http://localhost:3000"]
    )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PATCH", "DELETE"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    # Register blueprints
    from app.routes.rooms import rooms_bp
    from app.routes.inquiries import inquiries_bp
    from app.routes.contact import contact_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.packages import packages_bp

    app.register_blueprint(rooms_bp, url_prefix="/api/rooms")
    app.register_blueprint(inquiries_bp, url_prefix="/api/inquiries")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(packages_bp, url_prefix="/api/packages")

    # Health check route
    @app.route("/api/health")
    def health_check():
        return {"status": "healthy", "service": "WIMA Serenity Gardens API"}, 200

    app.logger.info("🚀 WIMA Serenity Gardens API initialized successfully")

    return app
