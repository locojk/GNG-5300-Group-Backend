"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
from marshmallow import Schema, fields, ValidationError, validates
from pydantic import BaseModel, EmailStr, Field
from daos.user.users_dao import UserDAO


# 验证逻辑嵌入到接口文件中
class RegistrationValidationSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)  # 自动验证邮箱格式
    password = fields.Str(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_dao = UserDAO()  # 初始化时创建 DAO 实例

    @validates('password')
    def validate_password(self, value):
        # 密码复杂性验证
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

    @validates('email')
    def validate_email(self, value):
        if self.user_dao.get_user_by_email(value):
            raise ValidationError("Email already exists")


class LoginValidationSchema(Schema):
    email = fields.Email(required=True)  # 自动验证邮箱格式
    password = fields.Str(required=True)

    @validates('password')
    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long")


# 更新用户资料验证（Pydantic）
class UserProfileUpdateSchema(BaseModel):
    username: str = Field(None, max_length=50)
    email: EmailStr = None
    first_name: str = Field(None, max_length=50)
    last_name: str = Field(None, max_length=50)
    weight_kg: float = Field(None, ge=0)  # 必须大于或等于 0
    height_cm: float = Field(None, ge=0)  # 必须大于或等于 0
    age: int = Field(None, ge=0, le=150)  # 必须是 0 到 150 之间的整数
