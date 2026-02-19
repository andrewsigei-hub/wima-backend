"""
Inquiries routes - API endpoints for handling inquiries and bookings.
"""
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from app.models.inquiry import Inquiry
from app.models.event_inquiry import EventInquiry
from app.models.room import Room
from app import db
from app.services.email import send_inquiry_email, send_event_inquiry_email
from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_required_fields,
    validate_check_dates,
    validate_date_not_past,
    validate_guest_count,
    validate_inquiry_type,
    validate_event_type,
    sanitize_string
)
from app.utils.errors import ValidationError, DatabaseError
from app.utils.rate_limit import limiter

inquiries_bp = Blueprint('inquiries', __name__)


@inquiries_bp.route('', methods=['POST'])
@limiter.limit("10 per hour")
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
        
        if not data:
            raise ValidationError('No data provided')
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'inquiry_type', 'message']
        is_valid, missing = validate_required_fields(data, required_fields)
        
        if not is_valid:
            raise ValidationError(f'Missing required fields: {", ".join(missing)}')
        
        # Sanitize string inputs
        name = sanitize_string(data['name'], max_length=100)
        email = sanitize_string(data['email'], max_length=100)
        phone = sanitize_string(data['phone'], max_length=20)
        message = sanitize_string(data['message'], max_length=2000)
        inquiry_type = sanitize_string(data['inquiry_type'], max_length=50)
        
        # Validate email format
        if not validate_email(email):
            raise ValidationError('Invalid email format')
        
        # Validate phone format
        if not validate_phone(phone):
            raise ValidationError('Invalid phone format. Use format: +254700000000')
        
        # Validate inquiry type
        if not validate_inquiry_type(inquiry_type):
            raise ValidationError('Invalid inquiry type. Must be: booking, event, or general')
        
        # Validate message length
        if len(message) < 10:
            raise ValidationError('Message must be at least 10 characters long')
        
        # If room_id is provided, verify it exists
        room_id = data.get('room_id')
        if room_id:
            room = Room.query.get(room_id)
            if not room or not room.is_active:
                raise ValidationError('Invalid room ID')
        
        # Parse and validate dates if provided
        check_in = None
        check_out = None
        
        if data.get('check_in') and data.get('check_out'):
            is_valid, error_msg = validate_check_dates(data['check_in'], data['check_out'])
            if not is_valid:
                raise ValidationError(error_msg)
            
            check_in = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
            check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()
        
        # Validate guest count if provided
        guests = data.get('guests')
        if guests and not validate_guest_count(guests, max_capacity=10):
            raise ValidationError('Guest count must be between 1 and 10')
        
        # Create inquiry
        inquiry = Inquiry(
            name=name,
            email=email,
            phone=phone,
            inquiry_type=inquiry_type,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            guests=int(guests) if guests else None,
            message=message
        )
        
        db.session.add(inquiry)
        db.session.commit()
        
        current_app.logger.info(f'New inquiry created: {inquiry.id} from {email}')
        
        # Send email notification
        try:
            send_inquiry_email(inquiry)
            current_app.logger.info(f'Inquiry email sent for inquiry {inquiry.id}')
        except Exception as email_error:
            current_app.logger.error(f'Failed to send inquiry email: {str(email_error)}')
        
        return jsonify({
            'success': True,
            'message': 'Inquiry submitted successfully',
            'inquiry': inquiry.to_dict()
        }), 201
        
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating inquiry: {str(e)}')
        raise DatabaseError(f'Failed to create inquiry: {str(e)}')


@inquiries_bp.route('/event', methods=['POST'])
@limiter.limit("10 per hour")
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
        
        if not data:
            raise ValidationError('No data provided')
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'event_type', 'event_date', 'guest_count', 'message']
        is_valid, missing = validate_required_fields(data, required_fields)
        
        if not is_valid:
            raise ValidationError(f'Missing required fields: {", ".join(missing)}')
        
        # Sanitize string inputs
        name = sanitize_string(data['name'], max_length=100)
        email = sanitize_string(data['email'], max_length=100)
        phone = sanitize_string(data['phone'], max_length=20)
        message = sanitize_string(data['message'], max_length=2000)
        event_type = sanitize_string(data['event_type'], max_length=50)
        venue_preference = sanitize_string(data.get('venue_preference', ''), max_length=50)
        
        # Validate email format
        if not validate_email(email):
            raise ValidationError('Invalid email format')
        
        # Validate phone format
        if not validate_phone(phone):
            raise ValidationError('Invalid phone format. Use format: +254700000000')
        
        # Validate event type
        if not validate_event_type(event_type):
            raise ValidationError('Invalid event type. Must be: wedding, corporate, birthday, reunion, graduation, or other')
        
        # Validate event date
        if not validate_date_not_past(data['event_date']):
            raise ValidationError('Event date must be today or in the future')
        
        event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
        
        # Validate guest count (events can have more guests)
        if not validate_guest_count(data['guest_count'], max_capacity=500):
            raise ValidationError('Guest count must be between 1 and 500')
        
        guest_count = int(data['guest_count'])
        
        # Validate message length
        if len(message) < 10:
            raise ValidationError('Message must be at least 10 characters long')
        
        # Create event inquiry
        event_inquiry = EventInquiry(
            name=name,
            email=email,
            phone=phone,
            event_type=event_type,
            event_date=event_date,
            guest_count=guest_count,
            venue_preference=venue_preference if venue_preference else None,
            message=message
        )
        
        db.session.add(event_inquiry)
        db.session.commit()
        
        current_app.logger.info(f'New event inquiry created: {event_inquiry.id} from {email}')
        
        # Send email notification
        try:
            send_event_inquiry_email(event_inquiry)
            current_app.logger.info(f'Event inquiry email sent for inquiry {event_inquiry.id}')
        except Exception as email_error:
            current_app.logger.error(f'Failed to send event inquiry email: {str(email_error)}')
        
        return jsonify({
            'success': True,
            'message': 'Event inquiry submitted successfully',
            'inquiry': event_inquiry.to_dict()
        }), 201
        
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating event inquiry: {str(e)}')
        raise DatabaseError(f'Failed to create event inquiry: {str(e)}')