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
from bson import ObjectId  # Import ObjectId for MongoDB handling
from datetime import datetime  # Import datetime for date serialization
from utils.env_loader import load_platform_specific_env
import json
import logging

# Load environment-specific configurations
load_platform_specific_env()

logger = logging.getLogger(__name__)


# Custom JSONEncoder to handle ObjectId and datetime serialization
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string for serialization
        elif isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        return super().default(obj)


def handle_response(f):
    """
    Decorator to handle and standardize API responses.

    It wraps the original function to:
    - Serialize the response using a custom JSON encoder.
    - Handle exceptions and return appropriate HTTP responses.
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        try:
            # Call the original function and get its return value
            result = await f(*args, **kwargs)

            # If the return value is already a JSONResponse, return it as-is
            if isinstance(result, JSONResponse):
                return result

            # If the return value is a tuple, unpack it into data and status_code
            if isinstance(result, tuple):
                data, status_code = result
            else:
                data = result
                status_code = 200  # Default status code is 200

            # Serialize the data using the custom JSONEncoder
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
