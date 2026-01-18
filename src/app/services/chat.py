from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.models import Chat, Message


class ChatService:
    @staticmethod
    async def get_chat(session: AsyncSession, chat_id: int) -> Chat | None:
        """
        Get chat by id

        Args:
            session: AsyncSession - db async session
            chat_id: int - chat's id to retrieve

        Returns:
            Chat or None
        """

        return await session.get(Chat, chat_id)

    @staticmethod
    async def get_recent_messages(
        session: AsyncSession, chat_id: int, limit: int
    ) -> list[Message]:
        """
        Get list of messages in chat limited by limit

        Args:
            session: AsyncSession - db async session
            chat_id: int - chat's id to retrieve messages from
            limit: int - how many messages to retrieve

        Returns:
            list[Message] - retrieved messages
        """

        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create_chat(session: AsyncSession, title: str) -> Chat:
        """
        Create a new chat

        Args:
            session: AsyncSession - db async session
            title: str - chat's title, non-empty

        Returns:
            Chat - created chat
        """
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        title = title.strip()
        if title == "":
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        chat = Chat(title=title)
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat

    @classmethod
    async def create_message(
        cls, session: AsyncSession, chat_id: int, text: str
    ) -> Message:
        """
        Create message in chat

        Args:
            session: AsyncSession - db async session
            chat_id: int - chat's id to create message in
            text: str - message's text

        Returns:
            Message - created message
        """

        text = text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        chat = await cls.get_chat(session, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        message = Message(chat_id=chat_id, text=text)
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    @classmethod
    async def delete_chat(cls, session: AsyncSession, chat_id: int) -> None:
        """
        Delete chat by id

        Args:
            session: AsyncSession - db async session
            chat_id: int - chat's id to delete

        Returns:
            None
        """

        chat = await cls.get_chat(session, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        await session.delete(chat)
        await session.commit()
