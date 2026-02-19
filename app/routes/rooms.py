"""
Rooms routes - API endpoints for room management.
"""
from flask import Blueprint, jsonify, request, current_app
from app.models.room import Room
from app import db
from app.utils.errors import NotFoundError, DatabaseError
from app.utils.validators import sanitize_string
from app.utils.rate_limit import limiter

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route('', methods=['GET'])
@limiter.limit("100 per hour")
def get_rooms():
    """
    Get all active rooms.
    
    Returns:
        JSON list of all active rooms with their details
    """
    try:
        rooms = Room.get_active_rooms()
        
        current_app.logger.info(f'Fetched {len(rooms)} active rooms')
        
        return jsonify({
            'success': True,
            'count': len(rooms),
            'rooms': [room.to_dict() for room in rooms]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Error fetching rooms: {str(e)}')
        raise DatabaseError('Failed to fetch rooms')


@rooms_bp.route('/featured', methods=['GET'])
@limiter.limit("100 per hour")
def get_featured_rooms():
    """
    Get featured rooms for homepage display.
    
    Returns:
        JSON list of featured rooms
    """
    try:
        rooms = Room.get_featured_rooms()
        
        current_app.logger.info(f'Fetched {len(rooms)} featured rooms')
        
        return jsonify({
            'success': True,
            'count': len(rooms),
            'rooms': [room.to_dict() for room in rooms]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Error fetching featured rooms: {str(e)}')
        raise DatabaseError('Failed to fetch featured rooms')


@rooms_bp.route('/<slug>', methods=['GET'])
@limiter.limit("100 per hour")
def get_room_by_slug(slug):
    """
    Get a single room by its slug.
    
    Args:
        slug: URL-friendly room identifier
    
    Returns:
        JSON room details or 404 if not found
    """
    try:
        # Sanitize slug input
        slug = sanitize_string(slug, max_length=100)
        
        if not slug:
            raise NotFoundError('Invalid room slug')
        
        room = Room.get_by_slug(slug)
        
        if not room:
            current_app.logger.info(f'Room not found: {slug}')
            raise NotFoundError(f'Room not found: {slug}')
        
        current_app.logger.info(f'Fetched room: {slug}')
        
        return jsonify({
            'success': True,
            'room': room.to_dict()
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f'Error fetching room {slug}: {str(e)}')
        raise DatabaseError('Failed to fetch room')


@rooms_bp.route('/type/<room_type>', methods=['GET'])
@limiter.limit("100 per hour")
def get_rooms_by_type(room_type):
    """
    Get all rooms of a specific type.
    
    Args:
        room_type: Type of room (premier, cottage, double, standard)
    
    Returns:
        JSON list of rooms matching the type
    """
    try:
        # Sanitize and validate room type
        room_type = sanitize_string(room_type, max_length=50)
        
        valid_types = ['premier', 'cottage', 'double', 'standard', 'deluxe', 'executive']
        if room_type not in valid_types:
            raise NotFoundError(f'Invalid room type. Must be one of: {", ".join(valid_types)}')
        
        rooms = Room.query.filter_by(type=room_type, is_active=True).all()
        
        current_app.logger.info(f'Fetched {len(rooms)} rooms of type: {room_type}')
        
        return jsonify({
            'success': True,
            'type': room_type,
            'count': len(rooms),
            'rooms': [room.to_dict() for room in rooms]
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f'Error fetching rooms by type {room_type}: {str(e)}')
        raise DatabaseError('Failed to fetch rooms')