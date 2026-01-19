from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.app import app
from core import db_helper
from core.models import Chat, Message

CHAT_URL = "/api/chats"
LIMIT_MESSAGES = 20


def override_db_session(session: AsyncSession) -> None:
    """Override db session dependencies"""

    def override_get_scoped_session():
        return session

    async def override_session_dependency():
        yield session

    app.dependency_overrides[db_helper.get_scoped_session] = override_get_scoped_session
    app.dependency_overrides[db_helper.session_dependency] = override_session_dependency


async def create_chat(client: AsyncClient, title: str) -> Chat:
    return await client.post(CHAT_URL, json={"title": title})


async def create_message(client: AsyncClient, chat_id: int, text: str) -> Message:
    return await client.post(
        f"{CHAT_URL}/{chat_id}/messages",
        json={"text": text},
    )
