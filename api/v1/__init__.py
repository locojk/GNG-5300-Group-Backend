"""
@Time ： 2024-11-03
@Auth ： Adam Lyu
"""
# api/v1/__init__.py

from fastapi import APIRouter
from api.v1.health import router as health_router
from api.v1.user import router as user_router
from api.v1.workout import router as workout_router


router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(user_router, tags=["user"])
router.include_router(workout_router, tags=["workout"])
