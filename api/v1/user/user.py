"""
@Time ： 2024-10-05
@Auth ： Adam Lyu
"""

from utils.logger import logger  # 假设你的日志工具在 utils/logger.py 中
from fastapi import APIRouter, BackgroundTasks
from services.user.auth_service import AuthService
from services.user.validation import RegistrationValidationSchema, LoginValidationSchema
from utils.decorators import handle_response

router = APIRouter()
auth_service = AuthService()


# 使用装饰器包装路由函数
@router.post('/register')
@handle_response
async def register(data: dict):
    schema = RegistrationValidationSchema()

    # 验证并处理数据
    schema.load(data)
    username = data['username']
    email = data['email']
    password = data['password']

    user_id = auth_service.register_user(username, email, password)
    logger.info(f"User registered successfully: {user_id}")
    return {"message": "Registration successful", "user_id": user_id}


@router.post('/login')
@handle_response
async def login(data: dict):
    schema = LoginValidationSchema()

    # 验证并处理数据
    schema.load(data)
    email = data['email']
    password = data['password']

    result = auth_service.login_user(email, password)
    logger.info(f"User logged in successfully: {result['user_id']}")
    return {"message": "Login successful", "user_id": result['user_id'], "token": result['token']}
