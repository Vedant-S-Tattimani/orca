#!/usr/bin/env python3
"""
Test script for the ORCA API endpoint
"""
import asyncio
import sys
import json
from datetime import datetime, timedelta

# Add the orca-backend directory to the path
sys.path.insert(0, '/c/Users/Lenovo/claudetest/orca-backend')

async def test_api_endpoint():
    """Test the API endpoint directly"""
    try:
        # Import the app
        from app.main import app
        from fastapi.testclient import TestClient

        # Create test client
        client = TestClient(app)

        print("Testing ORCA API endpoint...")

        # Test root endpoint
        response = client.get("/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")

        # Test health endpoint
        response = client.get("/health")
        print(f"Health endpoint: {response.status_code} - {response.json()}")

        # Test query endpoint
        query_data = {
            "task": "safety_check",
            "location": {
                "name": "Kollam",
                "latitude": 8.8932,
                "longitude": 76.6141,
                "radius_km": 5.0
            },
            "time_window": {
                "start": datetime.utcnow().replace(hour=5, minute=0, second=0, microsecond=0).isoformat() + "Z",
                "end": (datetime.utcnow() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat() + "Z"
            },
            "original_query": "Is it safe for me to go fishing tomorrow morning near Kollam?",
            "language": "en"
        }

        print("\nSubmitting query...")
        response = client.post("/api/v1/query/", json=query_data)
        print(f"Query submission: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Query ID: {result.get('query_id')}")
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")

            # Get the result
            query_id = result.get('query_id')
            if query_id:
                print(f"\nFetching result for query {query_id}...")
                response = client.get(f"/api/v1/query/{query_id}")
                print(f"Result fetch: {response.status_code}")

                if response.status_code == 200:
                    result_data = response.json()
                    print(f"Result status: {result_data.get('status')}")
                    if result_data.get('status') == 'completed':
                        result_content = result_data.get('result', {})
                        print(f"Overall risk level: {result_content.get('overall_risk_level', 'Unknown')}")
                        print(f"Recommendation: {result_content.get('recommendation', 'No recommendation')[:100]}...")
                    elif result_data.get('status') == 'processing':
                        print("Query is still processing...")
                    else:
                        print(f"Query failed: {result_data.get('error', 'Unknown error')}")
                else:
                    print(f"Error fetching result: {response.text}")
        else:
            print(f"Error submitting query: {response.text}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to test API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_endpoint())
    sys.exit(0 if success else 1)