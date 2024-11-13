"""
Password Reset Token Generator and Verifier

@Date: 2024-09-11
@Author: Adam Lyu
"""

from itsdangerous import URLSafeTimedSerializer
from flask import current_app

# Retrieve SECRET_KEY from configuration
def get_secret_key():
    return current_app.config['SECRET_KEY']

# Retrieve ALGORITHM from configuration, default to 'HS256'
def get_algorithm():
    return current_app.config.get('ALGORITHM', 'HS256')

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
