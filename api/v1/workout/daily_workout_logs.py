"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
from pydantic import Field
from datetime import date
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.workout.daily_workout_logs_service import DailyWorkoutLogsService
from utils.logger import Logger
from utils.decorators import handle_response
from services.user.auth_service import AuthService

logger = Logger(__name__)
router = APIRouter()
service = DailyWorkoutLogsService()
auth_service = AuthService()


# Request body definitions

class CreateOrUpdateWorkoutLogRequest(BaseModel):
    log_date: date = Field(default_factory=date.today)  # Use an explicit field name
    workout_content: str
    total_weight_lost: float
    total_calories_burnt: float
    avg_workout_duration: int


class UpdateWorkoutLogFieldsRequest(BaseModel):
    total_weight_lost: float = None
    total_calories_burnt: float = None
    avg_workout_duration: int = None
    workout_content: str = None


# Route implementations

@router.get("/workout_logs")
@handle_response
@auth_service.requires_auth
async def get_workout_log(request: Request, log_date: str):
    """
    Retrieve a user's workout log for a specific date.
    """
    user_id = request.state.user_id  # Retrieve user_id from request.state
    logger.info(f"API: Fetching workout log for user_id {user_id} on log_date {log_date}")
    log = service.get_workout_log(user_id, log_date)
    if not log:
        raise HTTPException(status_code=404, detail="Workout log not found")
    return {"status": "success", "data": log}


@router.post("/workout_logs")
@handle_response
@auth_service.requires_auth
async def create_or_update_workout_log(request: Request, body: CreateOrUpdateWorkoutLogRequest):
    """
    Create or update a workout log for a specific date.
    """
    user_id = request.state.user_id  # Retrieve user_id from request.state
    workout_log_date = body.log_date or date.today()  # Use today's date if none is provided
    logger.info(f"API: Creating or updating workout log for user_id {user_id} on log_date {workout_log_date}")

    try:
        result = service.create_or_update_workout_log(
            user_id=user_id,
            log_date=workout_log_date,
            workout_content=body.workout_content,
            total_weight_lost=body.total_weight_lost,
            total_calories_burnt=body.total_calories_burnt,
            avg_workout_duration=body.avg_workout_duration
        )
        return {"status": "success", "message": "Workout log successfully created/updated", "data": result}
    except Exception as e:
        logger.error(f"Error creating or updating workout log for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/workout_logs")
@handle_response
@auth_service.requires_auth
async def update_workout_log_fields(request: Request, body: UpdateWorkoutLogFieldsRequest, log_date: str):
    """
    Update specific fields in a user's workout log for a given date.
    """
    user_id = request.state.user_id  # Retrieve user_id from request.state
    logger.info(f"API: Updating workout log fields for user_id {user_id} on log_date {log_date}")
    try:
        update_data = body.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update provided")
        result = service.update_workout_log_fields(user_id, log_date, update_data)
        if result["matched_count"] == 0:
            raise HTTPException(status_code=404, detail="Workout log not found for update")
        return {"status": "success", "message": "Workout log successfully updated", "data": result}
    except ValueError as ve:
        logger.warning(f"Validation error for user_id {user_id}: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating workout log for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/workout_logs/progress")
@handle_response
@auth_service.requires_auth
async def calculate_total_progress(request: Request):
    """
    Calculate the total progress across all workout logs for a user.
    """
    user_id = request.state.user_id  # Retrieve user_id from request.state
    logger.info(f"API: Calculating total progress for user_id {user_id}")
    try:
        progress = service.calculate_total_progress(user_id)
        return {"status": "success", "data": progress}
    except Exception as e:
        logger.error(f"Error calculating total progress for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
