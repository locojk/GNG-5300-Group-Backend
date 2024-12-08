"""
Create or Update Goal Request Validation Schema

@Date: 2024-11-23
@Author: Adam Lyu
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
        Validate if the goal is a valid value.
        """
        valid_goals = {"strength", "weight_loss", "flexibility"}
        if value not in valid_goals:
            raise ValueError(f"Invalid goal: {value}. Must be one of {valid_goals}")
        return value

    @field_validator("days_per_week")
    def validate_days_per_week(cls, value: int) -> int:
        """
        Validate that days_per_week is between 1 and 7.
        """
        if not (1 <= value <= 7):
            raise ValueError("days_per_week must be between 1 and 7")
        return value

    @field_validator("workout_duration")
    def validate_workout_duration(cls, value: int) -> int:
        """
        Validate that workout_duration is at least 10 minutes.
        """
        if value < 10:
            raise ValueError("workout_duration must be at least 10 minutes")
        return value

    @field_validator("rest_days", mode="before")
    def validate_rest_days(cls, value: List[str]) -> List[str]:
        """
        Validate that each value in rest_days is a valid day of the week.
        """
        valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
        for day in value:
            if day not in valid_days:
                raise ValueError(f"Invalid rest day: {day}. Must be one of {valid_days}")
        return value
