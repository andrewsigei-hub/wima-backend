"""
Packages routes - API endpoints for package management.
"""
from flask import Blueprint, jsonify, current_app
from app.models.package import Package
from app.utils.errors import NotFoundError, DatabaseError
from app.utils.validators import sanitize_string
from app.utils.rate_limit import limiter

packages_bp = Blueprint('packages', __name__)


@packages_bp.route('', methods=['GET'])
@limiter.limit("100 per hour")
def get_packages():
    """
    Get all active packages.

    Returns:
        JSON list of all active packages with their details
    """
    try:
        packages = Package.get_active_packages()

        current_app.logger.info(f'Fetched {len(packages)} active packages')

        return jsonify({
            'success': True,
            'count': len(packages),
            'packages': [p.to_dict() for p in packages]
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error fetching packages: {str(e)}')
        raise DatabaseError('Failed to fetch packages')


@packages_bp.route('/featured', methods=['GET'])
@limiter.limit("100 per hour")
def get_featured_packages():
    """
    Get featured packages for homepage display.

    Returns:
        JSON list of featured packages
    """
    try:
        packages = Package.get_featured_packages()

        current_app.logger.info(f'Fetched {len(packages)} featured packages')

        return jsonify({
            'success': True,
            'count': len(packages),
            'packages': [p.to_dict() for p in packages]
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error fetching featured packages: {str(e)}')
        raise DatabaseError('Failed to fetch featured packages')


@packages_bp.route('/<slug>', methods=['GET'])
@limiter.limit("100 per hour")
def get_package_by_slug(slug):
    """
    Get a single package by its slug.

    Args:
        slug: URL-friendly package identifier

    Returns:
        JSON package details or 404 if not found
    """
    try:
        slug = sanitize_string(slug, max_length=100)

        if not slug:
            raise NotFoundError('Invalid package slug')

        package = Package.get_by_slug(slug)

        if not package:
            current_app.logger.info(f'Package not found: {slug}')
            raise NotFoundError(f'Package not found: {slug}')

        current_app.logger.info(f'Fetched package: {slug}')

        return jsonify({
            'success': True,
            'package': package.to_dict()
        }), 200

    except NotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f'Error fetching package {slug}: {str(e)}')
        raise DatabaseError('Failed to fetch package')
