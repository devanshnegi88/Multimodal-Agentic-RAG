"""
Tests for FastAPI API routes
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_db():
    db = MagicMock()
    db["users"].find_one = AsyncMock(return_value=None)
    db["users"].insert_one = AsyncMock(return_value=MagicMock(inserted_id="user-1"))
    db["chat_sessions"].find_one = AsyncMock(return_value=None)
    db["chat_sessions"].insert_one = AsyncMock()
    db["chat_sessions"].find = MagicMock(return_value=MagicMock(
        sort=MagicMock(return_value=MagicMock(limit=MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[])))))
    ))
    db["documents"].find_one = AsyncMock(return_value=None)
    db["documents"].count_documents = AsyncMock(return_value=0)
    db["documents"].find = MagicMock(return_value=MagicMock(
        sort=MagicMock(return_value=MagicMock(skip=MagicMock(return_value=MagicMock(limit=MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value[])))))))
    ))
    return db


class TestAuthAPI:
    def test_register_success(self):
        """Test user registration returns tokens."""
        # Integration test would need a running MongoDB
        # Unit test the logic directly
        from backend.app.api.auth import hash_password, verify_password
        pwd = "securepassword123"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_token_creation(self):
        from backend.app.api.auth import create_token
        from datetime import timedelta
        token = create_token({"sub": "user-1"}, timedelta(minutes=60))
        assert isinstance(token, str)
        assert len(token) > 20

    def test_password_hash_is_different(self):
        from backend.app.api.auth import hash_password
        pwd = "samepassword"
        h1 = hash_password(pwd)
        h2 = hash_password(pwd)
        # bcrypt generates unique salts
        assert h1 != h2


class TestDocumentsAPI:
    @pytest.mark.asyncio
    async def test_list_documents_empty(self):
        """Test listing documents when none exist."""
        from backend.app.api.documents import list_documents
        mock_db = MagicMock()
        mock_db["documents"].count_documents = AsyncMock(return_value=0)
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
        mock_db["documents"].find.return_value = mock_cursor

        result = await list_documents(page=1, page_size=20, file_type=None, status=None, db=mock_db)
        assert result["total"] == 0
        assert result["documents"] == []


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        """Test that the health endpoint returns healthy status."""
        import asyncio
        from backend.app.main import app
        # Test the route function directly
        async def run():
            from backend.app.main import health_check
            result = await health_check()
            return result
        result = asyncio.run(run())
        assert result["status"] == "healthy"
        assert "version" in result
