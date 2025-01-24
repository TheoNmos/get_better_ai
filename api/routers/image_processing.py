import asyncio
import base64
from ast import List
from datetime import datetime
from typing import Dict, Optional

from database import get_db, sessionmanager
from deps import openai_client
from fastapi import APIRouter, Depends, File, Form, UploadFile
from models import Base, ChatHistory
from openai.types.chat.chat_completion import ChatCompletion
from sqlalchemy import select, text

router = APIRouter(tags=["image processing with history"], prefix="/images")


async def get_user_historic_messages(user_id: int, amount: int, db) -> list[dict]:
    result = await db.execute(
        select(ChatHistory).where(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.desc()).limit(amount)
    )
    messages = result.scalars().all()
    return [
        {
            "created_at": message.created_at,
            "prompt": message.prompt,
            "response": message.response,
            "attachments_description": message.attachments_description,
        }
        for message in messages
    ]


async def post_to_user_history(
    user_id: int,
    chat_id: int,
    prompt: str,
    response: str,
    attachments_description: str | None,
    db,
):
    new_interaction = ChatHistory(
        user_id=user_id,
        chat_id=chat_id,
        created_at=datetime.utcnow(),
        prompt=prompt,
        response=response,
        attachments_description=attachments_description,
    )
    db.add(new_interaction)
    await db.commit()
    await db.refresh(new_interaction)
    print("posted interaction to user history")
    return {
        "user_id": new_interaction.user_id,
        "chat_id": new_interaction.chat_id,
        "created_at": new_interaction.created_at,
        "prompt": new_interaction.prompt,
        "response": new_interaction.response,
        "attachments_description": new_interaction.attachments_description,
    }


@router.post("/process_question")
async def process_image(
    user_id: int = Form(...), prompt: str = Form(...), image: Optional[UploadFile] = None, db=Depends(get_db)
) -> Dict[str, str]:
    """
    In this route the chat interprets images and describes them, adding those descriptions to the historic_chats table
    """

    image_base64 = None
    if image:
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode("utf-8")

    async def get_response(prompt: str, image_base64: str | None) -> str:
        historic_messages = await get_user_historic_messages(user_id, 10, db)

        messages = [
            {
                "role": "system",
                "content": """
                        You should answer the users question in a polite and concise way, matching the formality of the user's language. 
                        If an image is sent, look at it and use it to answer the question.
                        Use the last messages as context to answer the present question if you dont think you have enought information.
                        There are descriptions about the last images the user has sent in the attachments_description field, inside the users last messages.
                    """,
            },
            {
                "role": "system",
                "content": f" This are the user last messages {historic_messages}",  # correct the typing on this latter
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            },
        ]

        if image_base64:
            # only adds image if the user sends one
            messages[2]["content"].append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            )

        response: ChatCompletion = await openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages)

        return response.choices[0].message.content.strip()  # type: ignore

    async def get_description(prompt: str, image_base64: str | None) -> str | None:
        """
        calls the LLM model to describe the image sent by user, if there is one
        """

        if not image_base64:
            return None

        response: ChatCompletion = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You should describe the image sent by the user, focusing in what is asked in the user question. Your description should cover everything you consider important in the image, but there is no need for details.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},  # maybe removing this would not make much difference
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                    ],
                },  # type: ignore
            ],
        )

        return response.choices[0].message.content.strip()  # type: ignore

    main_task = asyncio.create_task(get_response(prompt, image_base64))
    description_task = asyncio.create_task(get_description(prompt, image_base64))

    # paralell execution of the tasks
    final_response, img_description = await asyncio.gather(main_task, description_task)

    asyncio.create_task(
        post_to_user_history(
            user_id, 1, prompt, final_response, img_description, db
        )  # using 1 as the chat_id just as an example
    )  # no need to wait for response to proceed with execution

    return {"response": final_response, "description": img_description if img_description else "No image in request"}
