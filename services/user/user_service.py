from datetime import time

from daos.user.users_dao import UserDAO
from flask_bcrypt import Bcrypt
from utils.auth_helpers import generate_reset_token
from utils.email_helpers import send_reset_email
from utils.logger import Logger

logger = Logger(__name__)
bcrypt = Bcrypt()


class UserService:
    def __init__(self):
        self.user_dao = UserDAO()

    # Email and password-based user registration
    def register_user(self, username, email, password):
        if self.user_dao.get_user_by_email(email):
            raise ValueError("Email already exists")

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        logger.debug(f"Generated Hashed Password: {hashed_password}")
        user_id = self.user_dao.insert_user(username, email, hashed_password)
        return user_id

    # User login with email and password
    def login_user(self, email, password):
        user = self.user_dao.get_user_by_email(email)
        logger.debug(f"user -> {user}")
        logger.debug(f"Stored Hash: {user['password']}")
        logger.debug(f"Password to Check: {password}")

        try:
            if user and bcrypt.check_password_hash(user['password'], password):
                self.user_dao.update_last_login(user['_id'])
                return user['_id'], user.get('username')  # Return user_id and username
        except ValueError as e:
            logger.error(f"Error during password check: {e}")
            raise

        raise ValueError("Incorrect email or password")


    # Update user information
    def update_user_info(self, user_id, **kwargs):
        """
        Update user information dynamically.

        Args:
            user_id (str): The ID of the user.
            kwargs: Key-value pairs of fields to update.

        Example:
            update_user_info("user_id", first_name="John", last_name="Doe")
        """
        if not kwargs:
            logger.warning("No fields provided for update")
            raise ValueError("No fields provided for update")

        logger.debug(f"Updating user {user_id} with data: {kwargs}")
        self.user_dao.update_user_info(user_id, kwargs)

    # Update email verification status
    def verify_user_email(self, user_id):
        self.user_dao.verify_email(user_id)

    # Request a password reset
    def request_password_reset(self, email):
        user = self.user_dao.get_user_by_email(email)
        if not user:
            raise ValueError("User does not exist")
        token = generate_reset_token(user['_id'])
        send_reset_email(user, token)

    # Change user status
    def change_user_status(self, user_id, status):
        if status not in ['active', 'inactive', 'banned', 'deleted']:
            raise ValueError("Invalid status")
        self.user_dao.update_user_status(user_id, status)

    # Change user role
    def change_user_role(self, user_id, role):
        if role not in ['user', 'admin', 'moderator', 'vip']:
            raise ValueError("Invalid role")
        self.user_dao.update_user_info(user_id, role=role)

    # Update failed login attempts
    def update_failed_login_attempt(self, user_id):
        user = self.user_dao.get_user_by_id(user_id)
        if user:
            failed_attempts = user['failed_login_attempts'] + 1
            self.user_dao.update_user_info(user_id, failed_login_attempts=failed_attempts,
                                           last_failed_login=time.strftime('%Y-%m-%d %H:%M:%S'))

    # Reset failed login attempts after successful login
    def reset_failed_login_attempts(self, user_id):
        self.user_dao.update_user_info(user_id, failed_login_attempts=0, last_failed_login=None)

    # Retrieve user information
    def get_user_info(self, user_id):
        return self.user_dao.get_user_by_id(user_id)
