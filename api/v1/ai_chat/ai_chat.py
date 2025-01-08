"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request
from utils.logger import Logger
from utils.decorators import handle_response
from services.ai_chat.ai_chat_service import AIChatService
from services.user.auth_service import AuthService

logger = Logger(__name__)
router = APIRouter()
service = AIChatService()
auth_service = AuthService()


# Request body definition

class ChatQueryRequest(BaseModel):
    query: str = Field(..., description="User's query content")


# Route implementations

@router.post("/query")
@handle_response
@auth_service.requires_auth
async def query_ai_chat(request: Request, body: ChatQueryRequest):
    """
    Generate a personalized response based on the user's input query and user information.
    """
    user_id = request.state.user_id  # Retrieve authenticated user ID from request.state
    logger.info(f"API: Generating AI chat response for user_id {user_id}")

    try:
        # Call the service to get a response
        response = service.retrieve_answer(user_id=user_id, query=body.query)

        # Return the response
        return {"status": "success", "data": response}
    except HTTPException as e:
        logger.warning(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error generating AI chat response for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/test")
@auth_service.requires_auth
async def test_ai_chat(request: Request):
    """
    Test endpoint to check if the service is working as expected.
    """
    user_id = request.state.user_id  # Retrieve authenticated user ID from request.state
    logger.info(f"API: Testing AIChatService for user_id {user_id}")

    try:
        # Example test query
        test_query = "What is the best exercise for weight loss?"

        # Call the service to get a test response
        response = service.retrieve_answer(user_id=user_id, query=test_query)
        logger.info("AIChatService test completed successfully.")

        # Return the test result
        return {"status": "success", "message": "Test passed", "data": response}
    except Exception as e:
        logger.error(f"Error during AIChatService test for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
