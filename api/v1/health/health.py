"""
@Time ： 2024-10-05
@Auth ： Adam Lyu
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from bson import ObjectId
from utils.decorators import handle_response

router = APIRouter()


@router.get('/')
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)


@router.get('/test_encoder')
@handle_response
async def test_encoder():
    test_data = {"_id": ObjectId(), "name": "Test Object"}
    return test_data
