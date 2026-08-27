import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.auth_service import create_access_token
import csv
import io

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_db():
    with patch("app.api.v1.reports.db_manager") as mock_db_mgr, \
         patch("app.api.deps.UserService.get_user_by_email") as mock_get_user:
        
        async def mock_user(email):
            if "researcher" in email:
                return {"email": email, "role": "researcher"}
            return {"email": email, "role": "fisherman"}
        mock_get_user.side_effect = mock_user

        mock_db = MagicMock()
        mock_db_mgr.db = mock_db
        
        # Mock historical cursor
        mock_hist_cursor = AsyncMock()
        mock_hist_cursor.to_list.return_value = [
            {"_id": "test_hist_1", "location": "Mangalore-Coast", "type": "sst", "value": 28.5, "timestamp": "2024-01-01T00:00:00Z"}
        ]
        
        # mock_collection.find().sort().limit() chain for historical
        mock_hist_find = MagicMock()
        mock_hist_sort = MagicMock()
        mock_hist_sort.limit.return_value = mock_hist_cursor
        mock_hist_find.sort.return_value = mock_hist_sort
        
        # Mock adv cursor
        mock_adv_cursor = AsyncMock()
        mock_adv_cursor.to_list.return_value = [
            {"_id": "test_adv_1", "location": "Mangalore-Coast", "severity": "HIGH", "hazard": "High Wind", "created_at": "2024-01-01T00:00:00Z"}
        ]
        
        mock_adv_find = MagicMock()
        mock_adv_sort = MagicMock()
        mock_adv_sort.limit.return_value = mock_adv_cursor
        mock_adv_find.sort.return_value = mock_adv_sort
        
        # Assign find methods based on collection name
        def get_collection(name):
            col = MagicMock()
            if name == "historical_readings":
                col.find.return_value = mock_hist_find
            else:
                col.find.return_value = mock_adv_find
            return col
            
        mock_db.__getitem__.side_effect = get_collection
        
        yield mock_db

def test_export_report_fisherman_forbidden():
    token = create_access_token(data={"sub": "test@orca.com", "role": "fisherman"})
    response = client.get(
        "/api/v1/reports/export?location=Mangalore-Coast",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_export_report_researcher_success():
    token = create_access_token(data={"sub": "researcher@orca.com", "role": "researcher"})
    response = client.get(
        "/api/v1/reports/export?location=Mangalore-Coast",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=orca_report_mangalore-coast.csv" in response.headers["content-disposition"]
    
    # Parse CSV content
    content = response.content.decode("utf-8")
    assert "ORCA Marine Report for Mangalore-Coast" in content
    assert "HAZARD ADVISORIES" in content
    assert "HISTORICAL READINGS" in content
    assert "28.5" in content
    assert "High Wind" in content
