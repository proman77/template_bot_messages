import asyncio
import sys
import os

# Add win_fix to PYTHONPATH for consistency
sys.path.insert(0, os.path.join(os.getcwd(), "win_fix"))

from app.services.scheduler.broadcast_tasks import start_broadcast_task
from app.services.scheduler.taskiq_broker import broker

async def trigger_manual(campaign_id: int):
    print(f"Initializing broker to trigger campaign {campaign_id}...")
    await broker.startup()
    
    print(f"Triggering start_broadcast_task for campaign {campaign_id}...")
    await start_broadcast_task.kiq(campaign_id=campaign_id)
    
    print("✅ Task sent!")
    await broker.shutdown()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trigger_manual.py <campaign_id>")
        sys.exit(1)
    
    cid = int(sys.argv[1])
    asyncio.run(trigger_manual(cid))
