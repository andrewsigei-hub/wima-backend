"""
Models package initialization.
Import all models here for easy access.
"""
from app.models.room import Room
from app.models.inquiry import Inquiry
from app.models.event_inquiry import EventInquiry
from app.models.user import User
from app.models.package import Package

__all__ = ['Room', 'Inquiry', 'EventInquiry', 'User', 'Package']