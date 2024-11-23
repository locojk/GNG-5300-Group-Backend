import hashlib
import time
import pymongo
from bson.objectid import ObjectId
from daos.mongodb_client import MongoDBClient
from utils.logger import Logger

# 初始化日志记录器
logger = Logger(__name__)


class UserDAO:
    def __init__(self):
        self.db_client = MongoDBClient()
        self.collection_name = 'users'

        # 应用 JSON Schema 验证规则并创建索引
        with self.db_client as db_client:
            logger.info(f"Initializing validation and index for collection: {self.collection_name}")
            db_client.ensure_validation(self.collection_name, 'users_schema.json')
            db_client.db[self.collection_name].create_index([("word", pymongo.ASCENDING)], unique=True)

    def get_user_by_username(self, username):
        """Retrieve user information by username"""
        logger.info(f"Fetching user by username: {username}")
        with self.db_client as db_client:
            user = db_client.find_one(self.collection_name, {"username": username})
            if user:
                logger.debug(f"User found: {user}")
            else:
                logger.warning(f"No user found with username: {username}")
            return user

    def get_user_by_email(self, email):
        """Retrieve user information by email"""
        logger.info(f"Fetching user by email: {email}")
        with self.db_client as db_client:
            user = db_client.find_one(self.collection_name, {"email": email})
            if user:
                logger.debug(f"User found: {user}")
            else:
                logger.warning(f"No user found with email: {email}")
            return user

    def insert_user(self, username, email, password):
        """Register a new user"""
        logger.info(f"Attempting to insert new user: {username}, {email}")
        with self.db_client as db_client:
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "status": "active",
                "email_verified": False,
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            user_id = db_client.insert_one(self.collection_name, user_data)
            logger.audit_log(
                user_id=str(user_id),
                action="insert",
                resource="users",
                status="success",
                details=f"Inserted user {username} with email {email}"
            )
            return user_id

    def update_last_login(self, user_id):
        """Update the last login timestamp"""
        logger.info(f"Updating last login for user_id: {user_id}")
        query = {"_id": ObjectId(user_id)}
        update_data = {"last_login": time.strftime('%Y-%m-%d %H:%M:%S')}
        logger.debug(f"Query: {query}, Update data: {update_data}")

        # 直接传入正确格式的更新数据
        with self.db_client as db_client:
            result = db_client.update_one(
                self.collection_name,
                query,
                {"$set": update_data}  # 确保只封装一次 $set
            )
            logger.audit_log(
                user_id=str(user_id),
                action="update_last_login",
                resource="users",
                status="success",
                details=f"Last login updated for user_id {user_id}"
            )
            return result

    def set_password_reset_token(self, email):
        """Set password reset token and expiration"""
        logger.info(f"Generating password reset token for email: {email}")
        token = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()
        expires = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 3600))  # Expires in 1 hour
        with self.db_client as db_client:
            result = db_client.update_one(
                self.collection_name,
                {"email": email},
                {"$set": {"password_reset_token": token, "password_reset_expires": expires}}
            )
            logger.audit_log(
                user_id=email,
                action="set_password_reset_token",
                resource="users",
                status="success" if result.modified_count > 0 else "failed",
                details=f"Password reset token set for {email}"
            )
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
            logger.audit_log(
                user_id=str(user_id),
                action="verify_email",
                resource="users",
                status="success",
                details=f"Email verified for user_id {user_id}"
            )
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
            logger.audit_log(
                user_id=str(user_id),
                action="update_status",
                resource="users",
                status="success",
                details=f"User status updated to {status}"
            )
            return result

    def get_user_by_id(self, user_id):
        """Retrieve user information by ObjectId"""
        logger.info(f"Fetching user by user_id: {user_id}")
        with self.db_client as db_client:
            try:
                user = db_client.find_one(self.collection_name, {"_id": ObjectId(user_id)})
                logger.debug(f"User retrieved: {user}")
                return user
            except Exception as e:
                logger.error(f"Error fetching user by id: {e}")
                raise ValueError(f"Error fetching user by id: {e}")


if __name__ == "__main__":
    import secrets

    # 生成一个 32 字节长度的随机密钥（推荐用于 SECRET_KEY）
    secret_key = secrets.token_hex(32)
    print(f"Generated SECRET_KEY: {secret_key}")
