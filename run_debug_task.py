import asyncio
import sys
import os

# Add win_fix to PYTHONPATH for consistency
sys.path.insert(0, os.path.join(os.getcwd(), "win_fix"))

from app.services.scheduler.tasks import test_di_task
from app.services.scheduler.taskiq_broker import broker

async def main():
    print("Starting broker...")
    await broker.startup()
    print("Sending test task...")
    task = await test_di_task.kiq()
    print(f"Task sent: {task.task_id}")
    try:
        print("Waiting for result (10s)...")
        result = await task.wait_result(timeout=10)
        print(f"Result: {result.return_value}")
    except Exception as e:
        print(f"Error waiting for result: {e}")
    finally:
        await broker.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
