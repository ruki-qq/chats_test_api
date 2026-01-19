from httpx import AsyncClient

from .utils import CHAT_URL, LIMIT_MESSAGES, create_chat, create_message


class TestCreateChat:
    """Tests for POST {CHAT_URL}"""

    async def test_create_chat_success(self, client: AsyncClient):
        response = await create_chat(client, "Test Chat")

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Chat"
        assert "id" in data
        assert "created_at" in data
        assert isinstance(data["id"], int)

    async def test_create_chat_min_length_title(self, client: AsyncClient):
        response = await create_chat(client, "A")

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "A"

    async def test_create_chat_max_length_title(self, client: AsyncClient):
        max_title = "A" * 200
        response = await create_chat(client, max_title)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == max_title

    async def test_create_chat_empty_title(self, client: AsyncClient):
        """Creating a chat with empty title should fail"""

        response = await create_chat(client, "")

        assert response.status_code == 422

    async def test_create_chat_missing_title(self, client: AsyncClient):
        """Creating a chat without title field should fail"""

        response = await client.post(CHAT_URL, json={})

        assert response.status_code == 422

    async def test_create_chat_title_too_long(self, client: AsyncClient):
        """Creating a chat with title exceeding max length should fail"""

        long_title = "A" * 201
        response = await create_chat(client, long_title)

        assert response.status_code == 422


class TestGetChatDetail:
    """Tests for GET {CHAT_URL}/{chat_id}"""

    async def test_get_chat_detail_success(self, client: AsyncClient):
        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        response = await client.get(f"{CHAT_URL}/{chat_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["chat"]["id"] == chat_id
        assert data["chat"]["title"] == "Test Chat"
        assert "chat" in data
        assert "messages" in data
        assert isinstance(data["messages"], list)

    async def test_get_chat_detail_with_messages(self, client: AsyncClient):
        create_response = await create_chat(client, "Chat with Messages")
        chat_id = create_response.json()["id"]

        await create_message(client, chat_id, "First message")
        await create_message(client, chat_id, "Second message")

        response = await client.get(f"{CHAT_URL}/{chat_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2
        message_texts = {msg["text"] for msg in data["messages"]}
        assert "First message" in message_texts
        assert "Second message" in message_texts

    async def test_get_chat_detail_with_limit(self, client: AsyncClient):
        create_response = await create_chat(client, "Limited Chat")
        chat_id = create_response.json()["id"]

        for i in range(5):
            await create_message(client, chat_id, f"Message {i}")

        response = await client.get(f"{CHAT_URL}/{chat_id}?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 3

    async def test_get_chat_detail_limit_default(self, client: AsyncClient):
        """Test default limit is LIMIT_MESSAGES"""

        create_response = await create_chat(client, "Default Limit Chat")
        chat_id = create_response.json()["id"]

        for i in range(25):
            await create_message(client, chat_id, f"Message {i}")

        response = await client.get(f"{CHAT_URL}/{chat_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == LIMIT_MESSAGES

    async def test_get_chat_detail_limit_min(self, client: AsyncClient):
        """Test minimum limit constraint"""

        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        response = await client.get(f"{CHAT_URL}/{chat_id}?limit=0")
        assert response.status_code == 422

    async def test_get_chat_detail_limit_max(self, client: AsyncClient):
        """Test maximum limit constraint"""

        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        response = await client.get(f"{CHAT_URL}/{chat_id}?limit=101")
        assert response.status_code == 422

    async def test_get_chat_detail_not_found(self, client: AsyncClient):
        """Getting a non-existent chat"""

        response = await client.get("{CHAT_URL}/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteChat:
    """Tests for DELETE {CHAT_URL}/{chat_id}"""

    async def test_delete_chat_success(self, client: AsyncClient):
        create_response = await create_chat(client, "To Be Deleted")
        chat_id = create_response.json()["id"]

        response = await client.delete(f"{CHAT_URL}/{chat_id}")
        assert response.status_code == 204

        get_response = await client.get(f"{CHAT_URL}/{chat_id}")
        assert get_response.status_code == 404

    async def test_delete_chat_with_message_success(self, client: AsyncClient):
        create_response = await create_chat(client, "To Be Deleted")
        chat_id = create_response.json()["id"]

        await create_message(client, chat_id, "Message")

        response = await client.delete(f"{CHAT_URL}/{chat_id}")
        assert response.status_code == 204

        get_response = await client.get(f"{CHAT_URL}/{chat_id}")
        assert get_response.status_code == 404

    async def test_delete_chat_not_found(self, client: AsyncClient):
        """Deleting a non-existent chat"""

        response = await client.delete(f"{CHAT_URL}/99999")
        assert response.status_code == 404


class TestCreateMessage:
    """Tests for POST {CHAT_URL}/{chat_id}/messages"""

    async def test_create_message_success(self, client: AsyncClient):
        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        response = await create_message(client, chat_id, "Hello, world!")

        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "Hello, world!"
        assert data["chat_id"] == chat_id
        assert "id" in data
        assert "created_at" in data
        assert isinstance(data["id"], int)

    async def test_create_message_min_length(self, client: AsyncClient):
        """Creating a message with minimum length text"""

        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        response = await create_message(client, chat_id, "A")

        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "A"

    async def test_create_message_max_length(self, client: AsyncClient):
        """Creating a message with maximum length text"""
        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        max_text = "A" * 5000
        response = await create_message(client, chat_id, max_text)

        assert response.status_code == 201
        data = response.json()
        assert data["text"] == max_text

    async def test_create_message_empty_text(self, client: AsyncClient):
        """Creating a message with empty text should fail"""

        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        response = await create_message(client, chat_id, "")

        assert response.status_code == 422

    async def test_create_message_missing_text(self, client: AsyncClient):
        """Creating a message without text field should fail"""

        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        response = await client.post(
            f"{CHAT_URL}/{chat_id}/messages",
            json={},
        )

        assert response.status_code == 422

    async def test_create_message_text_too_long(self, client: AsyncClient):
        """Creating a message with text exceeding max length should fail"""

        create_response = await create_chat(client, "Test Chat")
        chat_id = create_response.json()["id"]

        long_text = "A" * 5001
        response = await create_message(client, chat_id, long_text)

        assert response.status_code == 422

    async def test_create_message_chat_not_found(self, client: AsyncClient):
        """Creating a message in a non-existent chat"""

        response = await create_message(client, 99999, "This should fail")

        assert response.status_code == 404

    async def test_create_multiple_messages(self, client: AsyncClient):
        create_response = await create_chat(client, "Multi Message Chat")
        chat_id = create_response.json()["id"]

        messages = ["First", "Second", "Third"]
        created_messages = []
        for text in messages:
            response = await create_message(client, chat_id, text)

            assert response.status_code == 201
            created_messages.append(response.json())

        assert len(created_messages) == 3
        for msg in created_messages:
            assert msg["chat_id"] == chat_id
            assert msg["text"] in messages

        get_response = await client.get(f"{CHAT_URL}/{chat_id}")

        chat_data = get_response.json()
        assert len(chat_data["messages"]) == 3
        message_texts = {msg["text"] for msg in chat_data["messages"]}
        assert message_texts == {"First", "Second", "Third"}
