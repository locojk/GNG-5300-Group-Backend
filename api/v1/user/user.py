"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
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


# User registration route
@router.post('/register')
@handle_response
async def register(data: dict = Body(...)):
    schema = RegistrationValidationSchema()
    # Validate data using marshmallow
    validated_data = schema.load(data)

    # Extract fields from validated data
    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    # Register user
    user_id = auth_service.register_user(username, email, password)
    logger.info(f"User registered successfully: {user_id}")
    return {"message": "Registration successful", "user_id": user_id}


# User login route
@router.post('/login')
@handle_response
async def login(data: dict = Body(...)):
    schema = LoginValidationSchema()
    # Validate data using marshmallow
    validated_data = schema.load(data)

    # Extract fields from validated data
    email = validated_data['email']
    password = validated_data['password']

    # User login
    result = auth_service.login_user(email, password)
    logger.info(f"User logged in successfully: {result['user_id']}")
    return {
        "message": "Login successful",
        "user_id": result['user_id'],
        "username": result['username'],
        "token": result['token'],
    }


@router.get("/profile")
@handle_response
@auth_service.requires_auth
async def get_user_profile(request: Request, user_id: str):
    """
    Retrieve user profile
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
    Update user profile
    """
    # Retrieve user_id from request.state
    user_id = request.state.user_id

    # Get data from the request
    data = await request.json()

    # Validate data
    validated_data = UserProfileUpdateSchema(**data).dict(exclude_none=True)

    # Update user information
    user_service.update_user_info(user_id, **validated_data)

    return {"message": "User profile updated successfully"}
