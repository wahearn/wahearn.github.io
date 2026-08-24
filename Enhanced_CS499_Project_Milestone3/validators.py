"""Validation helpers for dashboard and database input."""

VALID_FILTER_TYPES = {"WATER", "MOUNTAIN", "DISASTER", "RESET"}
VALID_SEARCH_MODES = {"RANKED", "EXACT"}


class ValidationError(ValueError):
    """Raised when application input is missing or invalid."""


def validate_filter_type(filter_type):
    """Return a normalized rescue filter or raise ValidationError."""
    if not isinstance(filter_type, str):
        raise ValidationError("A rescue type must be selected.")

    normalized = filter_type.strip().upper()
    if normalized not in VALID_FILTER_TYPES:
        raise ValidationError("The selected rescue type is not supported.")

    return normalized


def validate_search_mode(search_mode):
    """Return a normalized search mode or raise ValidationError."""
    if not isinstance(search_mode, str):
        raise ValidationError("A search mode must be selected.")

    normalized = search_mode.strip().upper()
    if normalized not in VALID_SEARCH_MODES:
        raise ValidationError("The selected search mode is not supported.")

    return normalized


def validate_document(data):
    """Validate a document before it is inserted into MongoDB."""
    if not isinstance(data, dict) or not data:
        raise ValidationError("The document must be a non-empty dictionary.")
    return data


def validate_query(query):
    """Validate a MongoDB query. An empty dictionary is allowed."""
    if not isinstance(query, dict):
        raise ValidationError("The query must be a dictionary.")
    return query


def validate_write_query(query):
    """Validate a write query and prevent accidental all-record changes."""
    safe_query = validate_query(query)
    if not safe_query:
        raise ValidationError(
            "Update and delete operations require a specific query."
        )
    return safe_query


def validate_update_values(values):
    """Validate fields before a MongoDB update."""
    if not isinstance(values, dict) or not values:
        raise ValidationError("Update values must be a non-empty dictionary.")
    return values
