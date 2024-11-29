# v1/user/__init__.py

from fastapi import APIRouter
from .workout import router as workout_router
from .daily_workout_logs import router as daily_workout_logs_router

router = APIRouter()
router.include_router(workout_router, prefix="/workout", tags=["Workout"])
router.include_router(daily_workout_logs_router, prefix="/daily", tags=["Daily"])