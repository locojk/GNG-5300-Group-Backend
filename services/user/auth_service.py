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

security = HTTPBearer()  # 解析 Authorization 头中的 Bearer Token
from services.user.user_service import UserService

from utils.env_loader import load_platform_specific_env

load_platform_specific_env()
from utils.logger import Logger

logger = Logger(__name__)


class AuthService:
    def __init__(self):
        self.user_service = UserService()
        self.secret_key = os.getenv('SECRET_KEY')
        if not self.secret_key:
            raise ValueError("SECRET_KEY is not set in environment variables")
        self.algorithm = os.getenv('ALGORITHM', 'HS256')
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register_user(self, username: str, email: str, password: str) -> str:
        # hashed_password = self.password_context.hash(password)
        user_id = self.user_service.register_user(username, email, password)
        return user_id

    def login_user(self, email: str, password: str) -> dict:
        user_id, username = self.user_service.login_user(email, password)
        tokens = self._generate_tokens(str(user_id))
        return {"user_id": user_id, "username": username, "token": tokens}

    def _generate_tokens(self, user_id: str) -> str:
        now = datetime.now()
        refresh_token_payload = {
            'user_id': user_id,  # 包含 user_id
            'exp': int((now + timedelta(days=7)).timestamp())  # Refresh Token 有效期 7 天
        }
        refresh_token = jwt.encode(refresh_token_payload, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Generated refresh_token -> {refresh_token}")
        return refresh_token

    def verify_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def requires_auth(self, func):
        """装饰器：验证请求中的 JWT Token"""

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
    user_id = AuthService().verify_token(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6MTczMzUyMDg3Mn0.aekSzrgOic0miyr_yNkVO8WxM5kn3kmOgltdL_skmCA')
    print(f"user_id -> {user_id}")
