from datetime import datetime

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    chat_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
