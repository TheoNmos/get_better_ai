from typing import Sequence

import bcrypt
from models import Goal as GoalModel
from models import Suggestion as SugestionModel
from models import User as UserModel
from schemas import Goal, User, UserSugestion
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def build_model_ORM(user: User) -> UserModel:
    user_data = user.model_dump()
    user_ORM = UserModel(**user_data)
    return user_ORM


async def create_user(db: AsyncSession, user: User):
    user.password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_ORM: UserModel = await build_model_ORM(user)
    db.add(user_ORM)
    await db.commit()
    await db.refresh(user_ORM)
    return user_ORM


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(UserModel))
    return result.scalars().all()


async def get_full_user_by_id(db: AsyncSession, user_id: int) -> UserModel:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalars().first()


async def get_basic_user_by_id(db: AsyncSession, user_id: int) -> UserModel:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalars().first()


async def get_user_goals(db: AsyncSession, user_id: int) -> Sequence[Goal]:
    result = await db.execute(select(GoalModel).where(GoalModel.user_id == user_id))
    data = result.scalars().all()
    return data


async def add_user_goals(db: AsyncSession, user_id: int, goals: list[str]):
    try:
        goals_orm: list[GoalModel] = [GoalModel(user_id=user_id, goal=goal, is_completed=False) for goal in goals]
        print(goals_orm[0].goal)
        db.add_all(goals_orm)
        await db.commit()
        for goal in goals_orm:
            await db.refresh(goal)
    except Exception as e:
        await db.rollback()
        raise e


async def create_sugestion(db: AsyncSession, user_id: int, user_sugestion: UserSugestion):
    sugestion_orm = SugestionModel(
        user_id=user_id, suggestion=user_sugestion.sugestion, suggestion_date=user_sugestion.date
    )
    db.add(sugestion_orm)
    await db.commit()
    await db.refresh(sugestion_orm)
    print("saved sugestion on history")


async def get_last_sugestions(db: AsyncSession, user_id: int, amount: int | None = None):
    result = await db.execute(
        select(SugestionModel)
        .where(SugestionModel.user_id == user_id)
        .order_by(SugestionModel.suggestion_date.desc())
        .limit(amount)
    )
    data = result.scalars().all()
    return data


async def change_goal_state(db: AsyncSession, user_id: int, goal: str):
    try:
        result = await db.execute(select(GoalModel).where(GoalModel.goal == goal, GoalModel.user_id == user_id))
        goal_orm = result.scalars().first()
        if goal_orm:
            # inverting the current value
            goal_orm.is_completed = not goal_orm.is_completed  # type: ignore
            await db.commit()
            await db.refresh(goal_orm)
            return goal_orm
        else:
            raise ValueError("Goal not found")
    except Exception as e:
        await db.rollback()
        raise e
