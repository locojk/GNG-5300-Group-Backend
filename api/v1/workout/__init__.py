# v1/user/__init__.py

from fastapi import APIRouter
from .workout import router as user_router

router = APIRouter()
router.include_router(user_router, prefix="/workout", tags=["Workout"])