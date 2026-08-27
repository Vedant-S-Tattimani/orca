import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import db_manager
from unittest.mock import AsyncMock, patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_db():
    with patch("app.services.user_service.db_manager") as mock_db_mgr:
        mock_collection = AsyncMock()
        mock_db_mgr.db = {"users": mock_collection}
        
        # Mock find_one for login/register
        mock_collection.find_one.return_value = None
        
        # Mock insert_one
        mock_insert_result = AsyncMock()
        mock_insert_result.inserted_id = "test-id-123"
        mock_collection.insert_one.return_value = mock_insert_result
        
        yield mock_collection

def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "email": "test-ci@orca.com",
        "password": "strongpassword123",
        "full_name": "CI User",
        "role": "fisherman"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test-ci@orca.com"
    assert "id" in data

def test_login_user(mock_db):
    # Setup mock to return a user with a valid hashed password for 'strongpassword123'
    from app.services.auth_service import get_password_hash
    mock_db.find_one.return_value = {
        "email": "test-ci@orca.com",
        "hashed_password": get_password_hash("strongpassword123"),
        "role": "fisherman",
        "disabled": False
    }
    
    response = client.post("/api/v1/auth/login", data={
        "username": "test-ci@orca.com",
        "password": "strongpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
