from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_helper
from app.services import ChatService
from app.schemas.chat import ChatCreate, ChatResponse, ChatWithMessages
from app.schemas.message import MessageCreate, MessageResponse


router = APIRouter(prefix="/chats", tags=["chats"])

messages_router = APIRouter(tags=["messages"])


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_new_chat(
    chat_in: ChatCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    chat = await ChatService.create_chat(session, chat_in.title)
    return ChatResponse.model_validate(chat)


@router.get("/{chat_id}", response_model=ChatWithMessages)
async def get_chat_detail(
    chat_id: int,
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    chat = await ChatService.get_chat(session, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = await ChatService.get_recent_messages(session, chat_id, limit)

    return ChatWithMessages(
        chat=ChatResponse.model_validate(chat),
        messages=[MessageResponse.model_validate(msg) for msg in messages],
    )


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_chat(
    chat_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    await ChatService.delete_chat(session, chat_id)


@messages_router.post(
    "/{chat_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message_to_chat(
    chat_id: int,
    message_in: MessageCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    message = await ChatService.create_message(session, chat_id, message_in.text)
    return MessageResponse.model_validate(message)


router.include_router(messages_router)
