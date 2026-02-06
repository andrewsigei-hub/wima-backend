"""
Serializer mixin for SQLAlchemy models.
"""
from datetime import date, datetime
import sqlalchemy as sa


class SerializerMixin:
    """
    Mixin that auto-generates to_dict() by inspecting SQLAlchemy columns.
    Handles date formatting in a single place.
    """

    DATE_FORMAT = '%d-%m-%Y'

    # Override in subclasses to exclude columns from serialization
    serialize_exclude = ()

    # Override in subclasses to provide default values for nullable JSON columns
    serialize_defaults = {}

    def to_dict(self, exclude=(), extra=None):
        """
        Convert model instance to dictionary for API responses.

        Args:
            exclude: Column names to exclude from output
            extra: Extra key-value pairs to merge into the result

        Returns:
            Dictionary representation of the model
        """
        all_exclude = set(self.serialize_exclude) | set(exclude)
        data = {}

        for col in self.__table__.columns:
            if col.name in all_exclude:
                continue

            value = getattr(self, col.name)

            if value is None and col.name in self.serialize_defaults:
                value = self.serialize_defaults[col.name]()
            elif isinstance(value, datetime):
                value = value.strftime(self.DATE_FORMAT)
            elif isinstance(value, date):
                value = value.strftime(self.DATE_FORMAT)

            data[col.name] = value

        if extra:
            data.update(extra)

        return data
