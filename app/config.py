"""
Configuration settings for different environments.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration with common settings."""
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@wimaserenitygardens.com')
    
    # Business contact info
    BUSINESS_EMAIL = os.getenv('BUSINESS_EMAIL', 'info@wimaserenitygardens.com')
    BUSINESS_PHONE = os.getenv('BUSINESS_PHONE', '+254700000000')
    BUSINESS_WHATSAPP = os.getenv('BUSINESS_WHATSAPP', '+254700000000')
    
    # Pagination
    ROOMS_PER_PAGE = 20
    INQUIRIES_PER_PAGE = 50


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://localhost/wima_serenity_dev'
    )
    SQLALCHEMY_ECHO = True  # Log SQL queries


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    
    # Render PostgreSQL databases use 'postgres://' but SQLAlchemy 1.4+ requires 'postgresql://'
    database_url = os.getenv('DATABASE_URL', '')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_ECHO = False
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/wima_serenity_test'
    WTF_CSRF_ENABLED = False