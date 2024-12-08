"""
Password Reset Token Generator and Verifier

@Date: 2024-09-11
@Author: Adam Lyu
"""

import os
from itsdangerous import URLSafeTimedSerializer
from utils.env_loader import load_platform_specific_env

load_platform_specific_env()


# Retrieve SECRET_KEY from environment variable or fallback
def get_secret_key():
    return os.getenv('SECRET_KEY', 'your-default-secret-key')


# Retrieve ALGORITHM from environment variable, default to 'HS256'
def get_algorithm():
    return os.getenv('ALGORITHM', 'HS256')


def generate_reset_token(user_id):
    # Dynamically retrieve SECRET_KEY
    serializer = URLSafeTimedSerializer(get_secret_key())
    return serializer.dumps(user_id, salt='password-reset-salt')


def verify_reset_token(token, expiration=3600):
    # Dynamically retrieve SECRET_KEY
    serializer = URLSafeTimedSerializer(get_secret_key())
    try:
        user_id = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return user_id
