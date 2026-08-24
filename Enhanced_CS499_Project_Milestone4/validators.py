"""Validation helpers for dashboard and database input."""

from copy import deepcopy


ALLOWED_QUERY_OPERATORS = {
    "$eq",
    "$ne",
    "$gt",
    "$gte",
    "$lt",
    "$lte",
    "$in",
    "$nin",
}
ALLOWED_LOGICAL_OPERATORS = {"$and", "$or"}

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

    _validate_document_keys(data)
    return deepcopy(data)


def validate_query(query):
    """Validate a MongoDB query and reject unsafe operators."""
    if not isinstance(query, dict):
        raise ValidationError("The query must be a dictionary.")

    return _validate_query_parts(query)


def validate_write_query(query):
    """Validate a write query and prevent accidental all-record changes."""
    safe_query = validate_query(query)
    if not safe_query or _has_empty_logical_query(safe_query):
        raise ValidationError(
            "Update and delete operations require a specific query."
        )
    return safe_query


def validate_update_values(values):
    """Validate fields before a MongoDB update."""
    if not isinstance(values, dict) or not values:
        raise ValidationError("Update values must be a non-empty dictionary.")

    if "_id" in values:
        raise ValidationError("The MongoDB _id field cannot be changed.")

    _validate_document_keys(values)
    return deepcopy(values)


def validate_projection(projection):
    """Validate optional fields included in or excluded from query results."""
    if projection is None:
        return None
    if not isinstance(projection, dict) or not projection:
        raise ValidationError("The projection must be a non-empty dictionary.")

    safe_projection = {}
    included = False
    excluded = False

    for field_name, setting in projection.items():
        _validate_field_name(field_name)
        if setting not in (0, 1, False, True):
            raise ValidationError("Projection values must be 0 or 1.")

        safe_projection[field_name] = int(bool(setting))
        if field_name != "_id":
            included = included or bool(setting)
            excluded = excluded or not bool(setting)

    if included and excluded:
        raise ValidationError(
            "A projection cannot mix included and excluded fields."
        )

    return safe_projection


def _validate_query_parts(query):
    """Recursively validate a query dictionary."""
    safe_query = {}

    for field_name, condition in query.items():
        if field_name in ALLOWED_LOGICAL_OPERATORS:
            if not isinstance(condition, list) or not condition:
                raise ValidationError(
                    f"{field_name} must contain a non-empty list of queries."
                )
            if not all(isinstance(item, dict) for item in condition):
                raise ValidationError(
                    f"Every item in {field_name} must be a query dictionary."
                )
            safe_query[field_name] = [
                _validate_query_parts(item) for item in condition
            ]
            continue

        _validate_field_name(field_name)
        safe_query[field_name] = _validate_field_condition(condition)

    return safe_query


def _validate_field_condition(condition):
    """Validate the comparison operators used for one field."""
    if not isinstance(condition, dict):
        return deepcopy(condition)
    if not condition:
        raise ValidationError("Query conditions cannot be empty dictionaries.")

    safe_condition = {}
    for operator, value in condition.items():
        if operator not in ALLOWED_QUERY_OPERATORS:
            raise ValidationError(f"The query operator {operator!r} is not allowed.")
        if operator in {"$in", "$nin"} and not isinstance(value, (list, tuple)):
            raise ValidationError(f"{operator} requires a list of values.")
        if isinstance(value, dict):
            raise ValidationError("Nested query operators are not allowed.")
        safe_condition[operator] = deepcopy(value)

    return safe_condition


def _validate_document_keys(document):
    """Reject keys that MongoDB treats as operators or field paths."""
    for field_name, value in document.items():
        _validate_field_name(field_name)
        if isinstance(value, dict):
            _validate_document_keys(value)
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, dict):
                    _validate_document_keys(item)


def _validate_field_name(field_name):
    """Validate a MongoDB field name supplied by the application."""
    if not isinstance(field_name, str) or not field_name:
        raise ValidationError("MongoDB field names must be non-empty strings.")
    if field_name.startswith("$") or "." in field_name:
        raise ValidationError(
            "MongoDB field names cannot start with '$' or contain '.'."
        )


def _has_empty_logical_query(query):
    """Return True when a logical branch could match every document."""
    for field_name, condition in query.items():
        if field_name in ALLOWED_LOGICAL_OPERATORS:
            for nested_query in condition:
                if not nested_query or _has_empty_logical_query(nested_query):
                    return True
    return False
