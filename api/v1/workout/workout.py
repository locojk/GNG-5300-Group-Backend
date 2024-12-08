"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
from fastapi import APIRouter, HTTPException, Request
from services.workout.fitness_goal_service import FitnessGoalService
from services.workout.validation import CreateOrUpdateGoalRequest
from utils.logger import Logger
from services.user.auth_service import AuthService
from utils.decorators import handle_response

logger = Logger(__name__)
router = APIRouter()
service = FitnessGoalService()
auth_service = AuthService()


# Route implementations

@router.get("/fitness_goal")
@handle_response
@auth_service.requires_auth
async def get_fitness_goal(request: Request):
    """
    Retrieve the user's fitness goal.
    """
    user_id = request.state.user_id  # Retrieve user_id from request.state
    result = service.get_fitness_goal(user_id)
    if not result["data"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return {"status": "success", "data": result["data"]}


@router.post("/fitness_goal")
@handle_response
@auth_service.requires_auth
async def create_or_update_fitness_goal(request: Request, body: CreateOrUpdateGoalRequest):
    """
    Create or update the user's fitness goal.
    """
    user_id = request.state.user_id  # Retrieve user_id from request.state
    result = service.create_or_update_fitness_goal(user_id=user_id, data=body.dict(exclude_unset=True))
    return {"status": "success", "message": result["message"], "data": result["data"]}


@router.patch("/fitness_goal")
@handle_response
@auth_service.requires_auth
async def update_fitness_goal_fields(request: Request, body: CreateOrUpdateGoalRequest):
    """
    Dynamically update specific fields of the user's fitness goal.
    """
    user_id = request.state.user_id  # Retrieve user_id from request.state
    try:
        # Extract fields to be updated
        update_data = body.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update provided")

        # Call the service layer to perform the update
        result = service.update_fitness_goal_fields(user_id, update_data)

        # Serialize the `UpdateResult` fields
        serialized_result = {
            "matched_count": result["data"].get("matched_count", 0),
            "modified_count": result["data"].get("modified_count", 0),
            "upserted_id": str(result["data"].get("upserted_id")) if result["data"].get("upserted_id") else None,
        }

        # Check if any document was matched for update
        if serialized_result["matched_count"] == 0:
            raise HTTPException(status_code=404, detail="Fitness goal not found for update")

        return {"status": "success", "message": result["message"], "data": serialized_result}

    except ValueError as ve:
        logger.warning(f"Validation error for user_id {user_id}: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating fitness goal for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
