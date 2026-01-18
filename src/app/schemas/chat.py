from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .message import MessageResponse


class ChatBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class ChatCreate(ChatBase):
    pass


class ChatResponse(ChatBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatWithMessages(BaseModel):
    chat: ChatResponse
    messages: list["MessageResponse"]

    model_config = {"from_attributes": True}
