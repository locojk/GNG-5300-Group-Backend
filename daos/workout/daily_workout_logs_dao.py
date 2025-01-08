"""
@Time ： 2024-11-28
@Auth ： Adam Lyu
"""
from datetime import datetime, date
import pymongo
from bson.objectid import ObjectId
from daos.mongodb_client import MongoDBClient
from utils.logger import Logger

# Initialize logger
logger = Logger(__name__)


class DailyWorkoutLogsDAO:
    def __init__(self):
        self.db_client = MongoDBClient()
        self.collection_name = 'daily_workout_logs'

        # Apply JSON Schema validation rules and create indexes
        with self.db_client as db_client:
            logger.info(f"Initializing validation and index for collection: {self.collection_name}")
            db_client.ensure_validation(self.collection_name, 'daily_workout_logs_schema.json')
            db_client.db[self.collection_name].create_index(
                [("user_id", pymongo.ASCENDING), ("log_date", pymongo.ASCENDING)],
                unique=True  # Ensure each user has only one log per day
            )

    def get_log_by_user_and_date(self, user_id, log_date, db_client=None):
        """Retrieve workout log by user_id and log_date."""
        logger.info(f"Fetching workout log for user_id: {user_id}, log_date: {log_date}")
        query = {"user_id": ObjectId(user_id), "log_date": log_date}
        if db_client is None:
            with self.db_client as db_client:
                log = db_client.find_one(self.collection_name, query)
        else:
            log = db_client.find_one(self.collection_name, query)
        if log:
            logger.debug(f"Workout log found: {log}")
        else:
            logger.warning(f"No workout log found for user_id: {user_id}, log_date: {log_date}")
        return log

    def create_or_update_log(self, user_id, log_date, workout_content, total_weight_lost, total_calories_burnt,
                             avg_workout_duration):
        """Create or update a workout log for a user."""
        logger.info(f"Creating or updating workout log for user_id: {user_id}, log_date: {log_date}")

        # Convert log_date to datetime
        if isinstance(log_date, date):
            log_date = datetime.combine(log_date, datetime.min.time())

        with self.db_client as db_client:
            log_data = {
                "user_id": ObjectId(user_id),
                "log_date": log_date,
                "workout_content": workout_content,
                "total_weight_lost": total_weight_lost,
                "total_calories_burnt": total_calories_burnt,
                "avg_workout_duration": avg_workout_duration,
                "updated_at": datetime.utcnow()
            }

            # Check if the log already exists
            existing_log = self.get_log_by_user_and_date(user_id, log_date, db_client)
            if existing_log:
                # Update the existing log
                result = db_client.update_one(
                    self.collection_name,
                    {"user_id": ObjectId(user_id), "log_date": log_date},
                    {"$set": log_data}
                )
                return {
                    "operation": "update",
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None
                }
            else:
                # Create a new log
                log_data["created_at"] = datetime.now()
                inserted_id = db_client.insert_one(self.collection_name, log_data)
                return {
                    "operation": "create",
                    "inserted_id": str(inserted_id)
                }

    def update_log_fields(self, user_id, log_date, update_fields):
        """Update specific fields of a workout log."""
        logger.info(f"Updating workout log for user_id: {user_id}, log_date: {log_date}")
        if not isinstance(update_fields, dict) or not update_fields:
            logger.error("update_fields must be a non-empty dictionary")
            raise ValueError("update_fields must be a non-empty dictionary")

        # Automatically add the `updated_at` timestamp
        update_fields["updated_at"] = datetime.utcnow()

        query = {"user_id": ObjectId(user_id), "log_date": log_date}
        update_data = {"$set": update_fields}

        logger.debug(f"Query: {query}, Update data: {update_data}")

        with self.db_client as db_client:
            result = db_client.update_one(self.collection_name, query, update_data)
            if result.matched_count > 0:
                logger.audit_log(
                    user_id=str(user_id),
                    action="update_fields",
                    resource="daily_workout_logs",
                    status="success",
                    details=f"Updated fields for user_id {user_id}, log_date {log_date}: {update_fields}"
                )
            else:
                logger.warning(f"No workout log found for user_id: {user_id}, log_date: {log_date}")
                logger.audit_log(
                    user_id=str(user_id),
                    action="update_fields",
                    resource="daily_workout_logs",
                    status="failed",
                    details=f"Update failed for user_id: {user_id}, log_date: {log_date}"
                )
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count
            }

    def calculate_total_progress(self, user_id):
        """Calculate overall progress for a user."""
        logger.info(f"Calculating total progress for user_id: {user_id}")
        query = {"user_id": ObjectId(user_id), "is_deleted": False}

        try:
            with self.db_client as db_client:
                pipeline = [
                    {"$match": query},
                    {
                        "$group": {
                            "_id": "$user_id",
                            "total_weight_lost": {"$sum": "$total_weight_lost"},
                            "total_calories_burnt": {"$sum": "$total_calories_burnt"},
                            "total_duration": {"$sum": "$avg_workout_duration"},
                            "total_sessions": {"$sum": 1}
                        }
                    }
                ]
                total_results = list(db_client.db[self.collection_name].aggregate(pipeline))
                if total_results:
                    total_progress = total_results[0]
                    logger.debug(f"Total progress results: {total_progress}")
                    return {
                        "total_weight_lost": total_progress.get("total_weight_lost", 0),
                        "total_calories_burnt": total_progress.get("total_calories_burnt", 0),
                        "total_duration": total_progress.get("total_duration", 0),
                        "total_sessions": total_progress.get("total_sessions", 0),
                    }
                else:
                    logger.warning(f"No workout logs found for user_id: {user_id}")
                    return {
                        "total_weight_lost": 0,
                        "total_calories_burnt": 0,
                        "total_duration": 0,
                        "total_sessions": 0,
                    }
        except Exception as e:
            logger.error(f"Failed to calculate total progress for user_id {user_id}: {e}")
            raise



if __name__ == "__main__":
    dao = DailyWorkoutLogsDAO()

    # Insert multiple test logs for user 6741f0e75b6291baa9b7a273
    test_logs = [
        {
            "user_id": "674a21ac406725261a1ad15f",
            "log_date": datetime(2024, 11, 25),
            "workout_content": "Running and Yoga",
            "total_weight_lost": 0.2,
            "total_calories_burnt": 500,
            "avg_workout_duration": 45
        },
        {
            "user_id": "674a21ac406725261a1ad15f",
            "log_date": datetime(2024, 11, 26),
            "workout_content": "Strength Training",
            "total_weight_lost": 0.3,
            "total_calories_burnt": 600,
            "avg_workout_duration": 50
        },
        {
            "user_id": "674a21ac406725261a1ad15f",
            "log_date": datetime(2024, 11, 27),
            "workout_content": "Cycling",
            "total_weight_lost": 0.1,
            "total_calories_burnt": 400,
            "avg_workout_duration": 40
        },
        {
            "user_id": "674a21ac406725261a1ad15f",
            "log_date": datetime(2024, 11, 28),
            "workout_content": "Swimming",
            "total_weight_lost": 0.4,
            "total_calories_burnt": 700,
            "avg_workout_duration": 60
        }
    ]

    for log in test_logs:
        result = dao.create_or_update_log(
            user_id=log["user_id"],
            log_date=log["log_date"],
            workout_content=log["workout_content"],
            total_weight_lost=log["total_weight_lost"],
            total_calories_burnt=log["total_calories_burnt"],
            avg_workout_duration=log["avg_workout_duration"]
        )
        print(f"Inserted/Updated log for log_date {log['log_date']}: {result}")
