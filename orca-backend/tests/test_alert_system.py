import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_db():
    from unittest.mock import MagicMock
    with patch("app.services.alert_service.db_manager") as mock_db_mgr:
        mock_collection = MagicMock()
        mock_subs_collection = MagicMock()
        mock_db_mgr.db = {
            "hazard_advisories": mock_collection,
            "alert_subscriptions": mock_subs_collection
        }
        
        # Mock insert_one
        mock_collection.insert_one = AsyncMock()
        
        # Mock find for hazard_advisories
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = [
            {"title": "CI Test Alert", "severity": "WARNING"}
        ]
        from unittest.mock import MagicMock
        mock_find_result = MagicMock()
        mock_find_result.sort.return_value = mock_cursor
        mock_collection.find.return_value = mock_find_result
        
        # Mock find for alert_subscriptions
        mock_subs_cursor = AsyncMock()
        mock_subs_cursor.to_list.return_value = []
        mock_subs_collection.find.return_value = mock_subs_cursor
        
        yield mock_collection

def test_push_alert():
    response = client.post("/api/alerts", json={
        "title": "CI Test Alert",
        "severity": "WARNING",
        "location": "CI Location",
        "hazard": "Testing hazard",
        "recommended_action": "Do nothing"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["alert"]["title"] == "CI Test Alert"

def test_get_alerts():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    alerts = response.json()
    
    found = any(a.get("title") == "CI Test Alert" for a in alerts)
    assert found
