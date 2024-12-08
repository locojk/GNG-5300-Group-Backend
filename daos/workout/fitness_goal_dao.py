"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
from datetime import datetime

import pymongo
from bson.objectid import ObjectId
from daos.mongodb_client import MongoDBClient
from utils.logger import Logger

# Initialize logger
logger = Logger(__name__)


class FitnessGoalDAO:
    def __init__(self):
        self.db_client = MongoDBClient()
        self.collection_name = 'fitness_goals'

        # Apply JSON Schema validation rules and create indexes
        with self.db_client as db_client:
            logger.info(f"Initializing validation and index for collection: {self.collection_name}")
            db_client.ensure_validation(self.collection_name, 'fitness_goals_schema.json')
            db_client.db[self.collection_name].create_index(
                [("user_id", pymongo.ASCENDING)], unique=True  # Ensure each user can only have one goal
            )

    def get_goal_by_user_id(self, user_id, db_client=None):
        """Retrieve fitness goal information by user_id."""
        logger.info(f"Fetching fitness goal by user_id: {user_id}")
        if db_client is None:
            with self.db_client as db_client:
                goal = db_client.find_one(self.collection_name, {"user_id": ObjectId(user_id)})
        else:
            goal = db_client.find_one(self.collection_name, {"user_id": ObjectId(user_id)})
        if goal:
            logger.debug(f"Fitness goal found: {goal}")
        else:
            logger.warning(f"No fitness goal found for user_id: {user_id}")
        return goal

    def create_or_update_fitness_goal(self, user_id, goal, days_per_week, workout_duration, rest_days):
        """Create or update a fitness goal for a user."""
        logger.info(f"Creating or updating fitness goal for user_id: {user_id}")
        with self.db_client as db_client:
            goal_data = {
                "user_id": ObjectId(user_id),
                "goal": goal,
                "days_per_week": days_per_week,
                "workout_duration": workout_duration,
                "rest_days": rest_days,
                "updated_at": datetime.utcnow()
            }

            # Check for existing goal
            existing_goal = self.get_goal_by_user_id(user_id, db_client)
            if existing_goal:
                # Update existing goal
                result = db_client.update_one(
                    self.collection_name,
                    {"user_id": ObjectId(user_id)},
                    {"$set": goal_data}
                )
                logger.audit_log(
                    user_id=str(user_id),
                    action="update",
                    resource="fitness_goals",
                    status="success",
                    details=f"Updated fitness goal for user_id {user_id}"
                )
                return {"operation": "update", "result": result}
            else:
                # Create new goal
                goal_data["created_at"] = datetime.now()
                inserted_id = db_client.insert_one(self.collection_name, goal_data)
                logger.audit_log(
                    user_id=str(user_id),
                    action="create",
                    resource="fitness_goals",
                    status="success",
                    details=f"Created new fitness goal for user_id {user_id}"
                )
                return {"operation": "create", "inserted_id": inserted_id}

    def update_fitness_goal(self, user_id, update_fields):
        """Update specific fields of a user's fitness goal."""
        logger.info(f"Updating fitness goal for user_id: {user_id}")
        if not isinstance(update_fields, dict) or not update_fields:
            logger.error("update_fields must be a non-empty dictionary")
            raise ValueError("update_fields must be a non-empty dictionary")

        # Automatically add the `updated_at` timestamp
        update_fields["updated_at"] = datetime.utcnow()

        query = {"user_id": ObjectId(user_id)}
        update_data = {"$set": update_fields}

        logger.debug(f"Query: {query}, Update data: {update_data}")

        with self.db_client as db_client:
            result = db_client.update_one(self.collection_name, query, update_data)
            if result.matched_count > 0:
                logger.audit_log(
                    user_id=str(user_id),
                    action="update_fields",
                    resource="fitness_goals",
                    status="success",
                    details=f"Updated fields for user_id {user_id}: {update_fields}"
                )
            else:
                logger.warning(f"No fitness goal found for user_id: {user_id}")
                logger.audit_log(
                    user_id=str(user_id),
                    action="update_fields",
                    resource="fitness_goals",
                    status="failed",
                    details=f"Update failed for user_id: {user_id}"
                )
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count
            }


if __name__ == "__main__":
    # Example usage
    dao = FitnessGoalDAO()

    # Create or update a fitness goal
    result = dao.create_or_update_fitness_goal(
        user_id="674a21ac406725261a1ad15f",
        goal="strength",
        days_per_week=5,
        workout_duration=60,
        rest_days=["Saturday", "Sunday"]
    )
    print(f"Operation result: {result}")

    # Uncomment below for additional operations
    # Retrieve a fitness goal
    # goal = dao.get_goal_by_user_id("674a15955311e41c60aefd23")
    # print(f"Retrieved goal: {goal}")

    # Update specific fields of a fitness goal
    # updated_result = dao.update_fitness_goal(
    #     user_id="674a15955311e41c60aefd23",
    #     update_fields={"days_per_week": 6}
    # )
    # print(f"Update result: {updated_result}")

