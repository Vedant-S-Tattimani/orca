"""
Tests for auth endpoint rate limiting.

Verifies that:
- Login is limited to 5 attempts per 15 minutes per IP
- Registration is limited to 3 attempts per hour per IP
- Exceeding the limit returns HTTP 429
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock, patch
from app.api.v1.auth import login_limiter, register_limiter

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Reset rate limiter state before each test so tests are isolated."""
    login_limiter.reset()
    register_limiter.reset()
    yield
    login_limiter.reset()
    register_limiter.reset()


@pytest.fixture
def mock_db():
    with patch("app.services.user_service.db_manager") as mock_db_mgr:
        mock_collection = AsyncMock()
        mock_db_mgr.db = {"users": mock_collection}
        mock_collection.find_one.return_value = None

        mock_insert_result = AsyncMock()
        mock_insert_result.inserted_id = "test-id-123"
        mock_collection.insert_one.return_value = mock_insert_result

        yield mock_collection


def test_login_rate_limit_allows_5(mock_db):
    """First 5 login attempts should be processed (even if credentials are wrong)."""
    from app.services.auth_service import get_password_hash
    mock_db.find_one.return_value = None  # No user found -> 401

    for i in range(5):
        response = client.post("/api/v1/auth/login", data={
            "username": f"user{i}@example.com",
            "password": "wrong"
        })
        # Should be 401 (bad credentials), NOT 429
        assert response.status_code == 401, f"Attempt {i+1} returned {response.status_code}"


def test_login_rate_limit_blocks_6th(mock_db):
    """The 6th login attempt within the window should return 429."""
    mock_db.find_one.return_value = None

    for i in range(5):
        client.post("/api/v1/auth/login", data={
            "username": f"user{i}@example.com",
            "password": "wrong"
        })

    # 6th attempt
    response = client.post("/api/v1/auth/login", data={
        "username": "hacker@example.com",
        "password": "bruteforce"
    })
    assert response.status_code == 429
    assert "Too many login attempts" in response.json()["detail"]


def test_register_rate_limit_allows_3(mock_db):
    """First 3 registration attempts should succeed."""
    for i in range(3):
        response = client.post("/api/v1/auth/register", json={
            "email": f"newuser{i}@example.com",
            "password": "password123",
            "full_name": f"User {i}",
            "role": "fisherman"
        })
        assert response.status_code == 200, f"Attempt {i+1} returned {response.status_code}"


def test_register_rate_limit_blocks_4th(mock_db):
    """The 4th registration attempt within the window should return 429."""
    for i in range(3):
        client.post("/api/v1/auth/register", json={
            "email": f"newuser{i}@example.com",
            "password": "password123",
            "full_name": f"User {i}",
            "role": "fisherman"
        })

    # 4th attempt
    response = client.post("/api/v1/auth/register", json={
        "email": "spammer@example.com",
        "password": "password123",
        "full_name": "Spammer",
        "role": "fisherman"
    })
    assert response.status_code == 429
    assert "Too many registration attempts" in response.json()["detail"]
