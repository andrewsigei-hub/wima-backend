"""
Main entry point for WIMA Serenity Gardens Flask application.
"""
import os
from app import create_app

# Create app instance with environment-based configuration
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )