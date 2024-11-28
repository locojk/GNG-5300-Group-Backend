import json
import os
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid
from jsonschema import validate, ValidationError
from utils.logger import Logger
from utils.env_loader import load_platform_specific_env

logger = Logger(__name__)
# Dynamically load environment variables based on OS and hostname
load_platform_specific_env()


class MongoDBClient:
    def __init__(self, db_name=None):
        self.db_name = db_name if db_name else os.getenv('MONGO_DATABASE', 'fitness_db')
        self.uri = os.getenv('MONGO_URI')

        if not self.uri:
            raise ValueError("MONGO_URI environment variable is not set!")

        logger.info(f"MongoDB URI constructed: {self.uri}")
        self.client = None
        self.db = None
        self.schemas = {}  # Cache loaded schemas
        self._connect()

    def _connect(self):
        """Connect to MongoDB and test connection"""
        if not self.client:
            try:
                logger.info(f"Connecting to MongoDB: URI={self.uri}, DB_NAME={self.db_name}")
                self.client = MongoClient(self.uri)
                self.db = self.client[self.db_name]
                self.client.admin.command('ping')  # 测试连接
                logger.info(f"Successfully connected to MongoDB database: {self.db_name}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                self.db = None
                raise

    def __enter__(self):
        """Ensure self.db is initialized in context manager"""
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
            self.client = None
            self.db = None

    def _load_validation_schema(self, schema_filename):
        """
        Load JSON Schema from the schema directory or its subdirectories.
        :param schema_filename: Name of the schema file
        :return: Parsed JSON Schema
        """
        # Set base schema directory
        base_path = Path(__file__).parent.parent / 'schema'

        # Traverse all subdirectories to find the schema file
        schema_path = next(base_path.rglob(schema_filename), None)  # Use rglob to recursively search

        logger.debug(f"Searching for schema: {schema_filename} in {base_path}")
        if not schema_path or not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_filename} in {base_path} or its subdirectories.")

        # Load and return the JSON schema
        logger.debug(f"Found schema file at: {schema_path}")
        with open(schema_path, 'r') as f:
            return json.load(f)

    def validate_data(self, data, schema):
        """
        Validate data against JSON Schema.
        :param data: Data to be validated
        :param schema: JSON Schema for validation
        """
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            logger.error(f"Data validation failed: {e.message}")
            raise ValueError(f"Data validation error: {e.message}")

    def ensure_validation(self, collection_name, schema_filename):
        """
        Ensure the collection exists and load JSON Schema for application-level validation.
        :param collection_name: Name of the collection
        :param schema_filename: JSON Schema file name
        """
        try:
            self.db.create_collection(collection_name)
            logger.info(f"Collection '{collection_name}' created.")
        except CollectionInvalid:
            logger.info(f"Collection '{collection_name}' already exists.")

        schema = self._load_validation_schema(schema_filename)
        logger.warning(f"Schema validation is not supported in the database. "
                       f"Validation will be performed at the application level for collection: {collection_name}")

        return schema

    def insert_one(self, collection_name, data, schema=None):
        """
        Insert a single document into a collection with optional schema validation.
        """
        if self.db is None:  # 显式比较 None
            raise RuntimeError("Database connection is not initialized. Did you forget to use the context manager?")

        if schema:
            self.validate_data(data, schema)

        logger.info(f"Inserting one document into collection: {collection_name}")
        data["is_deleted"] = False
        collection = self.db[collection_name]
        result = collection.insert_one(data)
        logger.info(f"Document inserted with ID: {result.inserted_id}")
        return result.inserted_id

    def update_one(self, collection_name, query, update):
        """
        Update a single document in a collection.
        """
        if not isinstance(update, dict):
            raise ValueError("Update data must be a dictionary.")

        # 检查更新文档中是否已经包含 `$set`
        if "$set" in update and isinstance(update["$set"], dict):
            # 可能是重复封装，直接返回错误
            for key in update["$set"]:
                if key.startswith("$"):
                    raise ValueError(f"Illegal field name in update_data: {key}")

        logger.debug(f"Updating {collection_name} with query: {query}, update: {update}")
        collection = self.db[collection_name]
        return collection.update_one(query, update)

    def find_one(self, collection_name, query, include_deleted=False, projection=None):
        """
        Find a single document, ignoring soft-deleted documents by default.

        Args:
            collection_name (str): The name of the collection to query.
            query (dict): The query to filter documents.
            include_deleted (bool): Whether to include soft-deleted documents.
            projection (dict): A projection dict to include or exclude specific fields.
                               E.g., {"password": 0} to exclude the password field.

        Returns:
            dict: The found document, or None if no document matches the query.
        """
        logger.info(f"Finding one document in collection: {collection_name} with query: {query}")

        # Exclude soft-deleted documents unless explicitly allowed
        if not include_deleted:
            query["is_deleted"] = False

        # Execute the query with the optional projection
        collection = self.db[collection_name]
        result = collection.find_one(query, projection=projection)
        logger.info(f"Find one result: {result}")
        return result

    def insert_many(self, collection_name, data_list, schema=None):
        """
        Insert multiple documents into a collection with optional schema validation.
        :param collection_name: Target collection name
        :param data_list: List of document data to insert
        :param schema: JSON Schema for validation
        """
        if schema:
            for data in data_list:
                self.validate_data(data, schema)

        logger.info(f"Inserting many documents into collection: {collection_name}")
        for data in data_list:
            data["is_deleted"] = False
        collection = self.db[collection_name]
        result = collection.insert_many(data_list)
        logger.info(f"Documents inserted with IDs: {result.inserted_ids}")
        return result.inserted_ids

    def delete_one(self, collection_name, query, soft_delete=True):
        """
        Delete a single document, performing a soft delete by default.
        :param collection_name: Target collection name
        :param query: Query to identify the document
        :param soft_delete: If True, perform a soft delete by setting is_deleted to True
        """
        logger.info(f"Deleting one document in collection: {collection_name} with query: {query}")
        collection = self.db[collection_name]

        if soft_delete:
            update_data = {"is_deleted": True}
            result = collection.update_one(query, {"$set": update_data})
            logger.info(f"Soft delete result: {result.modified_count} document(s) modified")
        else:
            result = collection.delete_one(query)
            logger.info(f"Physical delete result: {result.deleted_count} document(s) deleted")
        return result

    def find_many(self, collection_name, query, include_deleted=False, sort=None, limit=0, skip=0):
        """
        Find multiple documents, supporting sorting, limit, and skip options.
        :param collection_name: Target collection name
        :param query: Query to filter documents
        :param include_deleted: If False, exclude soft-deleted documents
        :param sort: Sorting criteria (e.g., [("field", pymongo.ASCENDING)])
        :param limit: Number of documents to return
        :param skip: Number of documents to skip
        """
        logger.info(f"Finding many documents in collection: {collection_name} with query: {query}")
        if not include_deleted:
            query["is_deleted"] = False
        collection = self.db[collection_name]

        cursor = collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)

        result_list = list(cursor)
        logger.info(f"Find many result: {len(result_list)} document(s) found")
        return result_list

    def insert_many(self, collection_name, data_list, schema=None):
        """
        Insert multiple documents into the specified collection, optionally validating against a JSON Schema.
        :param collection_name: Target collection name
        :param data_list: List of documents to insert
        :param schema: JSON Schema for validation
        """
        logger.info(f"Inserting many documents into collection: {collection_name}")
        if schema:
            for data in data_list:
                self.validate_data(data, schema)

        for data in data_list:
            data["is_deleted"] = False
        collection = self.db[collection_name]
        result = collection.insert_many(data_list)
        logger.info(f"Documents inserted with IDs: {result.inserted_ids}")
        return result.inserted_ids

    def count_documents(self, collection_name, query):
        """
        Count the number of documents that match the query.
        :param collection_name: Target collection name
        :param query: Query to filter documents
        :return: Count of matching documents
        """
        logger.info(f"Counting documents in collection: {collection_name} with query: {query}")
        collection = self.db[collection_name]
        count = collection.count_documents(query)
        logger.info(f"Count result: {count} document(s) found")
        return count

    def delete_many(self, collection_name, query, soft_delete=True):
        """
        Delete multiple documents, performing a soft delete by default.
        :param collection_name: Target collection name
        :param query: Query to identify the documents
        :param soft_delete: If True, perform a soft delete by setting is_deleted to True
        """
        logger.info(f"Deleting many documents in collection: {collection_name} with query: {query}")
        collection = self.db[collection_name]

        if soft_delete:
            update_data = {"is_deleted": True}
            result = collection.update_many(query, {"$set": update_data})
            logger.info(f"Soft delete result: {result.modified_count} document(s) modified")
        else:
            result = collection.delete_many(query)
            logger.info(f"Physical delete result: {result.deleted_count} document(s) deleted")
        return result
