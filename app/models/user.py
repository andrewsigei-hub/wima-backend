"""
User model for admin authentication.
"""
from datetime import datetime
from app import db
import bcrypt


class User(db.Model):
    """Admin user model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='staff')  # admin, manager, staff
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Valid roles
    ROLES = ['admin', 'manager', 'staff']
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the user's password."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """Verify the password against the stored hash."""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def is_manager_or_above(self):
        """Check if user has manager or admin role."""
        return self.role in ['admin', 'manager']
    
    def to_dict(self):
        """Convert user to dictionary (excludes password)."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.strftime('%d-%m-%Y')
        }
    
    @classmethod
    def get_by_email(cls, email):
        """Find user by email address."""
        return cls.query.filter_by(email=email.lower()).first()
    
    @classmethod
    def create_user(cls, email, password, name, role='staff'):
        """Create a new user with hashed password."""
        if role not in cls.ROLES:
            raise ValueError(f'Invalid role. Must be one of: {", ".join(cls.ROLES)}')
        
        user = cls(
            email=email.lower(),
            name=name,
            role=role
        )
        user.set_password(password)
        return user