from fastapi import APIRouter, Body, Request, HTTPException
from services.user.user_service import UserService
from utils.logger import Logger
from services.user.auth_service import AuthService
from utils.decorators import handle_response
from services.user.validation import RegistrationValidationSchema, LoginValidationSchema, UserProfileUpdateSchema

logger = Logger(__name__)
router = APIRouter()
auth_service = AuthService()
user_service = UserService()


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


@router.get("/profile")
@handle_response
@auth_service.requires_auth
async def get_user_profile(request: Request, user_id: str):
    """
    获取用户个人资料
    """
    user_info = user_service.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User profile fetched successfully", "data": user_info}


@router.put("/profile/update")
@handle_response
@auth_service.requires_auth
async def update_user_profile(request: Request):
    """
    更新用户个人资料
    """
    # 从 request.state 中获取 user_id
    user_id = request.state.user_id

    # 获取请求中的数据
    data = await request.json()

    # 验证数据
    validated_data = UserProfileUpdateSchema(**data).dict(exclude_none=True)

    # 更新用户信息
    user_service.update_user_info(user_id, **validated_data)

    return {"message": "User profile updated successfully"}
