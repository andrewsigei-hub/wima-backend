"""
Contact routes - API endpoints for general contact form.
"""
from flask import Blueprint, jsonify, request, current_app
from app.services.email import send_contact_email
from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_required_fields,
    sanitize_string
)
from app.utils.errors import ValidationError
from app.utils.rate_limit import limiter

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('', methods=['POST'])
@limiter.limit("5 per hour")
def submit_contact():
    """
    Submit a general contact form message.
    
    Expected JSON:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+254700000000",
            "subject": "General Inquiry",
            "message": "I have a question about..."
        }
    
    Returns:
        JSON success response or validation errors
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError('No data provided')
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        is_valid, missing = validate_required_fields(data, required_fields)
        
        if not is_valid:
            raise ValidationError(f'Missing required fields: {", ".join(missing)}')
        
        # Sanitize string inputs
        name = sanitize_string(data['name'], max_length=100)
        email = sanitize_string(data['email'], max_length=100)
        phone = sanitize_string(data.get('phone', ''), max_length=20)
        subject = sanitize_string(data.get('subject', 'General Inquiry'), max_length=200)
        message = sanitize_string(data['message'], max_length=2000)
        
        # Validate email format
        if not validate_email(email):
            raise ValidationError('Invalid email format')
        
        # Validate phone format if provided
        if phone and not validate_phone(phone):
            raise ValidationError('Invalid phone format. Use format: +254700000000')
        
        # Validate message length
        if len(message) < 10:
            raise ValidationError('Message must be at least 10 characters long')
        
        # Validate name length
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long')
        
        # Send email
        try:
            send_contact_email(
                name=name,
                email=email,
                phone=phone if phone else 'Not provided',
                subject=subject,
                message=message
            )
            
            current_app.logger.info(f'Contact email sent from {email}')
            
            return jsonify({
                'success': True,
                'message': 'Your message has been sent successfully. We will get back to you soon!'
            }), 200
            
        except Exception as email_error:
            current_app.logger.error(f'Failed to send contact email: {str(email_error)}')
            return jsonify({
                'success': False,
                'error': 'Failed to send message. Please try again or contact us directly.'
            }), 500
        
    except ValidationError:
        raise
    except Exception as e:
        current_app.logger.error(f'Error in contact form: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500