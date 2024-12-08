"""
Validation Schemas for User Operations

@Date: 2024-11-23
@Author: Adam Lyu
"""
from marshmallow import Schema, fields, ValidationError, validates
from pydantic import BaseModel, EmailStr, Field
from daos.user.users_dao import UserDAO


# Validation logic embedded in the schema

class RegistrationValidationSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)  # Automatically validates email format
    password = fields.Str(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_dao = UserDAO()  # Initialize DAO instance

    @validates('password')
    def validate_password(self, value):
        """Validate password complexity"""
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in value):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one digit")

    @validates('email')
    def validate_email(self, value):
        """Check if email already exists in the database"""
        if self.user_dao.get_user_by_email(value):
            raise ValidationError("Email already exists")


class LoginValidationSchema(Schema):
    email = fields.Email(required=True)  # Automatically validates email format
    password = fields.Str(required=True)

    @validates('password')
    def validate_password(self, value):
        """Validate password length"""
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long")


# Update user profile validation (Pydantic)

class UserProfileUpdateSchema(BaseModel):
    username: str = Field(None, max_length=50)
    email: EmailStr = None
    first_name: str = Field(None, max_length=50)
    last_name: str = Field(None, max_length=50)
    weight_kg: float = Field(None, ge=0)  # Must be greater than or equal to 0
    height_cm: float = Field(None, ge=0)  # Must be greater than or equal to 0
    age: int = Field(None, ge=0, le=150)  # Must be an integer between 0 and 150
