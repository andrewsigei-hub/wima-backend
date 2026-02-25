"""
Package model for WIMA Serenity Gardens.
Represents whole-property or multi-room packages.
"""
from datetime import datetime
from app import db
from app.models.mixins import SerializerMixin


class Package(db.Model, SerializerMixin):
    """
    Represents a bookable package — e.g. exclusive use of the full property.
    """

    __tablename__ = 'packages'

    serialize_exclude = ('is_active',)
    serialize_defaults = {
        'rooms_included': list,
        'amenities': list,
        'benefits': list,
        'images': list,
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    tagline = db.Column(db.String(200), nullable=True)
    short_description = db.Column(db.Text, nullable=False)
    long_description = db.Column(db.Text, nullable=True)

    # Pricing (KSh)
    price_per_night = db.Column(db.Integer, nullable=False)
    original_price = db.Column(db.Integer, nullable=True)  # Full price if booked separately

    # What's included
    rooms_included = db.Column(db.JSON, default=list)   # e.g. ["3x Standard Double", ...]
    capacity = db.Column(db.Integer, nullable=False)
    breakfast_included = db.Column(db.Boolean, default=True)
    amenities = db.Column(db.JSON, default=list)
    benefits = db.Column(db.JSON, default=list)         # Marketing bullet points

    # Media
    images = db.Column(db.JSON, default=list)

    # Status
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Package {self.name}>'

    def get_savings(self):
        """Calculate savings compared to booking rooms separately."""
        if self.original_price:
            return self.original_price - self.price_per_night
        return 0

    def get_discount_percentage(self):
        """Calculate discount percentage."""
        if self.original_price and self.original_price > 0:
            return round((1 - self.price_per_night / self.original_price) * 100)
        return 0

    def to_dict(self):
        data = super().to_dict()
        data['savings'] = self.get_savings()
        data['discount_percentage'] = self.get_discount_percentage()
        return data

    @classmethod
    def get_active_packages(cls):
        """Get all active packages."""
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def get_featured_packages(cls):
        """Get featured packages for homepage."""
        return cls.query.filter_by(is_active=True, is_featured=True).all()

    @classmethod
    def get_by_slug(cls, slug):
        """Get package by slug."""
        return cls.query.filter_by(slug=slug, is_active=True).first()
