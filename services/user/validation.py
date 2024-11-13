"""
User Registration and Login Validation Schemas

@Date: 2024-10-05
@Author: Adam Lyu
"""

from marshmallow import Schema, fields, ValidationError, validates


class RegistrationValidationSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)  # Email field automatically validates format
    password = fields.Str(required=True)

    @validates('password')
    def validate_password(self, value):
        # Check password length and complexity
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in value):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one digit")
        if not any(char in "!@#$%^&*()_+-=[]{}|;':,.<>?/`~" for char in value):
            raise ValidationError("Password must contain at least one special character")


class LoginValidationSchema(Schema):
    email = fields.Email(required=True)  # Email field automatically validates format
    password = fields.Str(required=True)

    @validates('password')
    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long")
