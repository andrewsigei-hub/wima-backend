"""
Room model for WIMA Serenity Gardens.
"""
from datetime import datetime
from app import db


class Room(db.Model):
    """
    Represents a guest room or accommodation at WIMA Serenity Gardens.
    """
    
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)  # premier, cottage, double, standard
    description = db.Column(db.Text, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)  # Max guests
    price_per_night = db.Column(db.Integer, nullable=False)  # In KSh
    breakfast_included = db.Column(db.Boolean, default=True)
    amenities = db.Column(db.JSON, default=list)  # ["WiFi", "En-suite", "TV"]
    images = db.Column(db.JSON, default=list)  # Array of image URLs
    is_featured = db.Column(db.Boolean, default=False)  # Show on homepage
    is_active = db.Column(db.Boolean, default=True)  # Soft delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with inquiries
    inquiries = db.relationship('Inquiry', back_populates='room', lazy='dynamic')
    
    def __repr__(self):
        return f'<Room {self.name}>'
    
    def to_dict(self, include_inquiries=False):
        """
        Convert room object to dictionary for API responses.
        
        Args:
            include_inquiries: Whether to include related inquiries
        
        Returns:
            Dictionary representation of room
        """
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'type': self.type,
            'description': self.description,
            'capacity': self.capacity,
            'price_per_night': self.price_per_night,
            'breakfast_included': self.breakfast_included,
            'amenities': self.amenities or [],
            'images': self.images or [],
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_inquiries:
            data['inquiries_count'] = self.inquiries.count()
        
        return data
    
    @staticmethod
    def create_slug(name):
        """
        Generate URL-friendly slug from room name.
        
        Args:
            name: Room name
        
        Returns:
            URL-safe slug
        """
        return name.lower().replace(' ', '-').replace('/', '-')
    
    @classmethod
    def get_active_rooms(cls):
        """Get all active (non-deleted) rooms."""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_featured_rooms(cls):
        """Get featured rooms for homepage."""
        return cls.query.filter_by(is_active=True, is_featured=True).all()
    
    @classmethod
    def get_by_slug(cls, slug):
        """Get room by slug."""
        return cls.query.filter_by(slug=slug, is_active=True).first()