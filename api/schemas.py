from datetime import date
from typing import List

from pydantic import BaseModel


# User models
class UserRoutineText(BaseModel):
    user_speech: str


class UserSugestion(BaseModel):
    date: date
    sugestion: str


class User(BaseModel):
    username: str
    password: str
    effort: int
    basic_info: str
    birth_date: date

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    username: str
    effort: int
    basic_info: str
    birth_date: date

    class Config:
        orm_mode = True


class UserFullInfo(BaseModel):
    name: str
    password: str
    effort: int
    goals: dict  # goal : true/false => wheather the goal is done or not
    basic_info: str
    sugestions: list[UserSugestion] = []


class NewUser(BaseModel):
    name: str
    password: str
    effort: int
    goals: list[str]  # goal : true/false => wheather the goal is done or not
    basic_info: str


class Goal(BaseModel):
    user_id: int
    goal: str
    is_completed: bool


class CheckGoal(BaseModel):
    user_id: int
    checked_goal: str


class AddGoalsRequest(BaseModel):
    user_id: int
    new_goals: List[str]


class Sugestion(BaseModel):
    user_id: int
    date: str
    sugestion: str


class SugestionsRequest(BaseModel):
    user_id: int
    day_transcription: str
