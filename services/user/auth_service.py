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


class AuthService:
    def __init__(self):
        self.user_service = UserService()
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
            "user_id": str(user_id),  # 转换 ObjectId 为字符串
            "exp": datetime.now() + timedelta(hours=24)  # Token expiration time
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
                # 将 user_id 存入 request.state 中
                request.state.user_id = user_id
                return await func(request, *args, **kwargs)
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        return wrapper
