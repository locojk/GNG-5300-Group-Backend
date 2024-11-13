"""
User Authentication Service

@Date: 2024-10-05
@Author: Adam Lyu
"""

import jwt
import datetime
from flask_bcrypt import Bcrypt
from flask import current_app
from services.user.user_service import UserService

bcrypt = Bcrypt()
user_service = UserService()


class AuthService:
    def __init__(self):
        self.user_service = user_service

    def register_user(self, username, email, password):
        # Use UserService to register a new user
        user_id = self.user_service.register_user(username, email, password)
        return user_id

    def login_user(self, email, password):
        # Use UserService to validate login
        user_id = self.user_service.login_user(email, password)

        # Generate JWT
        token = self._generate_jwt(user_id)
        return {"user_id": user_id, "token": token}

    def _generate_jwt(self, user_id):
        # Retrieve SECRET_KEY and ALGORITHM from config
        secret_key = current_app.config['SECRET_KEY']
        algorithm = current_app.config.get('ALGORITHM', 'HS256')

        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expiration time
        }
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        return token

    def verify_token(self, token):
        try:
            # Retrieve SECRET_KEY and ALGORITHM from config
            secret_key = current_app.config['SECRET_KEY']
            algorithm = current_app.config.get('ALGORITHM', 'HS256')

            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            user_id = payload.get('user_id')
            return user_id
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
