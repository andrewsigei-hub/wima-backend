"""
Inquiry model for room booking inquiries.
"""
from datetime import datetime
from app import db
from app.models.mixins import SerializerMixin


class Inquiry(db.Model, SerializerMixin):
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
        data = super().to_dict()

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
