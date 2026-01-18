from httpx import AsyncClient


class TestCreateChat:
    """Tests for POST /api/chats/"""

    async def test_create_chat_success(self, client: AsyncClient):
        """Test successfully creating a chat"""
        response = await client.post("/api/chats/", json={"title": "Test Chat"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Chat"
        assert "id" in data
        assert "created_at" in data
        assert isinstance(data["id"], int)

    async def test_create_chat_min_length_title(self, client: AsyncClient):
        """Test creating a chat with minimum length title"""
        response = await client.post("/api/chats/", json={"title": "A"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "A"

    async def test_create_chat_max_length_title(self, client: AsyncClient):
        """Test creating a chat with maximum length title"""
        max_title = "A" * 200
        response = await client.post("/api/chats/", json={"title": max_title})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == max_title

    async def test_create_chat_empty_title(self, client: AsyncClient):
        """Test creating a chat with empty title should fail"""
        response = await client.post("/api/chats/", json={"title": ""})
        assert response.status_code == 422

    async def test_create_chat_missing_title(self, client: AsyncClient):
        """Test creating a chat without title field should fail"""
        response = await client.post("/api/chats/", json={})
        assert response.status_code == 422

    async def test_create_chat_title_too_long(self, client: AsyncClient):
        """Test creating a chat with title exceeding max length should fail"""
        long_title = "A" * 201
        response = await client.post("/api/chats/", json={"title": long_title})
        assert response.status_code == 422


class TestGetChatDetail:
    """Tests for GET /api/chats/{chat_id}"""

    async def test_get_chat_detail_success(self, client: AsyncClient):
        """Test successfully getting a chat with messages"""
        # Create a chat first
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        # Get chat detail
        response = await client.get(f"/api/chats/{chat_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["chat"]["id"] == chat_id
        assert data["chat"]["title"] == "Test Chat"
        assert "chat" in data
        assert "messages" in data
        assert isinstance(data["messages"], list)

    async def test_get_chat_detail_with_messages(self, client: AsyncClient):
        """Test getting a chat with messages"""
        # Create a chat
        create_response = await client.post(
            "/api/chats/", json={"title": "Chat with Messages"}
        )
        chat_id = create_response.json()["id"]

        # Create some messages
        await client.post(
            f"/api/chats/{chat_id}/messages",
            json={"text": "First message"},
        )
        await client.post(
            f"/api/chats/{chat_id}/messages",
            json={"text": "Second message"},
        )

        # Get chat detail
        response = await client.get(f"/api/chats/{chat_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2
        # Messages should be returned (order may vary if timestamps are identical)
        message_texts = {msg["text"] for msg in data["messages"]}
        assert "First message" in message_texts
        assert "Second message" in message_texts

    async def test_get_chat_detail_with_limit(self, client: AsyncClient):
        """Test getting a chat with message limit"""
        # Create a chat
        create_response = await client.post(
            "/api/chats/", json={"title": "Limited Chat"}
        )
        chat_id = create_response.json()["id"]

        # Create 5 messages
        for i in range(5):
            await client.post(
                f"/api/chats/{chat_id}/messages",
                json={"text": f"Message {i}"},
            )

        # Get chat with limit of 3
        response = await client.get(f"/api/chats/{chat_id}?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 3

    async def test_get_chat_detail_limit_default(self, client: AsyncClient):
        """Test default limit is 20"""
        # Create a chat
        create_response = await client.post(
            "/api/chats/", json={"title": "Default Limit Chat"}
        )
        chat_id = create_response.json()["id"]

        # Create 25 messages
        for i in range(25):
            await client.post(
                f"/api/chats/{chat_id}/messages",
                json={"text": f"Message {i}"},
            )

        # Get chat without specifying limit
        response = await client.get(f"/api/chats/{chat_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 20  # Default limit

    async def test_get_chat_detail_limit_min(self, client: AsyncClient):
        """Test minimum limit constraint"""
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        response = await client.get(f"/api/chats/{chat_id}?limit=0")
        assert response.status_code == 422

    async def test_get_chat_detail_limit_max(self, client: AsyncClient):
        """Test maximum limit constraint"""
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        response = await client.get(f"/api/chats/{chat_id}?limit=101")
        assert response.status_code == 422

    async def test_get_chat_detail_not_found(self, client: AsyncClient):
        """Test getting a non-existent chat"""
        response = await client.get("/api/chats/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteChat:
    """Tests for DELETE /api/chats/{chat_id}"""

    async def test_delete_chat_success(self, client: AsyncClient):
        """Test successfully deleting a chat"""
        # Create a chat
        create_response = await client.post(
            "/api/chats/", json={"title": "To Be Deleted"}
        )
        chat_id = create_response.json()["id"]

        # Delete the chat
        response = await client.delete(f"/api/chats/{chat_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/chats/{chat_id}")
        assert get_response.status_code == 404

    async def test_delete_chat_not_found(self, client: AsyncClient):
        """Test deleting a non-existent chat"""
        response = await client.delete("/api/chats/99999")
        assert response.status_code == 404


class TestCreateMessage:
    """Tests for POST /api/chats/{chat_id}/messages"""

    async def test_create_message_success(self, client: AsyncClient):
        """Test successfully creating a message"""
        # Create a chat first
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        # Create a message
        response = await client.post(
            f"/api/chats/{chat_id}/messages",
            json={"text": "Hello, world!"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "Hello, world!"
        assert data["chat_id"] == chat_id
        assert "id" in data
        assert "created_at" in data
        assert isinstance(data["id"], int)

    async def test_create_message_min_length(self, client: AsyncClient):
        """Test creating a message with minimum length text"""
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        response = await client.post(
            f"/api/chats/{chat_id}/messages",
            json={"text": "A"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "A"

    async def test_create_message_max_length(self, client: AsyncClient):
        """Test creating a message with maximum length text"""
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        max_text = "A" * 5000
        response = await client.post(
            f"/api/chats/{chat_id}/messages",
            json={"text": max_text},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == max_text

    async def test_create_message_empty_text(self, client: AsyncClient):
        """Test creating a message with empty text should fail"""
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        response = await client.post(
            f"/api/chats/{chat_id}/messages",
            json={"text": ""},
        )
        assert response.status_code == 422

    async def test_create_message_missing_text(self, client: AsyncClient):
        """Test creating a message without text field should fail"""
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        response = await client.post(
            f"/api/chats/{chat_id}/messages",
            json={},
        )
        assert response.status_code == 422

    async def test_create_message_text_too_long(self, client: AsyncClient):
        """Test creating a message with text exceeding max length should fail"""
        create_response = await client.post("/api/chats/", json={"title": "Test Chat"})
        chat_id = create_response.json()["id"]

        long_text = "A" * 5001
        response = await client.post(
            f"/api/chats/{chat_id}/messages",
            json={"text": long_text},
        )
        assert response.status_code == 422

    async def test_create_message_chat_not_found(self, client: AsyncClient):
        """Test creating a message in a non-existent chat"""
        response = await client.post(
            "/api/chats/99999/messages",
            json={"text": "This should fail"},
        )
        assert response.status_code == 404

    async def test_create_multiple_messages(self, client: AsyncClient):
        """Test creating multiple messages in a chat"""
        create_response = await client.post(
            "/api/chats/", json={"title": "Multi Message Chat"}
        )
        chat_id = create_response.json()["id"]

        # Create multiple messages
        messages = ["First", "Second", "Third"]
        created_messages = []
        for text in messages:
            response = await client.post(
                f"/api/chats/{chat_id}/messages",
                json={"text": text},
            )
            assert response.status_code == 201
            created_messages.append(response.json())

        # Verify all messages are created
        assert len(created_messages) == 3
        for msg in created_messages:
            assert msg["chat_id"] == chat_id
            assert msg["text"] in messages

        # Get chat and verify all messages are present
        get_response = await client.get(f"/api/chats/{chat_id}")
        chat_data = get_response.json()
        assert len(chat_data["messages"]) == 3
        # Verify all messages are present (order may vary if timestamps are identical)
        message_texts = {msg["text"] for msg in chat_data["messages"]}
        assert message_texts == {"First", "Second", "Third"}
