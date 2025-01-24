from asyncio import create_task
from datetime import datetime

from database import get_db
from deps import openai_client
from fastapi import APIRouter, Depends
from openai.types.chat.chat_completion import ChatCompletion
from prompts import PromptMaker
from schemas import (
    AddGoalsRequest,
    NewUser,
    SugestionsRequest,
    UserFullInfo,
    UserSugestion,
)
from service.userService import create_sugestion

router = APIRouter(tags=["AI operations"], prefix="/agent")


@router.post("/sugestion/daily")
async def sugestion_daily(req: SugestionsRequest, db=Depends(get_db)) -> UserSugestion:
    prompt_maker = PromptMaker(req.user_id)
    prompt = await prompt_maker.system_basic_sugestion(db)

    response: ChatCompletion = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": req.day_transcription,
            },
        ],
    )

    sugestion = UserSugestion(date=datetime.now().date(), sugestion=response.choices[0].message.content.strip())  # type: ignore
    create_task(
        create_sugestion(db, user_id=req.user_id, user_sugestion=sugestion)
    )  # adding sugestion to user historic sugestions
    return sugestion
