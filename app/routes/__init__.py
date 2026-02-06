"""
Routes package initialization.
Import all blueprints here.
"""
from app.routes.rooms import rooms_bp
from app.routes.inquiry import inquiries_bp
from app.routes.contact import contact_bp

__all__ = ['rooms_bp', 'inquiries_bp', 'contact_bp']