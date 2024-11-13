"""
@Time ： 2024-11-03
@Auth ： Adam Lyu
"""
# v1/health/__init__.py

from fastapi import APIRouter
from .health import router as health_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["Health"])
