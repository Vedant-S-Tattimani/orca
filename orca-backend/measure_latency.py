import time
import requests

def run_test():
    url = "http://localhost:8000/api/query"
    payload = {
        "text": "Is it safe to go fishing near Karwar tomorrow morning and which nearby area should I choose?",
        "context": {
            "latitude": 14.8185,
            "longitude": 74.1416
        }
    }
    
    # Send the query
    start_time = time.time()
    response = requests.post(url, json=payload)
    response.raise_for_status()
    query_id = response.json().get("query_id")
    print(f"Started query: {query_id}")
    
    # Poll until done
    while True:
        status_resp = requests.get(f"http://localhost:8000/api/result/{query_id}")
        data = status_resp.json()
        if data.get("status") in ["done", "error"]:
            break
        time.sleep(0.1)
        
    end_time = time.time()
    latency = end_time - start_time
    
    print(f"End-to-End Latency: {latency:.2f} seconds")
    print("Status:", data.get("status"))
    print("Agent Statuses:")
    for ag in data.get("agent_status", []):
        print(f"  - {ag['agent_name']}: {ag['status']}")

if __name__ == "__main__":
    run_test()
