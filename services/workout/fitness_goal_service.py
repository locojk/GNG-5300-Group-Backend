"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""

from daos.workout.fitness_goal_dao import FitnessGoalDAO
from utils.logger import Logger
from services.workout.validation import CreateOrUpdateGoalRequest  # 引入模型

logger = Logger(__name__)


class FitnessGoalService:
    def __init__(self):
        ...

    def get_fitness_goal(self, user_id: str):
        """
        获取用户的健身目标
        :param user_id: 用户 ID
        :return: 健身目标数据
        """
        logger.info(f"Fetching fitness goal for user_id: {user_id}")
        dao = FitnessGoalDAO()
        goal = dao.get_goal_by_user_id(user_id)
        if not goal:
            logger.warning(f"No fitness goal found for user_id: {user_id}")
            return {"message": "No fitness goal found", "data": None}
        return {"message": "Fitness goal retrieved successfully", "data": goal}

    def create_or_update_fitness_goal(self, user_id: str, data: dict):
        """
        创建或更新用户的健身目标
        :param user_id: 用户 ID
        :param data: 健身目标的数据（JSON 格式）
        :return: 操作结果
        """
        logger.info(f"Creating or updating fitness goal for user_id: {user_id}")

        # 使用模型进行数据验证
        validated_data = CreateOrUpdateGoalRequest(**data)
        dao = FitnessGoalDAO()

        # 调用 DAO 层进行创建或更新操作
        result = dao.create_or_update_fitness_goal(
            user_id=user_id,
            goal=validated_data.goal,
            days_per_week=validated_data.days_per_week,
            workout_duration=validated_data.workout_duration,
            rest_days=validated_data.rest_days,
        )

        # 处理 DAO 返回的结果
        if result["operation"] == "create":
            logger.info(f"Fitness goal created successfully for user_id: {user_id}")
            return {"message": "Fitness goal created successfully", "data": result}
        elif result["operation"] == "update":
            logger.info(f"Fitness goal updated successfully for user_id: {user_id}")
            return {
                "message": "Fitness goal updated successfully",
                "data": {
                    "matched_count": result.get("matched_count", 0),
                    "modified_count": result.get("modified_count", 0),
                },
            }
        else:
            logger.error(f"Unexpected operation result for user_id {user_id}: {result}")
            raise ValueError("Unexpected DAO operation result")

    def update_fitness_goal_fields(self, user_id: str, update_fields: dict):
        """
        动态更新用户的健身目标部分字段
        :param user_id: 用户 ID
        :param update_fields: 需要更新的字段（JSON 格式）
        :return: 更新结果
        """
        dao = FitnessGoalDAO()
        logger.info(f"Updating fitness goal fields for user_id: {user_id}")

        # 使用模型进行数据验证（仅验证提供的字段）
        validated_data = CreateOrUpdateGoalRequest(**update_fields)

        # 调用 DAO 层进行字段更新
        result = dao.update_fitness_goal(user_id, validated_data.dict(exclude_unset=True))

        # Extract serializable fields
        serialized_result = {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }

        # 返回结果
        if serialized_result["matched_count"] > 0:
            logger.info(f"Fitness goal updated successfully for user_id: {user_id}")
            return {"message": "Fitness goal updated successfully", "data": serialized_result}
        else:
            logger.warning(f"No fitness goal found to update for user_id: {user_id}")
            return {"message": "No fitness goal found to update", "data": None}
