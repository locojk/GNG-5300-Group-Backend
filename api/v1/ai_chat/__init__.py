"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
# v1/user/__init__.py

from fastapi import APIRouter
from .ai_chat import router as ai_chat_router

router = APIRouter()
router.include_router(ai_chat_router, prefix="/ai_chat", tags=["AI chat"])
