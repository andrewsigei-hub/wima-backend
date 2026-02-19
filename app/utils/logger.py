"""
Structured logging configuration for production.
"""
import logging
import logging.handlers
import os


def configure_logging(app):
    """Configure structured logging for all environments."""
    
    # Remove default Flask logger handlers
    app.logger.handlers.clear()
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # File handler for all logs (rotates at 10MB, keeps 10 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/wima_serenity.log',
        maxBytes=10485760,
        backupCount=10
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Set log level based on environment
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    app.logger.info('✅ Logging configured successfully')
    
    return app.logger