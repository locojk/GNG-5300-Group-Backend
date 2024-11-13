"""
Password Reset Email Sender

@Date: 2024-09-11
@Author: Adam Lyu
"""

from flask_mail import Message
from flask import current_app


def send_reset_email(user, token, mail):
    msg = Message('Reset Your Password', recipients=[user['email']])
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset_password?token={token}"
    msg.body = f'Click the link below to reset your password:\n{reset_url}'
    mail.send(msg)
