"""
Inquiries routes - API endpoints for handling inquiries and bookings.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models.inquiry import Inquiry
from app.models.event_inquiry import EventInquiry
from app.models.room import Room
from app import db
from app.services.email import send_inquiry_email, send_event_inquiry_email

inquiries_bp = Blueprint('inquiries', __name__)


@inquiries_bp.route('', methods=['POST'])
def create_inquiry():
    """
    Create a new room booking inquiry.
    
    Expected JSON:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+254700000000",
            "inquiry_type": "booking",
            "room_id": 1,
            "check_in": "2026-03-15",
            "check_out": "2026-03-17",
            "guests": 2,
            "message": "I would like to book this room..."
        }
    
    Returns:
        JSON success response or validation errors
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'inquiry_type', 'message']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate email format (basic)
        if '@' not in data['email']:
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # If room_id is provided, verify it exists
        if data.get('room_id'):
            room = Room.query.get(data['room_id'])
            if not room or not room.is_active:
                return jsonify({
                    'success': False,
                    'error': 'Invalid room ID'
                }), 400
        
        # Parse dates if provided
        check_in = None
        check_out = None
        if data.get('check_in'):
            try:
                check_in = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid check_in date format. Use YYYY-MM-DD'
                }), 400
        
        if data.get('check_out'):
            try:
                check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid check_out date format. Use YYYY-MM-DD'
                }), 400
        
        # Validate date logic
        if check_in and check_out and check_out <= check_in:
            return jsonify({
                'success': False,
                'error': 'Check-out date must be after check-in date'
            }), 400
        
        # Create inquiry
        inquiry = Inquiry(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            inquiry_type=data['inquiry_type'],
            room_id=data.get('room_id'),
            check_in=check_in,
            check_out=check_out,
            guests=data.get('guests'),
            message=data['message']
        )
        
        db.session.add(inquiry)
        db.session.commit()
        
        # Send email notification
        try:
            send_inquiry_email(inquiry)
        except Exception as email_error:
            # Log error but don't fail the request
            print(f"Failed to send email: {str(email_error)}")
        
        return jsonify({
            'success': True,
            'message': 'Inquiry submitted successfully',
            'inquiry': inquiry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@inquiries_bp.route('/event', methods=['POST'])
def create_event_inquiry():
    """
    Create a new event venue inquiry.
    
    Expected JSON:
        {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "+254700000000",
            "event_type": "wedding",
            "event_date": "2026-06-20",
            "guest_count": 150,
            "venue_preference": "field_1",
            "message": "I would like to book the venue for..."
        }
    
    Returns:
        JSON success response or validation errors
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'event_type', 'event_date', 'guest_count', 'message']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate email format
        if '@' not in data['email']:
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Parse event date
        try:
            event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid event_date format. Use YYYY-MM-DD'
            }), 400
        
        # Validate event date is in the future
        if event_date < datetime.now().date():
            return jsonify({
                'success': False,
                'error': 'Event date must be in the future'
            }), 400
        
        # Validate guest count
        try:
            guest_count = int(data['guest_count'])
            if guest_count <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Guest count must be a positive number'
            }), 400
        
        # Create event inquiry
        event_inquiry = EventInquiry(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            event_type=data['event_type'],
            event_date=event_date,
            guest_count=guest_count,
            venue_preference=data.get('venue_preference'),
            message=data['message']
        )
        
        db.session.add(event_inquiry)
        db.session.commit()
        
        # Send email notification
        try:
            send_event_inquiry_email(event_inquiry)
        except Exception as email_error:
            print(f"Failed to send email: {str(email_error)}")
        
        return jsonify({
            'success': True,
            'message': 'Event inquiry submitted successfully',
            'inquiry': event_inquiry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500