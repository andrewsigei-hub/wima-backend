"""
Input validation utilities for forms and API requests.
"""
import re
from datetime import datetime


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_phone(phone):
    """
    Validate phone format (accepts Kenyan +254 and international formats).
    
    Args:
        phone: Phone string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # E.164 format: + followed by 7-15 digits
    pattern = r'^\+?[1-9]\d{6,14}$'
    return re.match(pattern, cleaned) is not None


def validate_date_format(date_str):
    """
    Validate ISO date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_date_not_past(date_str):
    """
    Ensure date is not in the past.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        bool: True if date is today or future, False otherwise
    """
    if not validate_date_format(date_str):
        return False
    
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    return date >= datetime.now().date()


def validate_check_dates(check_in, check_out):
    """
    Validate check-in and check-out dates.
    
    Args:
        check_in: Check-in date string (YYYY-MM-DD)
        check_out: Check-out date string (YYYY-MM-DD)
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not validate_date_format(check_in):
        return False, 'Invalid check-in date format. Use YYYY-MM-DD.'
    
    if not validate_date_format(check_out):
        return False, 'Invalid check-out date format. Use YYYY-MM-DD.'
    
    if not validate_date_not_past(check_in):
        return False, 'Check-in date cannot be in the past.'
    
    check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
    
    if check_out_date <= check_in_date:
        return False, 'Check-out date must be after check-in date.'
    
    return True, None


def validate_guest_count(guests, max_capacity=20):
    """
    Validate guest count.
    
    Args:
        guests: Number of guests
        max_capacity: Maximum allowed guests
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        guests = int(guests)
        return 1 <= guests <= max_capacity
    except (TypeError, ValueError):
        return False


def validate_inquiry_type(inquiry_type):
    """
    Validate inquiry type is one of the allowed values.
    
    Args:
        inquiry_type: Type string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    allowed_types = ['booking', 'event', 'general']
    return inquiry_type in allowed_types


def validate_event_type(event_type):
    """
    Validate event type is one of the allowed values.
    
    Args:
        event_type: Event type string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    allowed_types = ['wedding', 'corporate', 'birthday', 'reunion', 'graduation', 'other']
    return event_type in allowed_types


def sanitize_string(value, max_length=500):
    """
    Sanitize a string input by stripping whitespace and limiting length.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized string
    """
    if not value or not isinstance(value, str):
        return ''
    
    return value.strip()[:max_length]


def validate_required_fields(data, required_fields):
    """
    Check that all required fields are present and non-empty.
    
    Args:
        data: Dictionary of form data
        required_fields: List of required field names
        
    Returns:
        tuple: (is_valid: bool, missing_fields: list)
    """
    missing = []
    
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    
    return len(missing) == 0, missing