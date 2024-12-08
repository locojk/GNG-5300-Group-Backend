"""
User Authentication Service

@Date: 2024-10-05
@Author: Adam Lyu
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from jose import jwt, JWTError
from fastapi import HTTPException, Request
from functools import wraps
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.user.user_service import UserService
from utils.env_loader import load_platform_specific_env
from utils.logger import Logger

# Load environment variables
load_platform_specific_env()
logger = Logger(__name__)

security = HTTPBearer()  # Parses Bearer Token from the Authorization header


class AuthService:
    def __init__(self):
        self.user_service = UserService()
        self.secret_key = os.getenv('SECRET_KEY')
        if not self.secret_key:
            raise ValueError("SECRET_KEY is not set in environment variables")
        self.algorithm = os.getenv('ALGORITHM', 'HS256')
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register_user(self, username: str, email: str, password: str) -> str:
        """
        Register a new user with a hashed password.

        :param username: The username of the user
        :param email: The user's email
        :param password: The user's password
        :return: The registered user ID
        """
        user_id = self.user_service.register_user(username, email, password)
        return user_id

    def login_user(self, email: str, password: str) -> dict:
        """
        Authenticate a user and generate a token.

        :param email: The user's email
        :param password: The user's password
        :return: A dictionary containing the user ID, username, and token
        """
        user_id, username = self.user_service.login_user(email, password)
        tokens = self._generate_tokens(str(user_id))
        return {"user_id": user_id, "username": username, "token": tokens}

    def _generate_tokens(self, user_id: str) -> str:
        """
        Generate a refresh token for the given user ID.

        :param user_id: The user ID
        :return: A refresh token
        """
        now = datetime.now()
        refresh_token_payload = {
            'user_id': user_id,  # Include user ID
            'exp': int((now + timedelta(days=7)).timestamp())  # Token expiration set to 7 days
        }
        refresh_token = jwt.encode(refresh_token_payload, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Generated refresh_token -> {refresh_token}")
        return refresh_token

    def verify_token(self, token: str) -> str:
        """
        Verify a JWT token.

        :param token: The JWT token
        :return: The user ID from the token payload
        :raises HTTPException: If the token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def requires_auth(self, func):
        """
        Decorator: Validates the JWT token in the request.

        :param func: The function to wrap
        :return: The wrapped function
        """

        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

            token = authorization.split(" ")[1]

            try:
                user_id = self.verify_token(token)
                request.state.user_id = user_id
                return await func(request, *args, **kwargs)
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        return wrapper


if __name__ == '__main__':
    # Test token verification
    auth_service = AuthService()
    try:
        user_id = auth_service.verify_token(
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsImV4cCI6MTczMzUyMDg3Mn0.aekSzrgOic0miyr_yNkVO8WxM5kn3kmOgltdL_skmCA'
        )
        print(f"user_id -> {user_id}")
    except HTTPException as e:
        print(f"Error: {e.detail}")
