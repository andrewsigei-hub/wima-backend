"""
EventInquiry model for event venue booking inquiries.
"""
from datetime import datetime
from app import db


class EventInquiry(db.Model):
    """
    Represents an inquiry for booking the event venue/field.
    """
    
    __tablename__ = 'event_inquiries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # wedding, corporate, birthday, etc.
    event_date = db.Column(db.Date, nullable=False)
    guest_count = db.Column(db.Integer, nullable=False)
    venue_preference = db.Column(db.String(50), nullable=True)  # field_1, field_2, either
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new, read, replied, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EventInquiry {self.id} - {self.event_type} on {self.event_date}>'
    
    def to_dict(self):
        """
        Convert event inquiry object to dictionary for API responses.
        
        Returns:
            Dictionary representation of event inquiry
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'event_type': self.event_type,
            'event_date': self.event_date.strftime('%d-%m-%Y') if self.event_date else None,
            'guest_count': self.guest_count,
            'venue_preference': self.venue_preference,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.strftime('%d-%m-%Y') if self.created_at else None
        }
    
    @classmethod
    def get_recent_inquiries(cls, limit=50):
        """Get recent event inquiries ordered by creation date."""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_status(cls, status):
        """Get event inquiries by status."""
        return cls.query.filter_by(status=status).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_event_date(cls, event_date):
        """Get event inquiries for a specific date."""
        return cls.query.filter_by(event_date=event_date).all()
    
    def mark_as_read(self):
        """Mark event inquiry as read."""
        self.status = 'read'
        db.session.commit()
    
    def mark_as_replied(self):
        """Mark event inquiry as replied."""
        self.status = 'replied'
        db.session.commit()