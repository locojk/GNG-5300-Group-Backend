import hashlib
from datetime import datetime
import pymongo
from bson.objectid import ObjectId
from daos.mongodb_client import MongoDBClient
from utils.logger import Logger

logger = Logger(__name__)

class UserDAO:
    def __init__(self):
        self.db_client = MongoDBClient()
        self.collection_name = 'users'

        # 初始化集合验证规则和索引
        with self.db_client as db_client:
            logger.info(f"Setting up validation and index for collection: {self.collection_name}")
            db_client.ensure_validation(self.collection_name, 'users_schema.json')
            db_client.db[self.collection_name].create_index(
                [("email", pymongo.ASCENDING)], unique=True, name="email_1"
            )

    def get_user_by_username(self, username):
        """Retrieve user information by username"""
        logger.debug(f"Fetching user by username: {username}")
        with self.db_client as db_client:
            user = db_client.find_one(self.collection_name, {"username": username})
            return user

    def get_user_by_email(self, email):
        """Retrieve user information by email"""
        logger.debug(f"Fetching user by email: {email}")
        with self.db_client as db_client:
            user = db_client.find_one(self.collection_name, {"email": email})
            return user

    def insert_user(self, username, email, password):
        """Register a new user"""
        logger.info(f"Inserting new user: {username}, {email}")
        with self.db_client as db_client:
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "status": "active",
                "email_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            try:
                user_id = db_client.insert_one(self.collection_name, user_data)
                logger.info(f"User inserted successfully: {user_id}")
                return user_id
            except pymongo.errors.DuplicateKeyError:
                logger.error(f"Duplicate email detected: {email}")
                raise ValueError("Email already exists")

    def update_last_login(self, user_id):
        """Update the last login timestamp"""
        logger.info(f"Updating last login for user_id: {user_id}")
        query = {"_id": ObjectId(user_id)}
        update_data = {"last_login": datetime.utcnow().isoformat()}
        with self.db_client as db_client:
            result = db_client.update_one(self.collection_name, query, {"$set": update_data})
            if result.modified_count > 0:
                logger.info(f"Last login updated for user_id: {user_id}")
            return result

    def set_password_reset_token(self, email):
        """Set password reset token and expiration"""
        logger.info(f"Generating password reset token for email: {email}")
        token = hashlib.sha256(f"{email}{datetime.utcnow().timestamp()}".encode()).hexdigest()
        expires = datetime.utcnow().isoformat()
        with self.db_client as db_client:
            result = db_client.update_one(
                self.collection_name,
                {"email": email},
                {"$set": {"password_reset_token": token, "password_reset_expires": expires}}
            )
            logger.info(f"Password reset token set for email: {email}")
            return result

    def verify_email(self, user_id):
        """Verify user's email"""
        logger.info(f"Verifying email for user_id: {user_id}")
        with self.db_client as db_client:
            result = db_client.update_one(
                self.collection_name,
                {"_id": ObjectId(user_id)},
                {"$set": {"email_verified": True}}
            )
            if result.modified_count > 0:
                logger.info(f"Email verified for user_id: {user_id}")
            return result

    def update_user_status(self, user_id, status):
        """Update user status"""
        logger.info(f"Updating status for user_id: {user_id} to {status}")
        if status not in ['active', 'inactive', 'banned', 'deleted']:
            logger.error(f"Invalid status: {status}")
            raise ValueError("Invalid status")
        with self.db_client as db_client:
            result = db_client.update_one(
                self.collection_name,
                {"_id": ObjectId(user_id)},
                {"$set": {"status": status}}
            )
            logger.info(f"User status updated for user_id: {user_id}")
            return result

    def get_user_by_id(self, user_id):
        """Retrieve user information by ObjectId, excluding sensitive fields"""
        logger.debug(f"Fetching user by user_id: {user_id}")
        with self.db_client as db_client:
            user = db_client.find_one(
                self.collection_name,
                {"_id": ObjectId(user_id)},
                projection={"password": 0}
            )
            return user

    def update_user_info(self, user_id, update_fields):
        """Dynamically update user information"""
        if not isinstance(update_fields, dict) or not update_fields:
            logger.error("update_fields must be a non-empty dictionary")
            raise ValueError("update_fields must be a non-empty dictionary")
        update_fields["updated_at"] = datetime.utcnow().isoformat()
        query = {"_id": ObjectId(user_id)}
        with self.db_client as db_client:
            result = db_client.update_one(self.collection_name, query, {"$set": update_fields})
            if result.matched_count > 0:
                logger.info(f"User updated successfully: {user_id}")
            else:
                logger.warning(f"No user found to update: {user_id}")
            return result

