import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_sources():
    response = client.get("/api/v1/health/sources")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    
    # We should have at least the mock ones responding
    # Even if they timeout, they should return in the list
    names = [s["name"] for s in data["sources"]]
    assert "OpenMeteo Weather" in names
    assert "IMD" in names
