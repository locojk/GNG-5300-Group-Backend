"""
API Router Initialization

@Date: 2024-09-11
@Author: Adam Lyu
"""

# api/__init__.py

from fastapi import APIRouter
from api.v1 import router as v1_router
# from api.v2 import router as v2_router  # Placeholder for a future v2 version

# Create a top-level router object
router = APIRouter()

# Register routes for different API versions
router.include_router(v1_router, prefix="/v1", tags=["v1"])
# router.include_router(v2_router, prefix="/v2", tags=["v2"])  # Future support for v2
