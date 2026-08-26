import requests
import json
import time

query = "Is it safe to go fishing near Karwar tomorrow morning and which nearby area should I choose?"
print(f"USER QUERY: {query}")

res = requests.post("http://localhost:8000/api/query", json={"text": query, "session_id": "test_verify_2"})
data = res.json()
query_id = data["query_id"]

while True:
    res = requests.get(f"http://localhost:8000/api/result/{query_id}")
    card = res.json()
    if card.get("status") == "done":
        with open("trace_output.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(card, indent=2))
        print("Done!")
        break
    time.sleep(2)
