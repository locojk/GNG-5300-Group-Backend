import hashlib
import time
from utils.logger import logger
from bson.objectid import ObjectId
from daos.mongodb_client import MongoDBClient


class UserDAO:
    def __init__(self):
        self.client = MongoDBClient()
        self.collection_name = 'users'

    def get_user_by_username(self, username):
        """Retrieve user information by username"""
        with self.client as db_client:
            return db_client.find_one(self.collection_name, {"username": username})

    def get_user_by_email(self, email):
        """Retrieve user information by email"""
        with self.client as db_client:
            return db_client.find_one(self.collection_name, {"email": email})

    def insert_user(self, username, email, password):
        """Register a new user"""
        with self.client as db_client:
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "status": "active",
                "email_verified": False,
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            return db_client.insert_one(self.collection_name, user_data)

    def update_last_login(self, user_id):
        """Update the last login timestamp"""
        with self.client as db_client:
            return db_client.update_one(
                self.collection_name,
                {"_id": user_id},
                {"last_login": time.strftime('%Y-%m-%d %H:%M:%S')}
            )

    def set_password_reset_token(self, email):
        """Set password reset token and expiration"""
        token = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()
        expires = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 3600))  # Expires in 1 hour
        with self.client as db_client:
            return db_client.update_one(
                self.collection_name,
                {"email": email},
                {
                    "password_reset_token": token,
                    "password_reset_expires": expires
                }
            )

    def verify_email(self, user_id):
        """Verify user's email"""
        with self.client as db_client:
            return db_client.update_one(
                self.collection_name,
                {"_id": user_id},
                {"email_verified": True}
            )

    def update_user_status(self, user_id, status):
        """Update user status"""
        if status not in ['active', 'inactive', 'banned', 'deleted']:
            raise ValueError("Invalid status")
        with self.client as db_client:
            return db_client.update_one(
                self.collection_name,
                {"_id": user_id},
                {"status": status}
            )

    def update_user_info(self, user_id, **kwargs):
        """Update user information"""
        if not kwargs:
            raise ValueError("No fields to update")
        with self.client as db_client:
            return db_client.update_one(
                self.collection_name,
                {"_id": user_id},
                kwargs
            )

    def deactivate_user(self, user_id):
        """Deactivate user account (soft delete)"""
        return self.update_user_status(user_id, status='deleted')

    def get_user_by_id(self, user_id):
        """Retrieve user information by ObjectId"""
        with self.client as db_client:
            try:
                user = db_client.find_one(self.collection_name, {"_id": ObjectId(user_id)})
                return user
            except Exception as e:
                # Add logging or error handling
                raise ValueError(f"Error fetching user by id: {e}")
