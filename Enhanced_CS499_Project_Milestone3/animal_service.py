"""Business logic for selecting, ranking, and displaying animal records."""

from validators import validate_filter_type, validate_search_mode


INELIGIBLE_RANKED_OUTCOMES = {"Died", "Euthanasia", "Disposal"}
BEST_TRAINING_AGE_RANGE_WEEKS = (8, 26)
SECOND_BEST_TRAINING_AGE_RANGE_WEEKS = (26, 156)
OLDER_DOG_AGE_RANGE_WEEKS = (156, 364)
SENIOR_DOG_AGE_WEEKS = 364
SENIOR_DOG_PENALTY = 2.2


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


RESCUE_CRITERIA = {
    "WATER": {
        "base_query": {
            "animal_type": "Dog",
            "outcome_type": {"$nin": sorted(INELIGIBLE_RANKED_OUTCOMES)},
        },
        "preferred_breeds": (
            "Labrador Retriever Mix",
            "Chesapeake Bay Retriever",
            "Newfoundland",
        ),
        "best_training_age_range": BEST_TRAINING_AGE_RANGE_WEEKS,
        "second_best_training_age_range": SECOND_BEST_TRAINING_AGE_RANGE_WEEKS,
        "preferred_sex": "Intact Female",
    },
    "MOUNTAIN": {
        "base_query": {
            "animal_type": "Dog",
            "outcome_type": {"$nin": sorted(INELIGIBLE_RANKED_OUTCOMES)},
        },
        "preferred_breeds": (
            "German Shepherd",
            "Alaskan Malamute",
            "Old English Sheepdog",
            "Siberian Husky",
            "Rottweiler",
        ),
        "best_training_age_range": BEST_TRAINING_AGE_RANGE_WEEKS,
        "second_best_training_age_range": SECOND_BEST_TRAINING_AGE_RANGE_WEEKS,
        "preferred_sex": "Intact Male",
    },
    "DISASTER": {
        "base_query": {
            "animal_type": "Dog",
            "outcome_type": {"$nin": sorted(INELIGIBLE_RANKED_OUTCOMES)},
        },
        "preferred_breeds": (
            "Doberman Pinscher",
            "German Shepherd",
            "Golden Retriever",
            "Bloodhound",
            "Rottweiler",
        ),
        "best_training_age_range": BEST_TRAINING_AGE_RANGE_WEEKS,
        "second_best_training_age_range": SECOND_BEST_TRAINING_AGE_RANGE_WEEKS,
        "preferred_sex": "Intact Male",
    },
    "RESET": {
        "base_query": {},
        "preferred_breeds": (),
        "best_training_age_range": None,
        "second_best_training_age_range": None,
        "preferred_sex": None,
    },
}


class AnimalService:
    """Coordinate rescue-filter business rules and database access."""

    def __init__(self, database):
        self._database = database

    def get_animals(self, filter_type, search_mode="EXACT"):
        """Return sanitized records using exact or ranked search behavior."""
        normalized_filter = validate_filter_type(filter_type)
        normalized_mode = validate_search_mode(search_mode)

        if normalized_mode == "RANKED" and normalized_filter != "RESET":
            return self.rank_animals(normalized_filter)

        query = RESCUE_FILTERS[normalized_filter]
        records = self._database.read(query)
        return self._remove_object_ids(records)

    def rank_animals(self, rescue_type):
        """Return rescue candidates ordered from strongest to weakest match."""
        normalized_filter = validate_filter_type(rescue_type)
        criteria = RESCUE_CRITERIA[normalized_filter]
        records = self._database.read(criteria["base_query"])

        ranked_results = []
        for record in self._remove_object_ids(records):
            if record.get("outcome_type") in INELIGIBLE_RANKED_OUTCOMES:
                continue

            score, reasons = self._score_animal(record, criteria)
            ranked_record = {
                "match_score": score,
                "match_reasons": ", ".join(reasons) or "No ranking criteria matched",
            }
            ranked_record.update(record)
            ranked_results.append(ranked_record)

        ranked_results.sort(key=lambda animal: -animal["match_score"])
        return ranked_results

    def get_table_data(self, filter_type, search_mode="EXACT"):
        """Return Dash-compatible table records and column definitions."""
        records = self.get_animals(filter_type, search_mode)
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

    @classmethod
    def _score_animal(cls, animal, criteria):
        """Calculate a weighted score and human-readable match reasons."""
        score = 0
        reasons = []

        if animal.get("breed") in criteria["preferred_breeds"]:
            score += 5
            reasons.append("breed (+5)")

        age = cls._to_number(animal.get("age_upon_outcome_in_weeks"))
        best_age_range = criteria["best_training_age_range"]
        second_best_age_range = criteria["second_best_training_age_range"]
        if age is not None and best_age_range is not None:
            minimum_age, maximum_age = best_age_range
            if 0 <= age < minimum_age:
                score += 0.5
                reasons.append("age: under 8 weeks (+0.5)")
            elif minimum_age <= age < maximum_age:
                score += 2.5
                reasons.append("age: 8 weeks–6 months (+2.5)")
            elif second_best_age_range is not None:
                minimum_age, maximum_age = second_best_age_range
                if minimum_age <= age < maximum_age:
                    score += 2.4
                    reasons.append("age: 6 months–2 years (+2.4)")
                else:
                    minimum_age, maximum_age = OLDER_DOG_AGE_RANGE_WEEKS
                    if minimum_age <= age < maximum_age:
                        score += 0.10
                        reasons.append("age: 3–6 years (+0.10)")

        preferred_sex = criteria["preferred_sex"]
        sex_matches = (
            preferred_sex is not None
            and animal.get("sex_upon_outcome") == preferred_sex
        )
        if sex_matches:
            score += 2.25
            reasons.append("sex (+2.25)")

        if (
            age is not None
            and best_age_range is not None
            and age >= SENIOR_DOG_AGE_WEEKS
        ):
            score = max(0, round(score - SENIOR_DOG_PENALTY, 2))
            if score == 0:
                # Hide positive criteria when the senior penalty consumes all
                # of their points, but always explain the senior penalty.
                reasons = ["age: 7+ years"]
            else:
                reasons.append("age: 7+ years")

        return score, reasons

    @staticmethod
    def _to_number(value):
        """Convert database numeric values without letting invalid ages match."""
        if isinstance(value, bool):
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None

        # for NaN
        return number if number == number else None

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
