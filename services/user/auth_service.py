"""
User Authentication Service

@Date: 2024-10-05
@Author: Adam Lyu
"""
import os

from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from services.user.user_service import UserService
from utils.env_loader import load_platform_specific_env

load_platform_specific_env()


class AuthService:
    def __init__(self, user_service: UserService = Depends()):
        self.user_service = user_service
        self.secret_key = os.getenv('SECRET_KEY')
        self.algorithm = os.getenv('ALGORITHM')
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register_user(self, username: str, email: str, password: str) -> str:
        """Register a new user"""
        # Hash the password before saving
        hashed_password = self.password_context.hash(password)
        user_id = self.user_service.register_user(username, email, hashed_password)
        return user_id

    def login_user(self, email: str, password: str) -> dict:
        """Validate login and return JWT"""
        # Validate user credentials
        user_id = self.user_service.login_user(email, password)
        # Generate JWT
        token = self._generate_jwt(user_id)
        return {"user_id": user_id, "token": token}

    def _generate_jwt(self, user_id: str) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)  # Token expiration time
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> str:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
