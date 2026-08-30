import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

def test_routing():
    with TestClient(app) as client:
        # Normal Route (e.g., from deep sea to Sri Lanka border or some far destination)
        # Deep sea point off Kerala
        origin_lat = 9.0
        origin_lon = 75.0
        # Far destination (e.g. Chennai)
        dest_lat = 13.0906
        dest_lon = 80.2989
        
        print("--- NORMAL ROUTE ---")
        res1 = client.post(
            "/api/route",
            json={
                "origin_lat": origin_lat,
                "origin_lon": origin_lon,
                "dest_lat": dest_lat,
                "dest_lon": dest_lon,
                "emergency": False
            }
        )
        assert res1.status_code == 200, res1.text
        data1 = res1.json()
        print("Normal Distance NM:", data1["route_geometry"]["distance_nm"])
        print("Final coordinate:", data1["route_geometry"]["coordinates"][-1])
        
        print("\n--- EMERGENCY ROUTE ---")
        res2 = client.post(
            "/api/route",
            json={
                "origin_lat": origin_lat,
                "origin_lon": origin_lon,
                "dest_lat": dest_lat,
                "dest_lon": dest_lon,
                "emergency": True
            }
        )
        assert res2.status_code == 200, res2.text
        data2 = res2.json()
        print("Emergency Distance NM:", data2["route_geometry"]["distance_nm"])
        final_coord = data2["route_geometry"]["coordinates"][-1]
        print("Final coordinate:", final_coord)
        
        # Verify emergency route ends somewhere much closer than Chennai
        assert data2["route_geometry"]["distance_nm"] < data1["route_geometry"]["distance_nm"]
        assert final_coord[0] != dest_lat or final_coord[1] != dest_lon