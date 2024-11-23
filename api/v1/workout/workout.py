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


# 路由实现

@router.get("/fitness_goal")
@handle_response
@auth_service.requires_auth
async def get_fitness_goal(request: Request):
    """
    获取用户的健身目标
    """
    user_id = request.state.user_id  # 从 request.state 获取 user_id
    try:
        result = service.get_fitness_goal(user_id)
        if not result["data"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return {"status": "success", "data": result["data"]}
    except Exception as e:
        logger.error(f"Error fetching fitness goal for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/fitness_goal")
@handle_response
@auth_service.requires_auth
async def create_or_update_fitness_goal(request: Request, body: CreateOrUpdateGoalRequest):
    """
    创建或更新用户的健身目标
    """
    user_id = request.state.user_id  # 从 request.state 获取 user_id
    # try:
    # 直接将模型转为字典，并传递给服务层
    result = service.create_or_update_fitness_goal(user_id=user_id, data=body.dict(exclude_unset=True))
    return {"status": "success", "message": result["message"], "data": result["data"]}
    # except ValueError as ve:
    #     logger.warning(f"Validation error for user_id {user_id}: {ve}")
    #     raise HTTPException(status_code=400, detail=str(ve))
    # except Exception as e:
    #     logger.error(f"Error creating or updating fitness goal for user_id {user_id}: {e}")
    #     raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/fitness_goal")
@handle_response
@auth_service.requires_auth
async def update_fitness_goal_fields(request: Request, body: CreateOrUpdateGoalRequest):
    """
    动态更新用户健身目标的部分字段
    """
    user_id = request.state.user_id  # 从 request.state 获取 user_id
    try:
        update_data = body.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update provided")
        result = service.update_fitness_goal_fields(user_id, update_data)
        if not result["matched_count"]:
            raise HTTPException(status_code=404, detail="Fitness goal not found for update")
        return {"status": "success", "message": result["message"], "data": result["data"]}
    except ValueError as ve:
        logger.warning(f"Validation error for user_id {user_id}: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating fitness goal for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
