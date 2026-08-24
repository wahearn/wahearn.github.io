"""MongoDB connection and CRUD operations for animal records."""

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import AppConfig
from validators import (
    validate_document,
    validate_query,
    validate_update_values,
    validate_write_query,
)


class DatabaseOperationError(RuntimeError):
    """Raised when a MongoDB connection or CRUD operation fails."""


class AnimalShelter:
    """Provide CRUD operations for the configured animal collection."""

    def __init__(self, config: AppConfig):
        client_options = {
            "host": config.mongo_host,
            "port": config.mongo_port,
            "username": config.mongo_username,
            "password": config.mongo_password,
            "serverSelectionTimeoutMS": config.server_selection_timeout_ms,
        }
        if config.mongo_auth_source:
            client_options["authSource"] = config.mongo_auth_source

        try:
            self.client = MongoClient(**client_options)
            self.database = self.client[config.mongo_database]
            self.collection = self.database[config.mongo_collection]
            self.client.admin.command("ping")
        except PyMongoError as exc:
            raise DatabaseOperationError("Unable to connect to MongoDB.") from exc

    def create(self, data):
        """Insert one animal record and return whether it was acknowledged."""
        document = validate_document(data)
        try:
            result = self.collection.insert_one(document)
            return result.acknowledged
        except PyMongoError as exc:
            raise DatabaseOperationError("Unable to create the animal record.") from exc

    def read(self, query, projection=None):
        """Return animal records matching a MongoDB query."""
        safe_query = validate_query(query)
        try:
            return list(self.collection.find(safe_query, projection))
        except PyMongoError as exc:
            raise DatabaseOperationError("Unable to retrieve animal records.") from exc

    def update(self, query, new_values):
        """Update matching animal records and return the modified count."""
        safe_query = validate_write_query(query)
        safe_values = validate_update_values(new_values)
        try:
            result = self.collection.update_many(safe_query, {"$set": safe_values})
            return result.modified_count
        except PyMongoError as exc:
            raise DatabaseOperationError("Unable to update animal records.") from exc

    def delete(self, query):
        """Delete matching animal records and return the deleted count."""
        safe_query = validate_write_query(query)
        try:
            result = self.collection.delete_many(safe_query)
            return result.deleted_count
        except PyMongoError as exc:
            raise DatabaseOperationError("Unable to delete animal records.") from exc

    def close(self):
        """Close the MongoDB client connection."""
        self.client.close()
