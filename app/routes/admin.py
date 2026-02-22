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

admin_bp = Blueprint("admin", __name__)


# ==================== DASHBOARD ====================


@admin_bp.route("/dashboard", methods=["GET"])
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
        new_inquiries = Inquiry.query.filter_by(status="new").count()
        read_inquiries = Inquiry.query.filter_by(status="read").count()
        replied_inquiries = Inquiry.query.filter_by(status="replied").count()

        # Event inquiry stats
        total_event_inquiries = EventInquiry.query.count()
        new_event_inquiries = EventInquiry.query.filter_by(status="new").count()

        # Room stats
        total_rooms = Room.query.filter_by(is_active=True).count()
        featured_rooms = Room.query.filter_by(is_active=True, is_featured=True).count()

        # Recent inquiries (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_inquiries = Inquiry.query.filter(Inquiry.created_at >= week_ago).count()
        recent_event_inquiries = EventInquiry.query.filter(
            EventInquiry.created_at >= week_ago
        ).count()

        current_app.logger.info(f"Dashboard accessed by {current_user.email}")

        return (
            jsonify(
                {
                    "success": True,
                    "stats": {
                        "inquiries": {
                            "total": total_inquiries,
                            "new": new_inquiries,
                            "read": read_inquiries,
                            "replied": replied_inquiries,
                            "last_7_days": recent_inquiries,
                        },
                        "event_inquiries": {
                            "total": total_event_inquiries,
                            "new": new_event_inquiries,
                            "last_7_days": recent_event_inquiries,
                        },
                        "rooms": {"total": total_rooms, "featured": featured_rooms},
                    },
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        raise DatabaseError("Failed to fetch dashboard stats")


# ==================== INQUIRIES ====================


@admin_bp.route("/inquiries", methods=["GET"])
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
        status = request.args.get("status")
        inquiry_type = request.args.get("type")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

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

        current_app.logger.info(f"Inquiries listed by {current_user.email}")

        return (
            jsonify(
                {
                    "success": True,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "count": len(inquiries),
                    "inquiries": [inquiry.to_dict() for inquiry in inquiries],
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error listing inquiries: {str(e)}")
        raise DatabaseError("Failed to fetch inquiries")


@admin_bp.route("/inquiries/<int:inquiry_id>", methods=["GET"])
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
            raise NotFoundError(f"Inquiry not found: {inquiry_id}")

        current_app.logger.info(f"Inquiry {inquiry_id} viewed by {current_user.email}")

        return jsonify({"success": True, "inquiry": inquiry.to_dict()}), 200

    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error fetching inquiry {inquiry_id}: {str(e)}")
        raise DatabaseError("Failed to fetch inquiry")


@admin_bp.route("/inquiries/<int:inquiry_id>", methods=["PATCH"])
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
            raise NotFoundError(f"Inquiry not found: {inquiry_id}")

        data = request.get_json()

        if not data:
            raise ValidationError("No data provided")

        # Update status if provided
        if "status" in data:
            valid_statuses = ["new", "read", "replied", "archived"]
            status = sanitize_string(data["status"], max_length=20)

            if status not in valid_statuses:
                raise ValidationError(
                    f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                )

            inquiry.status = status

        inquiry.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(
            f"Inquiry {inquiry_id} updated by {current_user.email}: status={inquiry.status}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Inquiry updated successfully",
                    "inquiry": inquiry.to_dict(),
                }
            ),
            200,
        )

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating inquiry {inquiry_id}: {str(e)}")
        raise DatabaseError("Failed to update inquiry")


@admin_bp.route("/inquiries/<int:inquiry_id>/mark-read", methods=["POST"])
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
            raise NotFoundError(f"Inquiry not found: {inquiry_id}")

        inquiry.status = "read"
        inquiry.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(
            f"Inquiry {inquiry_id} marked as read by {current_user.email}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Inquiry marked as read",
                    "inquiry": inquiry.to_dict(),
                }
            ),
            200,
        )

    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error marking inquiry {inquiry_id} as read: {str(e)}"
        )
        raise DatabaseError("Failed to update inquiry")


@admin_bp.route("/inquiries/<int:inquiry_id>/mark-replied", methods=["POST"])
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
            raise NotFoundError(f"Inquiry not found: {inquiry_id}")

        inquiry.status = "replied"
        inquiry.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(
            f"Inquiry {inquiry_id} marked as replied by {current_user.email}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Inquiry marked as replied",
                    "inquiry": inquiry.to_dict(),
                }
            ),
            200,
        )

    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error marking inquiry {inquiry_id} as replied: {str(e)}"
        )
        raise DatabaseError("Failed to update inquiry")


@admin_bp.route("/inquiries/<int:inquiry_id>", methods=["DELETE"])
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
            raise NotFoundError(f"Inquiry not found: {inquiry_id}")

        # Soft delete - just archive it
        inquiry.status = "archived"
        inquiry.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(
            f"Inquiry {inquiry_id} archived by {current_user.email}"
        )

        return (
            jsonify({"success": True, "message": "Inquiry archived successfully"}),
            200,
        )

    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error archiving inquiry {inquiry_id}: {str(e)}")
        raise DatabaseError("Failed to archive inquiry")


# ==================== EVENT INQUIRIES ====================


@admin_bp.route("/event-inquiries", methods=["GET"])
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
        status = request.args.get("status")
        event_type = request.args.get("event_type")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

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

        current_app.logger.info(f"Event inquiries listed by {current_user.email}")

        return (
            jsonify(
                {
                    "success": True,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "count": len(event_inquiries),
                    "event_inquiries": [ei.to_dict() for ei in event_inquiries],
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error listing event inquiries: {str(e)}")
        raise DatabaseError("Failed to fetch event inquiries")


@admin_bp.route("/event-inquiries/<int:inquiry_id>", methods=["GET"])
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
            raise NotFoundError(f"Event inquiry not found: {inquiry_id}")

        current_app.logger.info(
            f"Event inquiry {inquiry_id} viewed by {current_user.email}"
        )

        return jsonify({"success": True, "event_inquiry": event_inquiry.to_dict()}), 200

    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error fetching event inquiry {inquiry_id}: {str(e)}")
        raise DatabaseError("Failed to fetch event inquiry")


@admin_bp.route("/event-inquiries/<int:inquiry_id>", methods=["PATCH"])
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
            raise NotFoundError(f"Event inquiry not found: {inquiry_id}")

        data = request.get_json()

        if not data:
            raise ValidationError("No data provided")

        # Update status if provided
        if "status" in data:
            valid_statuses = ["new", "read", "replied", "archived"]
            status = sanitize_string(data["status"], max_length=20)

            if status not in valid_statuses:
                raise ValidationError(
                    f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                )

            event_inquiry.status = status

        event_inquiry.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(
            f"Event inquiry {inquiry_id} updated by {current_user.email}: status={event_inquiry.status}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Event inquiry updated successfully",
                    "event_inquiry": event_inquiry.to_dict(),
                }
            ),
            200,
        )

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating event inquiry {inquiry_id}: {str(e)}")
        raise DatabaseError("Failed to update event inquiry")


@admin_bp.route("/event-inquiries/<int:inquiry_id>", methods=["DELETE"])
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
            raise NotFoundError(f"Event inquiry not found: {inquiry_id}")

        # Soft delete - just archive it
        event_inquiry.status = "archived"
        event_inquiry.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(
            f"Event inquiry {inquiry_id} archived by {current_user.email}"
        )

        return (
            jsonify(
                {"success": True, "message": "Event inquiry archived successfully"}
            ),
            200,
        )

    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error archiving event inquiry {inquiry_id}: {str(e)}"
        )
        raise DatabaseError("Failed to archive event inquiry")


# ==================== ROOM MANAGEMENT ====================


@admin_bp.route("/rooms", methods=["GET"])
@require_auth
def admin_get_all_rooms(current_user):
    """
    Get all rooms (including inactive) for admin management.

    Query params:
        - include_inactive: Include inactive rooms (default: true)
        - type: Filter by room type

    Returns:
        JSON list of all rooms
    """
    try:
        include_inactive = (
            request.args.get("include_inactive", "true").lower() == "true"
        )
        room_type = request.args.get("type")

        query = Room.query

        if not include_inactive:
            query = query.filter_by(is_active=True)

        if room_type:
            query = query.filter_by(type=room_type)

        rooms = query.order_by(Room.created_at.desc()).all()

        current_app.logger.info(f"Admin rooms listed by {current_user.email}")

        return (
            jsonify(
                {
                    "success": True,
                    "count": len(rooms),
                    "rooms": [room.to_dict() for room in rooms],
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error listing rooms: {str(e)}")
        raise DatabaseError("Failed to fetch rooms")


@admin_bp.route("/rooms", methods=["POST"])
@require_manager
def create_room(current_user):
    """
    Create a new room (manager or admin only).

    Expected JSON:
        {
            "name": "Deluxe Room 4",
            "slug": "deluxe-room-4",
            "type": "deluxe",
            "description": "A beautiful deluxe room...",
            "capacity": 2,
            "price_per_night": 5500,
            "breakfast_included": true,
            "amenities": ["WiFi", "TV", "En-suite"],
            "images": ["/images/rooms/deluxe-4.jpg"],
            "is_featured": false
        }

    Returns:
        JSON created room
    """
    try:
        data = request.get_json()

        if not data:
            raise ValidationError("No data provided")

        # Validate required fields
        required_fields = [
            "name",
            "slug",
            "type",
            "description",
            "capacity",
            "price_per_night",
        ]
        is_valid, missing = validate_required_fields(data, required_fields)

        if not is_valid:
            raise ValidationError(f'Missing required fields: {", ".join(missing)}')

        # Sanitize inputs
        name = sanitize_string(data["name"], max_length=100)
        slug = sanitize_string(data["slug"], max_length=100).lower().replace(" ", "-")
        room_type = sanitize_string(data["type"], max_length=50)
        description = sanitize_string(data["description"], max_length=2000)

        # Validate room type
        valid_types = [
            "premier",
            "cottage",
            "double",
            "standard",
            "deluxe",
            "executive",
            "family",
        ]
        if room_type not in valid_types:
            raise ValidationError(
                f'Invalid room type. Must be one of: {", ".join(valid_types)}'
            )

        # Check if slug already exists
        existing_room = Room.query.filter_by(slug=slug).first()
        if existing_room:
            raise ValidationError(f'Room with slug "{slug}" already exists')

        # Validate numeric fields
        try:
            capacity = int(data["capacity"])
            if capacity < 1 or capacity > 20:
                raise ValueError
        except (ValueError, TypeError):
            raise ValidationError("Capacity must be a number between 1 and 20")

        try:
            price_per_night = int(data["price_per_night"])
            if price_per_night < 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValidationError("Price per night must be a positive number")

        # Create room
        room = Room(
            name=name,
            slug=slug,
            type=room_type,
            description=description,
            capacity=capacity,
            price_per_night=price_per_night,
            breakfast_included=data.get("breakfast_included", True),
            amenities=data.get("amenities", []),
            images=data.get("images", []),
            is_featured=data.get("is_featured", False),
            is_active=True,
        )

        db.session.add(room)
        db.session.commit()

        current_app.logger.info(f"Room created: {room.name} by {current_user.email}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Room created successfully",
                    "room": room.to_dict(),
                }
            ),
            201,
        )

    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating room: {str(e)}")
        raise DatabaseError("Failed to create room")


@admin_bp.route("/rooms/<int:room_id>", methods=["GET"])
@require_auth
def admin_get_room(current_user, room_id):
    """
    Get a single room by ID (includes inactive rooms).

    Args:
        room_id: Room ID

    Returns:
        JSON room details
    """
    try:
        room = Room.query.get(room_id)

        if not room:
            raise NotFoundError(f"Room not found: {room_id}")

        current_app.logger.info(f"Room {room_id} viewed by {current_user.email}")

        return jsonify({"success": True, "room": room.to_dict()}), 200

    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error fetching room {room_id}: {str(e)}")
        raise DatabaseError("Failed to fetch room")


@admin_bp.route("/rooms/<int:room_id>", methods=["PATCH"])
@require_manager
def update_room(current_user, room_id):
    """
    Update a room (manager or admin only).

    Expected JSON (all fields optional):
        {
            "name": "Updated Room Name",
            "description": "Updated description...",
            "capacity": 3,
            "price_per_night": 6000,
            "breakfast_included": true,
            "amenities": ["WiFi", "TV", "En-suite", "Balcony"],
            "images": ["/images/rooms/updated.jpg"],
            "is_featured": true,
            "is_active": true
        }

    Returns:
        JSON updated room
    """
    try:
        room = Room.query.get(room_id)

        if not room:
            raise NotFoundError(f"Room not found: {room_id}")

        data = request.get_json()

        if not data:
            raise ValidationError("No data provided")

        # Update name
        if "name" in data:
            room.name = sanitize_string(data["name"], max_length=100)

        # Update slug
        if "slug" in data:
            new_slug = (
                sanitize_string(data["slug"], max_length=100).lower().replace(" ", "-")
            )
            # Check if slug already exists for another room
            existing = Room.query.filter(
                Room.slug == new_slug, Room.id != room_id
            ).first()
            if existing:
                raise ValidationError(f'Room with slug "{new_slug}" already exists')
            room.slug = new_slug

        # Update type
        if "type" in data:
            room_type = sanitize_string(data["type"], max_length=50)
            valid_types = [
                "premier",
                "cottage",
                "double",
                "standard",
                "deluxe",
                "executive",
                "family",
            ]
            if room_type not in valid_types:
                raise ValidationError(
                    f'Invalid room type. Must be one of: {", ".join(valid_types)}'
                )
            room.type = room_type

        # Update description
        if "description" in data:
            room.description = sanitize_string(data["description"], max_length=2000)

        # Update capacity
        if "capacity" in data:
            try:
                capacity = int(data["capacity"])
                if capacity < 1 or capacity > 20:
                    raise ValueError
                room.capacity = capacity
            except (ValueError, TypeError):
                raise ValidationError("Capacity must be a number between 1 and 20")

        # Update price
        if "price_per_night" in data:
            try:
                price = int(data["price_per_night"])
                if price < 0:
                    raise ValueError
                room.price_per_night = price
            except (ValueError, TypeError):
                raise ValidationError("Price per night must be a positive number")

        # Update boolean fields
        if "breakfast_included" in data:
            room.breakfast_included = bool(data["breakfast_included"])

        if "is_featured" in data:
            room.is_featured = bool(data["is_featured"])

        if "is_active" in data:
            room.is_active = bool(data["is_active"])

        # Update arrays
        if "amenities" in data:
            if isinstance(data["amenities"], list):
                room.amenities = data["amenities"]
            else:
                raise ValidationError("Amenities must be an array")

        if "images" in data:
            if isinstance(data["images"], list):
                room.images = data["images"]
            else:
                raise ValidationError("Images must be an array")

        room.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(f"Room {room_id} updated by {current_user.email}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Room updated successfully",
                    "room": room.to_dict(),
                }
            ),
            200,
        )

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating room {room_id}: {str(e)}")
        raise DatabaseError("Failed to update room")


@admin_bp.route("/rooms/<int:room_id>", methods=["DELETE"])
@require_admin
def delete_room(current_user, room_id):
    """
    Soft delete a room (admin only).
    Sets is_active to False instead of actually deleting.

    Returns:
        JSON success message
    """
    try:
        room = Room.query.get(room_id)

        if not room:
            raise NotFoundError(f"Room not found: {room_id}")

        # Soft delete
        room.is_active = False
        room.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(f"Room {room_id} deactivated by {current_user.email}")

        return (
            jsonify({"success": True, "message": "Room deactivated successfully"}),
            200,
        )

    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deactivating room {room_id}: {str(e)}")
        raise DatabaseError("Failed to deactivate room")


@admin_bp.route("/rooms/<int:room_id>/activate", methods=["POST"])
@require_manager
def activate_room(current_user, room_id):
    """
    Reactivate a deactivated room.

    Returns:
        JSON success message
    """
    try:
        room = Room.query.get(room_id)

        if not room:
            raise NotFoundError(f"Room not found: {room_id}")

        room.is_active = True
        room.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(f"Room {room_id} activated by {current_user.email}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Room activated successfully",
                    "room": room.to_dict(),
                }
            ),
            200,
        )

    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error activating room {room_id}: {str(e)}")
        raise DatabaseError("Failed to activate room")


@admin_bp.route("/rooms/<int:room_id>/toggle-featured", methods=["POST"])
@require_auth
def toggle_room_featured(current_user, room_id):
    """
    Toggle a room's featured status.

    Returns:
        JSON success message with new status
    """
    try:
        room = Room.query.get(room_id)

        if not room:
            raise NotFoundError(f"Room not found: {room_id}")

        room.is_featured = not room.is_featured
        room.updated_at = datetime.utcnow()
        db.session.commit()

        status = "featured" if room.is_featured else "unfeatured"
        current_app.logger.info(f"Room {room_id} {status} by {current_user.email}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Room {status} successfully",
                    "is_featured": room.is_featured,
                    "room": room.to_dict(),
                }
            ),
            200,
        )

    except NotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error toggling room {room_id} featured status: {str(e)}"
        )
        raise DatabaseError("Failed to update room")
