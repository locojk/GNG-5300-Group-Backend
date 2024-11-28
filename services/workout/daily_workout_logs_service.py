"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""
from datetime import datetime, date as log_date
from daos.workout.daily_workout_logs_dao import DailyWorkoutLogsDAO
from pymongo.results import UpdateResult, InsertOneResult
from utils.logger import Logger

# 初始化日志记录器
logger = Logger(__name__)


class DailyWorkoutLogsService:
    def __init__(self):
        self.dao = DailyWorkoutLogsDAO()

    def get_workout_log(self, user_id, log_date):
        """
        Retrieve a workout log for a specific user and log_date.
        """
        logger.info(f"Service: Fetching workout log for user_id: {user_id}, log_date: {log_date}")
        try:
            log = self.dao.get_log_by_user_and_date(user_id, log_date)
            if log:
                logger.debug(f"Workout log retrieved: {log}")
            else:
                logger.warning(f"No workout log found for user_id: {user_id}, log_date: {log_date}")
            return log
        except Exception as e:
            logger.error(f"Failed to retrieve workout log: {e}")
            raise

    def create_or_update_workout_log(self, user_id, log_date=None, workout_content=None,
                                     total_weight_lost=0, total_calories_burnt=0, avg_workout_duration=0):
        """
        Create or update a workout log for a specific user.
        """
        log_date = log_date or datetime.today().date()  # 如果未提供日期，则使用今天的日期
        logger.info(f"Service: Creating or updating workout log for user_id {user_id} on log_date {log_date}")

        try:
            result = self.dao.create_or_update_log(
                user_id=user_id,
                log_date=log_date,
                workout_content=workout_content,
                total_weight_lost=total_weight_lost,
                total_calories_burnt=total_calories_burnt,
                avg_workout_duration=avg_workout_duration
            )

            # 处理 MongoDB 的结果，确保可序列化
            if isinstance(result, UpdateResult):
                result_data = {
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                }
            elif isinstance(result, InsertOneResult):
                result_data = {"inserted_id": str(result.inserted_id)}
            else:
                result_data = result  # 如果是普通字典

            logger.info(f"Workout log successfully created/updated for user_id {user_id} on log_date {log_date}")
            return result_data
        except Exception as e:
            logger.error(f"Error creating or updating workout log for user_id {user_id}: {e}")
            raise

    def update_workout_log_fields(self, user_id, log_date, update_fields):
        """
        Update specific fields of a workout log.
        """
        logger.info(f"Service: Updating workout log fields for user_id: {user_id}, log_date: {log_date}")
        try:
            result = self.dao.update_log_fields(
                user_id=user_id,
                log_date=log_date,
                update_fields=update_fields
            )
            if result["matched_count"] > 0:
                logger.info(f"Workout log fields successfully updated for user_id: {user_id}, log_date: {log_date}")
            else:
                logger.warning(f"No workout log found to update for user_id: {user_id}, log_date: {log_date}")
            return result
        except Exception as e:
            logger.error(f"Failed to update workout log fields: {e}")
            raise

    def calculate_total_progress(self, user_id):
        """
        Calculate total progress for a user based on all workout logs.
        Returns:
            {
                "key_statistics": {
                    "total_weight_lost": 3.5,
                    "total_calories_burnt": 12500,
                    "avg_calories_burnt_per_day": 500,
                    "avg_workout_duration_per_session": 45
                },
                "daily_progress": [
                    {"log_date": "2024-11-01", "total_workout_time": 30, "total_calories_burnt": 500},
                    {"log_date": "2024-11-02", "total_workout_time": 40, "total_calories_burnt": 600},
                    ...
                ]
            }
        """
        logger.info(f"Service: Calculating total progress for user_id: {user_id}")
        try:
            # 获取总统计数据
            total_progress = self.dao.calculate_total_progress(user_id)
            logger.debug(f"Total progress: {total_progress}")

            # 获取每日数据
            daily_progress = self.dao.calculate_daily_progress(user_id)
            logger.debug(f"Daily progress: {daily_progress}")

            # 计算前端需要的平均值
            avg_calories_burnt_per_day = total_progress["total_calories_burnt"] / len(
                daily_progress) if daily_progress else 0
            avg_workout_duration_per_session = total_progress["total_duration"] / total_progress["total_sessions"] if \
                total_progress["total_sessions"] > 0 else 0

            result = {
                "key_statistics": {
                    "total_weight_lost": total_progress["total_weight_lost"],
                    "total_calories_burnt": total_progress["total_calories_burnt"],
                    "avg_calories_burnt_per_day": round(avg_calories_burnt_per_day, 2),
                    "avg_workout_duration_per_session": round(avg_workout_duration_per_session, 2),
                },
                "daily_progress": [
                    {
                        "log_date": item["_id"]["log_date"].strftime("%Y-%m-%d"),  # 转换日期格式
                        "total_workout_time": item["total_workout_time"],
                        "total_calories_burnt": item["total_calories_burnt"]
                    } for item in daily_progress
                ]
            }
            logger.info(f"Total progress calculated for user_id {user_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to calculate total progress for user_id {user_id}: {e}")
            raise
