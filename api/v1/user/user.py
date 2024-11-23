from fastapi import APIRouter, Body
from utils.logger import Logger
from services.user.auth_service import AuthService
from utils.decorators import handle_response
from services.user.validation import RegistrationValidationSchema, LoginValidationSchema

logger = Logger(__name__)
router = APIRouter()
auth_service = AuthService()


# 用户注册路由
@router.post('/register')
@handle_response
async def register(data: dict = Body(...)):
    schema = RegistrationValidationSchema()
    # 使用 marshmallow 验证数据
    validated_data = schema.load(data)

    # 从验证后的数据中获取字段
    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    # 注册用户
    user_id = auth_service.register_user(username, email, password)
    logger.info(f"User registered successfully: {user_id}")
    return {"message": "Registration successful", "user_id": user_id}


# 用户登录路由
@router.post('/login')
@handle_response
async def login(data: dict = Body(...)):
    schema = LoginValidationSchema()
    # 使用 marshmallow 验证数据
    validated_data = schema.load(data)

    # 从验证后的数据中获取字段
    email = validated_data['email']
    password = validated_data['password']

    # 用户登录
    result = auth_service.login_user(email, password)
    logger.info(f"User logged in successfully: {result['user_id']}")
    return {"message": "Login successful", "user_id": result['user_id'], "token": result['token']}

