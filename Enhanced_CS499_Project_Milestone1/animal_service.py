"""Business logic for selecting and displaying animal records."""

from validators import validate_filter_type


RESCUE_FILTERS = {
    "WATER": {
        "breed": {
            "$in": [
                "Labrador Retriever Mix",
                "Chesapeake Bay Retriever",
                "Newfoundland",
            ]
        },
        "sex_upon_outcome": "Intact Female",
        "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
    },
    "MOUNTAIN": {
        "breed": {
            "$in": [
                "German Shepherd",
                "Alaskan Malamute",
                "Old English Sheepdog",
                "Siberian Husky",
                "Rottweiler",
            ]
        },
        "sex_upon_outcome": "Intact Male",
        "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
    },
    "DISASTER": {
        "breed": {
            "$in": [
                "Doberman Pinscher",
                "German Shepherd",
                "Golden Retriever",
                "Bloodhound",
                "Rottweiler",
            ]
        },
        "sex_upon_outcome": "Intact Male",
        "age_upon_outcome_in_weeks": {"$gte": 20, "$lte": 300},
    },
    "RESET": {},
}


class AnimalService:
    """Coordinate rescue-filter business rules and database access."""

    def __init__(self, database):
        self._database = database

    def get_animals(self, filter_type):
        """Return sanitized animal records for the selected rescue type."""
        normalized_filter = validate_filter_type(filter_type)
        query = RESCUE_FILTERS[normalized_filter]
        records = self._database.read(query)
        return self._remove_object_ids(records)

    def get_table_data(self, filter_type):
        """Return Dash-compatible table records and column definitions."""
        records = self.get_animals(filter_type)
        field_names = self._collect_field_names(records)

        columns = []
        for field_name in field_names:
            column = {
                "name": field_name,
                "id": field_name,
                "deletable": False,
                "selectable": True,
            }
            columns.append(column)

        return records, columns

    @staticmethod
    def _remove_object_ids(records):
        """Remove MongoDB ObjectId values that Dash cannot serialize."""
        sanitized_records = []
        for record in records:
            sanitized = dict(record)
            sanitized.pop("_id", None)
            sanitized_records.append(sanitized)
        return sanitized_records

    @staticmethod
    def _collect_field_names(records):
        """Collect record fields while preserving their first-seen order."""
        field_names = []

        for record in records:
            for field_name in record:
                if field_name not in field_names:
                    field_names.append(field_name)

        return field_names
