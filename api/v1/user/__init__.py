"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
# v1/user/__init__.py

from fastapi import APIRouter
from .user import router as user_router

router = APIRouter()
router.include_router(user_router, prefix="/user", tags=["User"])
