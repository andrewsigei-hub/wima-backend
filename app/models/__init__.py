"""
Models package initialization.
Import all models here for easy access.
"""
from app.models.room import Room
from app.models.inquiry import Inquiry
from app.models.event_inquiry import EventInquiry

__all__ = ['Room', 'Inquiry', 'EventInquiry']