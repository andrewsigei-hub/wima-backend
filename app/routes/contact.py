"""
Contact routes - API endpoints for general contact form.
"""
from flask import Blueprint, jsonify, request
from app.services.email import send_contact_email

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('', methods=['POST'])
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
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
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
        
        # Validate message length
        if len(data['message'].strip()) < 10:
            return jsonify({
                'success': False,
                'error': 'Message must be at least 10 characters long'
            }), 400
        
        # Send email
        try:
            send_contact_email(
                name=data['name'],
                email=data['email'],
                phone=data.get('phone', 'Not provided'),
                subject=data.get('subject', 'General Inquiry'),
                message=data['message']
            )
            
            return jsonify({
                'success': True,
                'message': 'Your message has been sent successfully. We will get back to you soon!'
            }), 200
            
        except Exception as email_error:
            print(f"Failed to send contact email: {str(email_error)}")
            return jsonify({
                'success': False,
                'error': 'Failed to send message. Please try again or contact us directly.'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500