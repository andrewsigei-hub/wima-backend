"""
Authentication utilities - JWT token handling and decorators.
"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import User


def generate_token(user, expires_in=24):
    """
    Generate a JWT token for authenticated user.
    
    Args:
        user: User model instance
        expires_in: Token validity in hours (default 24)
    
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=expires_in),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def decode_token(token):
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Token payload if valid
        None: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        current_app.logger.warning('Token expired')
        return None
    except jwt.InvalidTokenError as e:
        current_app.logger.warning(f'Invalid token: {str(e)}')
        return None


def get_current_user():
    """
    Get the current authenticated user from the request.
    
    Returns:
        User: User model instance if authenticated
        None: If not authenticated
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    payload = decode_token(token)
    
    if not payload:
        return None
    
    user = User.query.get(payload['user_id'])
    
    if not user or not user.is_active:
        return None
    
    return user


def require_auth(f):
    """
    Decorator to require authentication for a route.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'error_type': 'unauthorized'
            }), 401
        
        # Add user to kwargs so route can access it
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """
    Decorator to require admin role for a route.
    
    Usage:
        @app.route('/admin-only')
        @require_admin
        def admin_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'error_type': 'unauthorized'
            }), 401
        
        if not user.is_admin():
            current_app.logger.warning(f'User {user.email} attempted admin access')
            return jsonify({
                'success': False,
                'error': 'Admin privileges required',
                'error_type': 'forbidden'
            }), 403
        
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    
    return decorated_function


def require_manager(f):
    """
    Decorator to require manager or admin role for a route.
    
    Usage:
        @app.route('/manager-route')
        @require_manager
        def manager_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'error_type': 'unauthorized'
            }), 401
        
        if not user.is_manager_or_above():
            current_app.logger.warning(f'User {user.email} attempted manager access')
            return jsonify({
                'success': False,
                'error': 'Manager privileges required',
                'error_type': 'forbidden'
            }), 403
        
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    
    return decorated_function