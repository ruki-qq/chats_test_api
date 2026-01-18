from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, CheckConstraint, ForeignKey, String, func

from .base import Base


if TYPE_CHECKING:
    from .chat import Chat


class Message(Base):
    """
    Model for messages

    Fields:
        chat_id: INT - points at this message's chat (M-1)
        text: VARCHAR - message text, non-empty, max lenght (5000)
        created_at: timestamp with time zone - message's creation time

    Relationships:
        chat: Chat - points at this message's chat
    """

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(
        String(5000),
        CheckConstraint("length(text) > 0", name="text_not_empty"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    chat: Mapped["Chat"] = relationship(back_populates="messages", lazy="joined")
