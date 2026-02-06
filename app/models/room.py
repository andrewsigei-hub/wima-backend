"""
Room model for WIMA Serenity Gardens.
"""
from datetime import datetime
from app import db
from app.models.mixins import SerializerMixin


class Room(db.Model, SerializerMixin):
    """
    Represents a guest room or accommodation at WIMA Serenity Gardens.
    """

    __tablename__ = 'rooms'

    serialize_exclude = ('is_active',)
    serialize_defaults = {
        'amenities': list,
        'images': list,
    }

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
        data = super().to_dict()

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
