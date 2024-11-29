"""
@Time ： 2024-11-23
@Auth ： Adam Lyu
"""

from pydantic import BaseModel, field_validator
from typing import List, Optional


class CreateOrUpdateGoalRequest(BaseModel):
    goal: Optional[str] = None
    days_per_week: Optional[int] = None
    workout_duration: Optional[int] = None
    rest_days: Optional[List[str]] = None

    @field_validator("goal")
    def validate_goal(cls, value: str) -> str:
        """
        校验 goal 是否是有效值
        """
        valid_goals = {"strength", "weight_loss", "flexibility"}
        if value not in valid_goals:
            raise ValueError(f"Invalid goal: {value}. Must be one of {valid_goals}")
        return value

    @field_validator("days_per_week")
    def validate_days_per_week(cls, value: int) -> int:
        """
        校验 days_per_week 必须在 1 到 7 之间
        """
        if not (1 <= value <= 7):
            raise ValueError("days_per_week must be between 1 and 7")
        return value

    @field_validator("workout_duration")
    def validate_workout_duration(cls, value: int) -> int:
        """
        校验 workout_duration 必须至少为 10 分钟
        """
        if value < 10:
            raise ValueError("workout_duration must be at least 10 minutes")
        return value

    @field_validator("rest_days", mode="before")
    def validate_rest_days(cls, value: List[str]) -> List[str]:
        """
        校验 rest_days 中的每个值必须是有效的星期
        """
        valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
        for day in value:
            if day not in valid_days:
                raise ValueError(f"Invalid rest day: {day}. Must be one of {valid_days}")
        return value
