"""
Admin routes - API endpoints for managing inquiries, event inquiries, and dashboard.
"""
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
from app import db
from app.models.inquiry import Inquiry
from app.models.event_inquiry import EventInquiry
from app.models.room import Room
from app.utils.auth import require_auth, require_admin, require_manager
from app.utils.validators import validate_required_fields, sanitize_string
from app.utils.errors import ValidationError, NotFoundError, DatabaseError
from app.utils.rate_limit import limiter

admin_bp = Blueprint('admin', __name__)


# ==================== DASHBOARD ====================

@admin_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard_stats(current_user):
    """
    Get dashboard statistics overview.
    
    Returns:
        JSON with inquiry counts, recent activity, etc.
    """
    try:
        # Inquiry stats
        total_inquiries = Inquiry.query.count()
        new_inquiries = Inquiry.query.filter_by(status='new').count()
        read_inquiries = Inquiry.query.filter_by(status='read').count()
        replied_inquiries = Inquiry.query.filter_by(status='replied').count()
        
        # Event inquiry stats
        total_event_inquiries = EventInquiry.query.count()
        new_event_inquiries = EventInquiry.query.filter_by(status='new').count()
        
        # Room stats
        total_rooms = Room.query.filter_by(is_active=True).count()
        featured_rooms = Room.query.filter_by(is_active=True, is_featured=True).count()
        
        # Recent inquiries (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_inquiries = Inquiry.query.filter(Inquiry.created_at >= week_ago).count()
        recent_event_inquiries = EventInquiry.query.filter(EventInquiry.created_at >= week_ago).count()
        
        current_app.logger.info(f'Dashboard accessed by {current_user.email}')
        
        return jsonify({
            'success': True,
            'stats': {
                'inquiries': {
                    'total': total_inquiries,
                    'new': new_inquiries,
                    'read': read_inquiries,
                    'replied': replied_inquiries,
                    'last_7_days': recent_inquiries
                },
                'event_inquiries': {
                    'total': total_event_inquiries,
                    'new': new_event_inquiries,
                    'last_7_days': recent_event_inquiries
                },
                'rooms': {
                    'total': total_rooms,
                    'featured': featured_rooms
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Dashboard error: {str(e)}')
        raise DatabaseError('Failed to fetch dashboard stats')


# ==================== INQUIRIES ====================

@admin_bp.route('/inquiries', methods=['GET'])
@require_auth
def get_all_inquiries(current_user):
    """
    Get all inquiries with optional filtering.
    
    Query params:
        - status: Filter by status (new, read, replied, archived)
        - type: Filter by inquiry type (booking, event, general)
        - limit: Number of results (default 50)
        - offset: Pagination offset (default 0)
    
    Returns:
        JSON list of inquiries
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        inquiry_type = request.args.get('type')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = Inquiry.query
        
        if status:
            query = query.filter_by(status=status)
        
        if inquiry_type:
            query = query.filter_by(inquiry_type=inquiry_type)
        
        # Order by newest first
        query = query.order_by(Inquiry.created_at.desc())
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        inquiries = query.limit(limit).offset(offset).all()
        
        current_app.logger.info(f'Inquiries listed by {current_user.email}')
        
        return jsonify({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'count': len(inquiries),
            'inquiries': [inquiry.to_dict() for inquiry in inquiries]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Error listing inquiries: {str(e)}')
        raise DatabaseError('Failed to fetch inquiries')


@admin_bp.route('/inquiries/<int:inquiry_id>', methods=['GET'])
@require_auth
def get_inquiry(current_user, inquiry_id):
    """
    Get a single inquiry by ID.
    
    Args:
        inquiry_id: Inquiry ID
    
    Returns:
        JSON inquiry details
    """
    try:
        inquiry = Inquiry.query.get(inquiry_id)
        
        if not inquiry:
            raise NotFoundError(f'Inquiry not found: {inquiry_id}')
        
        current_app.logger.info(f'Inquiry {inquiry_id} viewed by {current_user.email}')
        
        return jsonify({
            'success': True,
            'inquiry': inquiry.to_dict()
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f'Error fetching inquiry {inquiry_id}: {str(e)}')
        raise DatabaseError('Failed to fetch inquiry')


@admin_bp.route('/inquiries/<int:inquiry_id>', methods=['PATCH'])
@require_auth
def update_inquiry(current_user, inquiry_id):
    """
    Update an inquiry's status.
    
    Expected JSON:
        {
            "status": "read" | "replied" | "archived"
        }
    
    Returns:
        JSON updated inquiry
    """
    try:
        inquiry = Inquiry.query.get(inquiry_id)
        
        if not inquiry:
            raise NotFoundError(f'Inquiry not found: {inquiry_id}')
        
        data = request.get_json()
        
        if not data:
            raise ValidationError('No data provided')
        
        # Update status if provided
        if 'status' in data:
            valid_statuses = ['new', 'read', 'replied', 'archived']
            status = sanitize_string(data['status'], max_length=20)
            
            if status not in valid_statuses:
                raise ValidationError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
            
            inquiry.status = status
        
        inquiry.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f'Inquiry {inquiry_id} updated by {current_user.email}: status={inquiry.status}')
        
        return jsonify({
            'success': True,
            'message': 'Inquiry updated successfully',
            'inquiry': inquiry.to_dict()
        }), 200
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating inquiry {inquiry_id}: {str(e)}')
        raise DatabaseError('Failed to update inquiry')


@admin_bp.route('/inquiries/<int:inquiry_id>/mark-read', methods=['POST'])
@require_auth
def mark_inquiry_read(current_user, inquiry_id):
    """
    Quick action to mark inquiry as read.
    
    Returns:
        JSON updated inquiry
    """
    try:
        inquiry = Inquiry.query.get(inquiry_id)
        
        if not inquiry:
            raise NotFoundError(f'Inquiry not found: {inquiry_id}')
        
        inquiry.status = 'read'
        inquiry.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f'Inquiry {inquiry_id} marked as read by {current_user.email}')
        
        return jsonify({
            'success': True,
            'message': 'Inquiry marked as read',
            'inquiry': inquiry.to_dict()
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error marking inquiry {inquiry_id} as read: {str(e)}')
        raise DatabaseError('Failed to update inquiry')


@admin_bp.route('/inquiries/<int:inquiry_id>/mark-replied', methods=['POST'])
@require_auth
def mark_inquiry_replied(current_user, inquiry_id):
    """
    Quick action to mark inquiry as replied.
    
    Returns:
        JSON updated inquiry
    """
    try:
        inquiry = Inquiry.query.get(inquiry_id)
        
        if not inquiry:
            raise NotFoundError(f'Inquiry not found: {inquiry_id}')
        
        inquiry.status = 'replied'
        inquiry.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f'Inquiry {inquiry_id} marked as replied by {current_user.email}')
        
        return jsonify({
            'success': True,
            'message': 'Inquiry marked as replied',
            'inquiry': inquiry.to_dict()
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error marking inquiry {inquiry_id} as replied: {str(e)}')
        raise DatabaseError('Failed to update inquiry')


@admin_bp.route('/inquiries/<int:inquiry_id>', methods=['DELETE'])
@require_manager
def delete_inquiry(current_user, inquiry_id):
    """
    Archive/delete an inquiry (manager or admin only).
    
    Returns:
        JSON success message
    """
    try:
        inquiry = Inquiry.query.get(inquiry_id)
        
        if not inquiry:
            raise NotFoundError(f'Inquiry not found: {inquiry_id}')
        
        # Soft delete - just archive it
        inquiry.status = 'archived'
        inquiry.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f'Inquiry {inquiry_id} archived by {current_user.email}')
        
        return jsonify({
            'success': True,
            'message': 'Inquiry archived successfully'
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error archiving inquiry {inquiry_id}: {str(e)}')
        raise DatabaseError('Failed to archive inquiry')


# ==================== EVENT INQUIRIES ====================

@admin_bp.route('/event-inquiries', methods=['GET'])
@require_auth
def get_all_event_inquiries(current_user):
    """
    Get all event inquiries with optional filtering.
    
    Query params:
        - status: Filter by status (new, read, replied, archived)
        - event_type: Filter by event type (wedding, corporate, etc.)
        - limit: Number of results (default 50)
        - offset: Pagination offset (default 0)
    
    Returns:
        JSON list of event inquiries
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        event_type = request.args.get('event_type')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = EventInquiry.query
        
        if status:
            query = query.filter_by(status=status)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        # Order by newest first
        query = query.order_by(EventInquiry.created_at.desc())
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        event_inquiries = query.limit(limit).offset(offset).all()
        
        current_app.logger.info(f'Event inquiries listed by {current_user.email}')
        
        return jsonify({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'count': len(event_inquiries),
            'event_inquiries': [ei.to_dict() for ei in event_inquiries]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Error listing event inquiries: {str(e)}')
        raise DatabaseError('Failed to fetch event inquiries')


@admin_bp.route('/event-inquiries/<int:inquiry_id>', methods=['GET'])
@require_auth
def get_event_inquiry(current_user, inquiry_id):
    """
    Get a single event inquiry by ID.
    
    Args:
        inquiry_id: Event inquiry ID
    
    Returns:
        JSON event inquiry details
    """
    try:
        event_inquiry = EventInquiry.query.get(inquiry_id)
        
        if not event_inquiry:
            raise NotFoundError(f'Event inquiry not found: {inquiry_id}')
        
        current_app.logger.info(f'Event inquiry {inquiry_id} viewed by {current_user.email}')
        
        return jsonify({
            'success': True,
            'event_inquiry': event_inquiry.to_dict()
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f'Error fetching event inquiry {inquiry_id}: {str(e)}')
        raise DatabaseError('Failed to fetch event inquiry')


@admin_bp.route('/event-inquiries/<int:inquiry_id>', methods=['PATCH'])
@require_auth
def update_event_inquiry(current_user, inquiry_id):
    """
    Update an event inquiry's status.
    
    Expected JSON:
        {
            "status": "read" | "replied" | "archived"
        }
    
    Returns:
        JSON updated event inquiry
    """
    try:
        event_inquiry = EventInquiry.query.get(inquiry_id)
        
        if not event_inquiry:
            raise NotFoundError(f'Event inquiry not found: {inquiry_id}')
        
        data = request.get_json()
        
        if not data:
            raise ValidationError('No data provided')
        
        # Update status if provided
        if 'status' in data:
            valid_statuses = ['new', 'read', 'replied', 'archived']
            status = sanitize_string(data['status'], max_length=20)
            
            if status not in valid_statuses:
                raise ValidationError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
            
            event_inquiry.status = status
        
        event_inquiry.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f'Event inquiry {inquiry_id} updated by {current_user.email}: status={event_inquiry.status}')
        
        return jsonify({
            'success': True,
            'message': 'Event inquiry updated successfully',
            'event_inquiry': event_inquiry.to_dict()
        }), 200
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating event inquiry {inquiry_id}: {str(e)}')
        raise DatabaseError('Failed to update event inquiry')


@admin_bp.route('/event-inquiries/<int:inquiry_id>', methods=['DELETE'])
@require_manager
def delete_event_inquiry(current_user, inquiry_id):
    """
    Archive/delete an event inquiry (manager or admin only).
    
    Returns:
        JSON success message
    """
    try:
        event_inquiry = EventInquiry.query.get(inquiry_id)
        
        if not event_inquiry:
            raise NotFoundError(f'Event inquiry not found: {inquiry_id}')
        
        # Soft delete - just archive it
        event_inquiry.status = 'archived'
        event_inquiry.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f'Event inquiry {inquiry_id} archived by {current_user.email}')
        
        return jsonify({
            'success': True,
            'message': 'Event inquiry archived successfully'
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error archiving event inquiry {inquiry_id}: {str(e)}')
        raise DatabaseError('Failed to archive event inquiry')