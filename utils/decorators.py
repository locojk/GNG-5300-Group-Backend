"""
Custom JSON Encoder and Response Handler

@Date: 2024-10-20
@Author: Adam Lyu
"""
import os
from functools import wraps
from fastapi.responses import JSONResponse
from marshmallow import ValidationError
from fastapi import HTTPException
from bson import ObjectId  # Import ObjectId
from datetime import datetime  # Import datetime
from utils.env_loader import load_platform_specific_env
import json
import logging
load_platform_specific_env()
logger = logging.getLogger(__name__)


# Custom JSONEncoder to handle ObjectId and datetime serialization
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to a string
        elif isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
        return super().default(obj)


def handle_response(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        try:
            # 获取原始函数的返回值
            result = await f(*args, **kwargs)

            # 如果返回值是 JSONResponse，直接返回
            if isinstance(result, JSONResponse):
                return result

            # 如果返回值是元组，解包为内容和状态码
            if isinstance(result, tuple):
                data, status_code = result
            else:
                data = result
                status_code = 200  # 默认状态码为 200

            # 使用自定义 JSONEncoder 序列化数据
            serialized_data = json.loads(CustomJSONEncoder().encode(data))
            return JSONResponse(content=serialized_data, status_code=status_code)

        except ValidationError as e:
            logger.warning(f"ValidationError: {e.messages}")
            raise HTTPException(status_code=400, detail=e.messages)
        except HTTPException as e:
            logger.warning(f"HTTPException: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    return decorated_function

