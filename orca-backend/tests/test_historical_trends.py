import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.auth_service import create_access_token

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_db():
    with patch("app.api.v1.historical.db_manager") as mock_db_mgr, \
         patch("app.api.deps.UserService.get_user_by_email") as mock_get_user:
        
        # Mock get_user_by_email to bypass 401
        async def mock_user(email):
            if "researcher" in email:
                return {"email": email, "role": "researcher"}
            return {"email": email, "role": "fisherman"}
        mock_get_user.side_effect = mock_user

        mock_collection = MagicMock()
        mock_db_mgr.db = {"historical_readings": mock_collection}
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = [
            {"_id": "test_id_1", "location": "Mangalore-Coast", "sst": 28.5, "chlorophyll": 1.2, "timestamp": "2024-01-01T00:00:00Z"}
        ]
        
        # mock_collection.find().sort().limit() chain
        mock_find = MagicMock()
        mock_sort = MagicMock()
        mock_sort.limit.return_value = mock_cursor
        mock_find.sort.return_value = mock_sort
        mock_collection.find.return_value = mock_find
        
        yield mock_collection

def test_historical_trends_unauthorized():
    response = client.get("/api/v1/historical/trends?location=Mangalore-Coast&days=7")
    assert response.status_code == 401

def test_historical_trends_fisherman_forbidden():
    # Create fisherman token
    token = create_access_token(data={"sub": "test@orca.com", "role": "fisherman"})
    response = client.get(
        "/api/v1/historical/trends?location=Mangalore-Coast&days=7",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Operation not permitted" in response.json()["detail"]

def test_historical_trends_researcher_success():
    # Create researcher token
    token = create_access_token(data={"sub": "researcher@orca.com", "role": "researcher"})
    
    # Patch the db_manager used inside the historical endpoint with event-per-metric mock docs
    from datetime import datetime
    mock_docs = [
        {"_id": "id1", "location": "Mangalore-Coast", "type": "sst", "value": 28.5,
         "timestamp": datetime(2024, 1, 1), "created_at": datetime(2024, 1, 1)},
        {"_id": "id2", "location": "Mangalore-Coast", "type": "chlorophyll", "value": 1.2,
         "timestamp": datetime(2024, 1, 1), "created_at": datetime(2024, 1, 1)},
    ]
    
    mock_cursor = AsyncMock()
    mock_cursor.__aiter__.return_value = mock_docs
    
    mock_find = MagicMock()
    mock_sort = MagicMock()
    mock_sort.limit.return_value = mock_cursor
    mock_find.sort.return_value = mock_sort
    
    with patch("app.api.v1.historical.db_manager") as mock_db_mgr, \
         patch("app.api.deps.UserService.get_user_by_email") as mock_get_user:
        async def mock_user(email):
            return {"email": email, "role": "researcher"}
        mock_get_user.side_effect = mock_user
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_find
        mock_db_mgr.db = {"historical_readings": mock_collection}
        
        response = client.get(
            "/api/v1/historical/trends?location=Mangalore-Coast&days=7",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 1
    # The pivot logic groups by date and maps type -> field name
    assert data["data"][0]["sst"] == 28.5
    assert data["data"][0]["chlorophyll"] == 1.2

