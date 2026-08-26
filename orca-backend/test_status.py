import requests
import time
import json

base_url = "http://127.0.0.1:8000"

def run_test(scenario, headers, query_text):
    print(f"\n{'='*50}\nTesting: {scenario}\n{'='*50}")
    
    response = requests.post(
        f"{base_url}/api/query",
        json={"text": query_text, "lat": 14.8, "lon": 74.1},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to submit query: {response.status_code} - {response.text}")
        return
        
    query_id = response.json().get("query_id")
    print(f"Query submitted: {query_id}")
    
    # Poll for completion
    while True:
        res = requests.get(f"{base_url}/api/result/{query_id}")
        data = res.json()
        status = data.get("status")
        if status in ["completed", "failed"]:
            break
        time.sleep(1)
        
    if status == "failed":
        print("Query failed.")
        return
        
    result = data.get("result", {})
    evidence = result.get("evidence", {})
    references = evidence.get("references", [])
    
    print("\nEVIDENCE RESULTS:")
    print(f"{'PROVIDER/SOURCE':<30} | {'DATA_STATUS':<15}")
    print("-" * 50)
    for ref in references:
        print(f"{ref.get('source', 'Unknown'):<30} | {ref.get('data_status', 'Unknown'):<15}")

if __name__ == "__main__":
    # Test 1: Success (No failure headers)
    run_test(
        "Normal Execution (Open-Meteo success etc.)", 
        {}, 
        "Find fishing zones near Karwar"
    )
    
    # Test 2: INCOIS failure
    # run_test(
    #     "INCOIS API Timeout", 
    #     {"Failure-Demo": "incois-timeout"}, 
    #     "Find fishing zones near Karwar"
    # )
    
    # Test 3: ISRO failure
    # run_test(
    #     "ISRO API Unavailable", 
    #     {"Failure-Demo": "isro-unavailable"}, 
    #     "Find fishing zones near Karwar"
    # )
    
    # Test 4: Complete failure
    # run_test(
    #     "Complete Provider Failure", 
    #     {"Failure-Demo": "all-fail"}, 
    #     "Find fishing zones near Karwar"
    # )
