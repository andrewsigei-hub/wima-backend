"""
Inquiry model for room booking inquiries.
"""
from datetime import datetime
from app import db


class Inquiry(db.Model):
    """
    Represents a guest inquiry or booking request.
    """
    
    __tablename__ = 'inquiries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    inquiry_type = db.Column(db.String(50), nullable=False)  # booking, general
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    check_in = db.Column(db.Date, nullable=True)
    check_out = db.Column(db.Date, nullable=True)
    guests = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new, read, replied, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with room
    room = db.relationship('Room', back_populates='inquiries')
    
    def __repr__(self):
        return f'<Inquiry {self.id} - {self.name}>'
    
    def to_dict(self, include_room=True):
        """
        Convert inquiry object to dictionary for API responses.
        
        Args:
            include_room: Whether to include room details
        
        Returns:
            Dictionary representation of inquiry
        """
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'inquiry_type': self.inquiry_type,
            'room_id': self.room_id,
            'check_in': self.check_in.strftime('%d-%m-%Y') if self.check_in else None,
            'check_out': self.check_out.strftime('%d-%m-%Y') if self.check_out else None,
            'guests': self.guests,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.strftime('%d-%m-%Y') if self.created_at else None
        }
        
        if include_room and self.room:
            data['room'] = {
                'id': self.room.id,
                'name': self.room.name,
                'slug': self.room.slug,
                'type': self.room.type
            }
        
        return data
    
    @classmethod
    def get_recent_inquiries(cls, limit=50):
        """Get recent inquiries ordered by creation date."""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_status(cls, status):
        """Get inquiries by status."""
        return cls.query.filter_by(status=status).order_by(cls.created_at.desc()).all()
    
    def mark_as_read(self):
        """Mark inquiry as read."""
        self.status = 'read'
        db.session.commit()
    
    def mark_as_replied(self):
        """Mark inquiry as replied."""
        self.status = 'replied'
        db.session.commit()