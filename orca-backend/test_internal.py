import asyncio
import uuid
import logging
from app.api.v1.query import process_query_background, query_results
from app.interface.schemas import StructuredQuery, Location, TimeWindow, TaskType
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)

async def run():
    query_id = str(uuid.uuid4())
    print(f"Running test for query {query_id}")
    
    sq = StructuredQuery(
        original_query="Find fishing zones near Karwar",
        task=TaskType.FISHING_ZONES,
        location=Location(name="Karwar", lat=14.8, lon=74.1, point_of_interest=True),
        time_window=TimeWindow(
            start=datetime.utcnow(),
            end=datetime.utcnow() + timedelta(days=1),
            is_explicit=False
        ),
        parameters={}
    )
    
    from app.interface.schemas import RiskCard
    query_results[query_id] = RiskCard(status="processing", risk_level="low", reasoning="", recommendation="", evidence=[], agent_status=[])
    
    try:
        await process_query_background(query_id, sq, "test_session")
        print("\n\nFINAL RESULT:")
        result = query_results.get(query_id)
        if result:
            with open("test_internal_output.json", "w", encoding="utf-8") as f:
                f.write(result.model_dump_json(indent=2))
            print("Result written to test_internal_output.json")
        else:
            print("No result found in query_results")
    except BaseException as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
