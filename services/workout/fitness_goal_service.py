"""
Fitness Goal Service

@Date: 2024-11-23
@Author: Adam Lyu
"""

from daos.workout.fitness_goal_dao import FitnessGoalDAO
from utils.logger import Logger
from services.workout.validation import CreateOrUpdateGoalRequest  # Import validation model

logger = Logger(__name__)


class FitnessGoalService:
    def __init__(self):
        pass

    def get_fitness_goal(self, user_id: str):
        """
        Retrieve the fitness goal for a user.

        :param user_id: User ID
        :return: Fitness goal data
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
        Create or update the fitness goal for a user.

        :param user_id: User ID
        :param data: Fitness goal data in JSON format
        :return: Operation result
        """
        logger.info(f"Creating or updating fitness goal for user_id: {user_id}")

        # Validate the input data using the model
        validated_data = CreateOrUpdateGoalRequest(**data)
        dao = FitnessGoalDAO()

        # Call the DAO layer to perform create or update operation
        result = dao.create_or_update_fitness_goal(
            user_id=user_id,
            goal=validated_data.goal,
            days_per_week=validated_data.days_per_week,
            workout_duration=validated_data.workout_duration,
            rest_days=validated_data.rest_days,
        )

        # Handle results from the DAO
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
        Dynamically update specific fields of a user's fitness goal.

        :param user_id: User ID
        :param update_fields: Fields to update in JSON format
        :return: Update result
        """
        dao = FitnessGoalDAO()
        logger.info(f"Updating fitness goal fields for user_id: {user_id}")

        # Validate the input fields (only validate provided fields)
        validated_data = CreateOrUpdateGoalRequest(**update_fields)

        # Call the DAO layer to perform field updates
        result = dao.update_fitness_goal(user_id, validated_data.dict(exclude_unset=True))

        # Extract serializable fields from the result
        serialized_result = {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }

        # Return results
        if serialized_result["matched_count"] > 0:
            logger.info(f"Fitness goal updated successfully for user_id: {user_id}")
            return {"message": "Fitness goal updated successfully", "data": serialized_result}
        else:
            logger.warning(f"No fitness goal found to update for user_id: {user_id}")
            return {"message": "No fitness goal found to update", "data": None}
