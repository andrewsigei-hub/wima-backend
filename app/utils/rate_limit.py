"""
Rate limiting configuration to prevent abuse and spam.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Initialize limiter with remote address as key
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Use in-memory storage (use Redis in production for multiple workers)
)


def init_rate_limiter(app):
    """
    Initialize rate limiter with the Flask app.
    
    Args:
        app: Flask application instance
    """
    limiter.init_app(app)
    app.logger.info('✅ Rate limiter initialized')
    return limiter


# Decorator shortcuts for common limits
def limit_inquiries():
    """Strict limit for inquiry submissions (prevent spam)."""
    return limiter.limit("10 per hour", error_message="Too many inquiries. Please try again later.")


def limit_contact():
    """Strict limit for contact form (prevent spam)."""
    return limiter.limit("5 per hour", error_message="Too many messages. Please try again later.")


def limit_api_read():
    """Standard limit for read operations."""
    return limiter.limit("100 per hour", error_message="Too many requests. Please slow down.")