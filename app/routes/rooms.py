"""
Rooms routes - API endpoints for room management.
"""
from flask import Blueprint, jsonify, request
from app.models.room import Room
from app import db

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route('', methods=['GET'])
def get_rooms():
    """
    Get all active rooms.
    
    Returns:
        JSON list of all active rooms with their details
    """
    try:
        rooms = Room.get_active_rooms()
        return jsonify({
            'success': True,
            'count': len(rooms),
            'rooms': [room.to_dict() for room in rooms]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rooms_bp.route('/featured', methods=['GET'])
def get_featured_rooms():
    """
    Get featured rooms for homepage display.
    
    Returns:
        JSON list of featured rooms
    """
    try:
        rooms = Room.get_featured_rooms()
        return jsonify({
            'success': True,
            'count': len(rooms),
            'rooms': [room.to_dict() for room in rooms]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rooms_bp.route('/<slug>', methods=['GET'])
def get_room_by_slug(slug):
    """
    Get a single room by its slug.
    
    Args:
        slug: URL-friendly room identifier
    
    Returns:
        JSON room details or 404 if not found
    """
    try:
        room = Room.get_by_slug(slug)
        
        if not room:
            return jsonify({
                'success': False,
                'error': 'Room not found'
            }), 404
        
        return jsonify({
            'success': True,
            'room': room.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rooms_bp.route('/type/<room_type>', methods=['GET'])
def get_rooms_by_type(room_type):
    """
    Get all rooms of a specific type.
    
    Args:
        room_type: Type of room (premier, cottage, double, standard)
    
    Returns:
        JSON list of rooms matching the type
    """
    try:
        rooms = Room.query.filter_by(type=room_type, is_active=True).all()
        
        return jsonify({
            'success': True,
            'type': room_type,
            'count': len(rooms),
            'rooms': [room.to_dict() for room in rooms]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500