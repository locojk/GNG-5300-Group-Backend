"""
User Authentication API

@Date: 2024-10-20
@Author: Adam Lyu
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Request, Depends
from pydantic import ValidationError
from services.user.auth_service import AuthService
from services.user.validation import RegistrationValidationSchema, LoginValidationSchema
# from fastapi_mail import FastMail, MessageSchema
from utils.logger import logger  # Assumes a logger utility is available

# from utils.mail_config import mail_config  # Assumes FastMail configuration is here

router = APIRouter()
auth_service = AuthService()

# mail = FastMail(mail_config)

# Asynchronous email sending
# async def send_email(background_tasks: BackgroundTasks, msg: MessageSchema):
#     background_tasks.add_task(mail.send_message, msg)

# User registration API
@router.post('/register')
async def register(data: dict, background_tasks: BackgroundTasks):
    schema = RegistrationValidationSchema()

    try:
        # Validate data
        schema.load(data)
        username = data['username']
        email = data['email']
        password = data['password']

        user_id = auth_service.register_user(username, email, password)
        logger.info(f"User registered successfully: {user_id}")
        return {"message": "Registration successful", "user_id": user_id}
    except ValidationError as err:
        logger.error(f"Validation error during registration: {err.messages}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.messages)
    except ValueError as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# User login API
@router.post('/login')
async def login(data: dict):
    schema = LoginValidationSchema()

    try:
        # Validate data
        schema.load(data)
        email = data['email']
        password = data['password']

        result = auth_service.login_user(email, password)
        logger.info(f"User logged in successfully: {result['user_id']}")
        return {"message": "Login successful", "user_id": result['user_id'], "token": result['token']}
    except ValidationError as err:
        logger.error(f"Validation error during login: {err.messages}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.messages)
    except ValueError as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


# Email verification API
@router.post('/verify-email')
async def verify_email(data: dict):
    user_id = data.get('user_id')

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is required")

    try:
        auth_service.user_service.verify_user_email(user_id)
        logger.info(f"Email verified successfully for user_id: {user_id}")
        return {"message": "Email verification successful"}
    except ValueError as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

