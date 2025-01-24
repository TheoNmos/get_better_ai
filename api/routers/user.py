from typing import Any, List

import service.userService as userService
from database import get_db
from fastapi import APIRouter, Depends
from schemas import (
    AddGoalsRequest,
    CheckGoal,
    Goal,
    User,
    UserOut,
)

router = APIRouter(tags=["User operations"], prefix="/users")


@router.get("/", response_model=List[UserOut])
async def get_users(db=Depends(get_db)):
    users = await userService.get_all_users(db)
    return users


@router.get("/goals", response_model=List[Goal])
async def get_user_goals(user_id: int, db=Depends(get_db)):
    user_goals = await userService.get_user_goals(db, user_id)
    return user_goals


@router.post("/goals")
async def add_goals(request: AddGoalsRequest, db=Depends(get_db)) -> List[str]:
    await userService.add_user_goals(db=db, user_id=request.user_id, goals=request.new_goals)
    return request.new_goals


@router.post("/")
async def add_user(new_user: User, db=Depends(get_db)) -> User:
    return await userService.create_user(db, new_user)


@router.post("/goals/check")
async def change_goal_state(goal: CheckGoal, db=Depends(get_db)) -> Goal:
    return await userService.change_goal_state(db, goal.user_id, goal.checked_goal)


@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(user_id: int, db=Depends(get_db)) -> UserOut:
    user: UserOut = await userService.get_basic_user_by_id(db, user_id)
    return user
