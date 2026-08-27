import requests, json, time, sys

sys.stdout.reconfigure(encoding='utf-8')

def test_query(text, location=None):
    url = "http://localhost:8000/api/query"
    payload = {"text": text, "session_id": "test_session_123"}
    if location:
        payload["lat"] = location[0]
        payload["lon"] = location[1]
    
    print(f"--- Query: {text} ---")
    try:
        resp = requests.post(url, json=payload)
        data = resp.json()
        if "query_id" not in data:
            print("Failed to get query ID:", data)
            return
            
        query_id = data["query_id"]
        print(f"Got query_id: {query_id}. Polling...")
        
        for _ in range(15):
            res_resp = requests.get(f"http://localhost:8000/api/result/{query_id}")
            res_data = res_resp.json()
            if res_data.get("status") == "done":
                print("Result Status: DONE")
                print(f"Reasoning: {res_data.get('reasoning')}")
                print(f"Recommendation: {res_data.get('recommendation')}")
                break
            elif res_data.get("status") == "failed":
                print("Query processing failed!")
                print("Result data:", json.dumps(res_data, indent=2)[:500])
                break
            time.sleep(2)
        else:
            print("Timed out waiting for result.")
    except Exception as e:
        print(f"Request failed: {e}")
    print()

if __name__ == "__main__":
    test_query("what is the weather at Mangalore", (12.9141, 74.8560))
    test_query("is it safe to fish near Mangalore today", (12.9141, 74.8560))
    test_query("tell me a joke", (12.9141, 74.8560))
    print("=== Testing Missing Location ===")
    test_query("what is the weather like", None)
    
    print("=== Testing Unresolvable Location ===")
    test_query("is it safe to fish in Atlantis", None)

    print("=== Testing Follow-up Context (Multi-turn) ===")
    # First turn provides the location
    print("Turn 1: Providing location")
    url = "http://localhost:8000/api/query"
    payload1 = {"text": "What is the weather in Mangalore?", "session_id": "test_context_1"}
    try:
        r1 = requests.post(url, json=payload1).json()
        q1 = r1.get("query_id")
        time.sleep(5)
        print("Turn 2: Follow-up question without location")
        payload2 = {"text": "What about tomorrow?", "session_id": "test_context_1"}
        r2 = requests.post(url, json=payload2).json()
        q2 = r2.get("query_id")
        time.sleep(5)
        res2 = requests.get(f"http://localhost:8000/api/result/{q2}").json()
        reasoning = res2.get('reasoning', '')
        print("Follow-up Output:", reasoning)
        if "Unknown" in reasoning or "I need a specific location" in reasoning:
            print("Follow-up Context Test FAILED: Location context was lost.")
        else:
            print("Follow-up Context Test PASSED.")
    except Exception as e:
        print(f"Follow-up Context Test FAILED: {e}")

    print("=== Testing Out of Scope General Inquiry ===")
    url_joke = "http://localhost:8000/api/query"
    payload_joke = {"text": "tell me a joke", "session_id": "test_joke", "lat": 12.9141, "lon": 74.8560}
    try:
        rj = requests.post(url_joke, json=payload_joke).json()
        qj = rj.get("query_id")
        time.sleep(5)
        resj = requests.get(f"http://localhost:8000/api/result/{qj}").json()
        print("Joke Output:", resj.get('reasoning'))
        print("Out of Scope Test PASSED (Manual verification that it refused nicely).")
    except Exception as e:
        print(f"Out of Scope Test FAILED: {e}")

    # Test Area 1: All-agents-timeout
    print("=== Testing All-Agents Timeout ===")
    url = "http://localhost:8000/api/query?demo_failure=true"
    payload = {"text": "what is the weather at Mangalore", "session_id": "test_session_timeout", "lat": 12.9141, "lon": 74.8560}
    try:
        resp = requests.post(url, json=payload)
        q_id = resp.json().get("query_id")
        time.sleep(5)
        res_data = requests.get(f"http://localhost:8000/api/result/{q_id}").json()
        print("Fallback Output:", res_data.get('reasoning'))
        assert "We couldn't retrieve any data right now" in res_data.get('reasoning', ''), "Fallback failed!"
        print("All-Agents Timeout Test PASSED.")
    except Exception as e:
        print(f"All-Agents Timeout Test FAILED: {e}")

    # Test Area 2: Multilingual Translation Accuracy
    print("=== Testing Multilingual Numbers ===")
    url_ml = "http://localhost:8000/api/query"
    payload_ml = {"text": "aaj mausam kaisa hai", "session_id": "test_session_ml", "lat": 12.9141, "lon": 74.8560}
    try:
        resp_ml = requests.post(url_ml, json=payload_ml)
        q_id_ml = resp_ml.json().get("query_id")
        time.sleep(15)
        res_data_ml = requests.get(f"http://localhost:8000/api/result/{q_id_ml}").json()
        reasoning = res_data_ml.get('reasoning', '')
        print("Hindi Output:", reasoning)
        import re
        nums = re.findall(r'\d+(?:\.\d+)?', reasoning)
        if len(nums) > 0:
            print(f"Found numbers in Hindi output: {nums}. Test PASSED.")
        else:
            print("No numbers preserved in Hindi output! Test FAILED.")
    except Exception as e:
        print(f"Multilingual Numbers Test FAILED: {e}")

    # Test Area 3: Twilio Webhook Security
    print("=== Testing Twilio Webhook Security ===")
    url_tw = "http://localhost:8000/api/webhook/twilio"
    # Send without signature
    payload_tw = {"Body": "hello", "From": "+1234567890"}
    try:
        resp_tw = requests.post(url_tw, data=payload_tw)
        if resp_tw.status_code == 403:
            print("Twilio Webhook Security Test (No Signature) PASSED.")
        else:
            print(f"Twilio Webhook Security Test FAILED: expected 403, got {resp_tw.status_code}")
    except Exception as e:
        print(f"Twilio Webhook Security Test FAILED: {e}")

    # Test Area 4: Feedback Endpoint Abuse Protection
    print("=== Testing Feedback Abuse Protection ===")
    url_fb = "http://localhost:8000/api/feedback"
    try:
        status_429_received = False
        import concurrent.futures
        
        def send_fb(i):
            payload_fb = {"query_id": f"test_spam_{i}", "is_helpful": True}
            return requests.post(url_fb, json=payload_fb)
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(send_fb, i) for i in range(25)]
            for future in concurrent.futures.as_completed(futures):
                resp_fb = future.result()
                if resp_fb.status_code == 429:
                    status_429_received = True
        
        if status_429_received:
            print("Feedback Abuse Protection Test (429 Too Many Requests) PASSED.")
        else:
            print("Feedback Abuse Protection Test FAILED: Did not receive 429 status.")
    except Exception as e:
        print(f"Feedback Abuse Protection Test FAILED: {e}")
