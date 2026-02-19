"""
Centralized error handling and HTTP exception responses.
"""
from flask import jsonify


class ValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
    
    def to_dict(self):
        return {
            'success': False,
            'error': self.message,
            'error_type': 'validation_error'
        }


class DatabaseError(Exception):
    """Raised when a database operation fails."""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
    
    def to_dict(self):
        return {
            'success': False,
            'error': 'Database operation failed. Please try again.',
            'error_type': 'database_error'
        }


class NotFoundError(Exception):
    """Raised when a resource is not found."""
    def __init__(self, message='Resource not found', status_code=404):
        self.message = message
        self.status_code = status_code
    
    def to_dict(self):
        return {
            'success': False,
            'error': self.message,
            'error_type': 'not_found'
        }


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, message='Too many requests. Please try again later.', status_code=429):
        self.message = message
        self.status_code = status_code
    
    def to_dict(self):
        return {
            'success': False,
            'error': self.message,
            'error_type': 'rate_limit_exceeded'
        }


def register_error_handlers(app):
    """Register all error handlers with the Flask app."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        app.logger.warning(f'Validation error: {error.message}')
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(error):
        app.logger.error(f'Database error: {error.message}')
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        app.logger.info(f'Not found: {error.message}')
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(RateLimitError)
    def handle_rate_limit_error(error):
        app.logger.warning(f'Rate limit exceeded: {error.message}')
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        app.logger.warning(f'Bad request: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'error_type': 'bad_request'
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        app.logger.info(f'Route not found: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'error_type': 'not_found'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        app.logger.warning(f'Method not allowed: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'error_type': 'method_not_allowed'
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f'Internal server error: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error. Please try again later.',
            'error_type': 'internal_error'
        }), 500
    
    app.logger.info('✅ Error handlers registered')