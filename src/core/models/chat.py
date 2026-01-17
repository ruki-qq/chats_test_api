from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, CheckConstraint, String, func

from .base import Base

if TYPE_CHECKING:
    from .message import Message


class Chat(Base):
    """
    Model for chats

    Fields:
        title: VARCHAR - chat title, must not be empty
        created_at: date - chat's creation time

    Relationships:
        messages: lits[Message] - points at chat's messages
    """

    title: Mapped[str] = mapped_column(
        String(200),
        CheckConstraint("length(video_path) > 0", name="video_path_not_empty"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat",
        lazy="selectin",
    )
