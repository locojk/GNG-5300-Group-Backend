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
            # Get the original function's return value
            result = await f(*args, **kwargs)

            # If the result is a tuple, unpack content and status code
            if isinstance(result, tuple):
                data, status_code = result
            else:
                data = result
                status_code = 200  # Default status code is 200

            # Serialize data using the custom JSONEncoder
            serialized_data = json.loads(CustomJSONEncoder().encode(data))
            return JSONResponse(content=serialized_data, status_code=status_code)

        except ValidationError as e:
            # Handle marshmallow validation errors
            logger.warning(f"ValidationError: {e.messages}")
            raise HTTPException(
                status_code=400,
                detail=e.messages  # Pass the detailed validation errors
            )
        except HTTPException as e:
            # Re-raise HTTPExceptions to be handled by FastAPI
            logger.warning(f"HTTPException: {e.detail}")
            raise e
        except ValueError as e:
            # Handle custom ValueErrors with a 400 status code
            logger.error(f"ValueError: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Handle all other exceptions with a 500 status code
            logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
            if os.getenv('DEBUG', False):
                # Include detailed error messages in debug mode
                raise HTTPException(status_code=500, detail=str(e))
            else:
                # Generic error message in production mode
                raise HTTPException(status_code=500, detail="Internal server error")

    return decorated_function
