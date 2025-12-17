import sys
import os
import asyncio
import logging

# Ensure we import from local directory, not site-packages
sys.path.insert(0, os.getcwd())

# Re-export broker so 'app.worker:broker' still works if needed
from app.services.scheduler.taskiq_broker import broker
print(f"DEBUG: Broker ID in worker.py: {id(broker)}")

if __name__ == "__main__":
    # Fix for Windows ProactorEventLoop issue with psycopg
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        from taskiq.cli.worker.run import run_worker
        from taskiq.cli.worker.args import WorkerArgs
        
        # Force import of tasks to ensure they are registered with the broker
        import app.services.scheduler.tasks
        
        print("🚀 Starting Worker with Windows compatibility fix and workers=1...")
        
        # Run the worker programmatically with correct arguments
        # Pass the broker import string to avoid pickling issues on Windows
        args = WorkerArgs(
            broker="app.worker:broker", 
            modules=["app.services.scheduler.tasks"],
            workers=1,
        )
        run_worker(args)
        
    except ImportError as e:
        print(f"❌ Error: Could not import taskiq or modules. Error: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Error starting worker: {e}")
