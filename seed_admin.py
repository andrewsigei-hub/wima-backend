"""
Seed script to create the initial admin user.
Run this once after setting up the database.
"""
from app import create_app, db
from app.models.user import User

def seed_admin():
    """Create the initial admin user."""
    app = create_app('development')
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.get_by_email('admin@wimaserenity.com')
        
        if existing_admin:
            print('Admin user already exists!')
            return
        
        # Create admin user
        admin = User.create_user(
            email='admin@wimaserenity.com',
            password='WimaAdmin2026!',  # Change this in production!
            name='WIMA Admin',
            role='admin'
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print('✅ Admin user created successfully!')
        print(f'   Email: admin@wimaserenity.com')
        print(f'   Password: WimaAdmin2026!')
        print(f'   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY IN PRODUCTION!')

if __name__ == '__main__':
    seed_admin()