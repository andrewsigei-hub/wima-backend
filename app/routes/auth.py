"""
Authentication routes - Login, logout, and user management.
"""
from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models.user import User
from app.utils.auth import generate_token, require_auth, require_admin
from app.utils.validators import validate_email, validate_required_fields, sanitize_string
from app.utils.errors import ValidationError
from app.utils.rate_limit import limiter

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    Authenticate user and return JWT token.
    
    Expected JSON:
        {
            "email": "admin@wimaserenity.com",
            "password": "securepassword"
        }
    
    Returns:
        JSON with token on success, error on failure
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError('No data provided')
        
        # Validate required fields
        is_valid, missing = validate_required_fields(data, ['email', 'password'])
        if not is_valid:
            raise ValidationError(f'Missing required fields: {", ".join(missing)}')
        
        email = sanitize_string(data['email'], max_length=100).lower()
        password = data['password']  # Don't sanitize password
        
        # Validate email format
        if not validate_email(email):
            raise ValidationError('Invalid email format')
        
        # Find user
        user = User.get_by_email(email)
        
        if not user or not user.check_password(password):
            current_app.logger.warning(f'Failed login attempt for: {email}')
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Check if user is active
        if not user.is_active:
            current_app.logger.warning(f'Inactive user login attempt: {email}')
            return jsonify({
                'success': False,
                'error': 'Account is deactivated. Contact administrator.'
            }), 401
        
        # Generate token
        token = generate_token(user)
        
        # Update last login
        user.update_last_login()
        
        current_app.logger.info(f'User logged in: {email}')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except ValidationError:
        raise
    except Exception as e:
        current_app.logger.error(f'Login error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Login failed. Please try again.'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user_info(current_user):
    """
    Get current authenticated user's information.
    
    Returns:
        JSON with user details
    """
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password(current_user):
    """
    Change current user's password.
    
    Expected JSON:
        {
            "current_password": "oldpassword",
            "new_password": "newpassword"
        }
    
    Returns:
        JSON success or error
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError('No data provided')
        
        # Validate required fields
        is_valid, missing = validate_required_fields(data, ['current_password', 'new_password'])
        if not is_valid:
            raise ValidationError(f'Missing required fields: {", ".join(missing)}')
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 400
        
        # Validate new password strength
        if len(new_password) < 8:
            raise ValidationError('New password must be at least 8 characters long')
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        current_app.logger.info(f'Password changed for user: {current_user.email}')
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Password change error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to change password'
        }), 500


@auth_bp.route('/users', methods=['POST'])
@require_admin
def create_user(current_user):
    """
    Create a new admin user (admin only).
    
    Expected JSON:
        {
            "email": "newuser@wimaserenity.com",
            "password": "securepassword",
            "name": "New User",
            "role": "staff"
        }
    
    Returns:
        JSON with created user details
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError('No data provided')
        
        # Validate required fields
        is_valid, missing = validate_required_fields(data, ['email', 'password', 'name'])
        if not is_valid:
            raise ValidationError(f'Missing required fields: {", ".join(missing)}')
        
        email = sanitize_string(data['email'], max_length=100).lower()
        name = sanitize_string(data['name'], max_length=100)
        password = data['password']
        role = sanitize_string(data.get('role', 'staff'), max_length=20)
        
        # Validate email format
        if not validate_email(email):
            raise ValidationError('Invalid email format')
        
        # Check if email already exists
        if User.get_by_email(email):
            raise ValidationError('Email already registered')
        
        # Validate password strength
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        # Validate role
        if role not in User.ROLES:
            raise ValidationError(f'Invalid role. Must be one of: {", ".join(User.ROLES)}')
        
        # Create user
        user = User.create_user(email=email, password=password, name=name, role=role)
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f'New user created: {email} by {current_user.email}')
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'User creation error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to create user'
        }), 500


@auth_bp.route('/users', methods=['GET'])
@require_admin
def list_users(current_user):
    """
    List all users (admin only).
    
    Returns:
        JSON with list of users
    """
    try:
        users = User.query.all()
        
        return jsonify({
            'success': True,
            'count': len(users),
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Error listing users: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to fetch users'
        }), 500