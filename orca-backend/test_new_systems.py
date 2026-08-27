#!/usr/bin/env python3
"""
Test validation suite for ORCA Marine's upgraded systems:
- PortService
- GeospatialService (geofencing boundaries)
- AISService (vessel tracking registry)
- RoutingService (coastal route wrapping)
- NLU structured parsing & language support
- New API Endpoints (/api/ports, /api/vessels, /api/alerts)
"""
import sys
import os
import json
import asyncio
from datetime import datetime

# Adjust sys.path to include workspace backend root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def run_tests():
    print("=" * 60)
    print("         ORCA MARINE INTELLIGENCE TEST SUITE            ")
    print("=" * 60)
    
    # Initialize DB connection for testing
    from app.db import db_manager
    from app.config import settings
    from app.services.geospatial_service import GeofenceCache
    print(f"Connecting to MongoDB at: {settings.MONGODB_URL} ...")
    await db_manager.connect_db()
    print("Loading geofences into cache...")
    await GeofenceCache.load_from_db()
    
    # 1. Test PortService
    print("\n[TEST 1] Verifying PortService...")
    try:
        from app.services.port_service import PortService
        port_service = PortService()
        ports = await port_service.get_all_ports()
        print(f"  - Total registered ports: {len(ports)}")
        
        # Test search match for Kochi
        kochi_ports = await port_service.search_ports("Kochi")
        print(f"  - Proximity search match for Kochi: {[p['name'] for p in kochi_ports]}")
        assert len(kochi_ports) > 0, "No Kochi port resolved"
        assert "Kochi" in kochi_ports[0]["name"], "Incorrect port name matched"
        print("  [OK] PortService: PASSED")
    except Exception as e:
        print(f"  [FAIL] PortService: FAILED - {e}")
        return False

    # 2. Test GeospatialService (Geofencing)
    print("\n[TEST 2] Verifying GeospatialService...")
    try:
        from app.services.geospatial_service import GeospatialService
        geo_service = GeospatialService()
        
        # Test deep ocean (clear)
        clear_fences = geo_service.check_geofences(15.0, 70.0)
        print(f"  - Location 15N, 70E checks (Clear Ocean): {clear_fences}")
        for f in clear_fences:
            assert f["inside"] is False, f"Should be outside geofence: {f['geofence_name']}"
            
        # Test Navy Zone (Lakshadweep coordinates: 11.2N, 72.8E)
        navy_fences = geo_service.check_geofences(11.2, 72.8)
        print(f"  - Location 11.2N, 72.8E checks (Navy Zone):")
        found_navy = False
        for f in navy_fences:
            print(f"    * {f['geofence_name']}: inside={f['inside']}, type={f['type']}")
            if f["type"] == "RESTRICTED" and f["inside"]:
                found_navy = True
        assert found_navy, "Should have triggered Lakshadweep Restricted Navy Zone alert"
        
        # Test IMBL (Sri Lanka border coordinates: 9.4N, 79.6E)
        border_fences = geo_service.check_geofences(9.4, 79.6)
        print(f"  - Location 9.4N, 79.6E checks (IMBL):")
        found_imbl = False
        for f in border_fences:
            print(f"    * {f['geofence_name']}: distance={f.get('distance_km')}km, status={f.get('status')}")
            if f["type"] == "IMBL" and f["status"] == "CRITICAL":
                found_imbl = True
        assert found_imbl, "Should have triggered Sri Lanka border proximity warning"
        print("  [OK] GeospatialService: PASSED")
    except Exception as e:
        print(f"  [FAIL] GeospatialService: FAILED - {e}")
        return False

    # 3. Test AISService (Vessel Register)
    print("\n[TEST 3] Verifying AISService...")
    try:
        from app.services.ais_service import AISService
        ais_service = AISService()
        vessels = await ais_service.get_all_vessels()
        print(f"  - Simulated vessel telemetry count: {len(vessels)}")
        assert len(vessels) >= 4, "Missing registered AIS vessels"
        
        # Proximity check near Mumbai coordinates (18.9N, 72.8E)
        nearby_ships = await ais_service.find_nearby_vessels(18.9, 72.8, radius_km=50.0)
        print(f"  - Vessels near Mumbai: {[v['name'] for v in nearby_ships]}")
        assert len(nearby_ships) > 0, "No vessels resolved near Mumbai"
        print("  [OK] AISService: PASSED")
    except Exception as e:
        print(f"  [FAIL] AISService: FAILED - {e}")
        return False

    # 4. Test RoutingService (Kanyakumari wrap-around)
    print("\n[TEST 4] Verifying RoutingService...")
    try:
        from app.services.routing_service import RoutingService
        routing = RoutingService()
        
        # Route from Kochi (West coast: 9.9637, 76.2711) to Chennai (East coast: 13.0906, 80.2989)
        # Should wrap south around Kanyakumari (approx 7.8N) instead of going overland
        start_lat, start_lon = 9.9637, 76.2711
        end_lat, end_lon = 13.0906, 80.2989
        
        route_res = routing.calculate_route(start_lat, start_lon, end_lat, end_lon)
        path = route_res["coordinates"]
        print(f"  - Coastal route calculated. Waypoints: {len(path)}")
        assert len(path) >= 3, "Coastal route should include intermediate wrapping waypoints"
        
        # Verify no overland crossing: check that waypoint latitude goes down near Kanyakumari
        has_southern_wrap = any(pt[0] < 8.2 for pt in path)
        print(f"  - Path contains southern wrap around peninsula (latitude < 8.2): {has_southern_wrap}")
        assert has_southern_wrap, "Route crossed overland! Did not wrap south of Cape Comorin (Kanyakumari)"
        print("  [OK] RoutingService: PASSED")
    except Exception as e:
        print(f"  [FAIL] RoutingService: FAILED - {e}")
        return False

    # 5. Test NLU parsing & regional languages
    print("\n[TEST 5] Verifying NLU Processor...")
    try:
        from app.interface.nlu import NLU
        nlu = NLU()
        
        # Test English query geocoding
        q_en = await nlu.parse_query("Is it safe tomorrow in Kandla?")
        print(f"  - Query En: language={q_en.language}, location={q_en.location.name}")
        assert "kandla" in q_en.location.name.lower(), "NLU failed to geocode/extract Kandla"
        
        # Test Hindi query language detection
        q_hi = await nlu.parse_query("क्या कल कांडला में तूफान आने वाला है?")
        print(f"  - Query Hi: language={q_hi.language}, location={q_hi.location.name}")
        assert q_hi.language == "hi", "NLU failed to detect Hindi"
        assert "kandla" in q_hi.location.name.lower(), "NLU failed to extract location in Hindi query"
        print("  [OK] NLU Processor: PASSED")
    except Exception as e:
        print(f"  [FAIL] NLU Processor: FAILED - {e}")
        return False

    # 6. Test FastAPI Web API Client
    print("\n[TEST 6] Verifying Web API Endpoints...")
    try:
        from app.main import app
        import httpx
        
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            # GET /api/ports
            res_ports = await client.get("/api/ports")
            print(f"  - GET /api/ports -> status {res_ports.status_code}, count={len(res_ports.json())}")
            assert res_ports.status_code == 200
            assert len(res_ports.json()) > 0
            
            # GET /api/vessels
            res_vessels = await client.get("/api/vessels")
            print(f"  - GET /api/vessels -> status {res_vessels.status_code}, count={len(res_vessels.json())}")
            assert res_vessels.status_code == 200
            assert len(res_vessels.json()) > 0
            
            # GET /api/alerts
            res_alerts = await client.get("/api/alerts")
            print(f"  - GET /api/alerts -> status {res_alerts.status_code}, alerts={len(res_alerts.json())}")
            assert res_alerts.status_code == 200
            assert len(res_alerts.json()) > 0
            
            # POST /api/query (E2E Process)
            query_payload = {
                "text": "What is the wave height near Kochi?",
                "lat": 9.9,
                "lon": 76.2
            }
            res_query = await client.post("/api/query", json=query_payload)
            assert res_query.status_code == 200
            query_id = res_query.json()["query_id"]
            print(f"  - POST /api/query -> status 200, query_id={query_id}")
            
            # Poll result to check done and verify dev_logs are populated
            print("  - Polling background task processing...")
            is_done = False
            for i in range(15):
                await asyncio.sleep(1)
                res_result = await client.get(f"/api/result/{query_id}")
                card = res_result.json()
                if card["status"] == "done":
                    is_done = True
                    print(f"    * Completed! Risk level: {card['risk_level']}")
                    print(f"    * Logs generated: {len(card['dev_logs'])} steps recorded.")
                    assert len(card["dev_logs"]) > 0, "dev_logs list is empty!"
                    break
            assert is_done, "Background processing timed out"
            print("  [OK] Web API Endpoints: PASSED")
    except Exception as e:
        print(f"  [FAIL] Web API Endpoints: FAILED - {e}")
        return False

    print("\n" + "=" * 60)
    print("         ALL ORCA UPGRADED COMPONENT TESTS PASSED!       ")
    print("=" * 60)
    
    # Close DB connection
    await db_manager.close_db()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
