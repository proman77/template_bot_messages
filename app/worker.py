import sys
import logging
from app.services.scheduler.taskiq_broker import broker

# This file serves as an entry point for the worker process.
# It imports the configured broker.
#
# Usage:
# taskiq worker app.worker:broker

if __name__ == "__main__":
    # Allow running the worker directly via python
    try:
        from taskiq.cli.worker.run import run_worker
        from taskiq.cli.worker.args import WorkerArgs
        
        # We need to construct args. This is a bit internal, but helpful for debugging.
        # Alternatively, just print instructions.
        print("Starting worker process...")
        print("For production, use: taskiq worker app.worker:broker")
        
        # Attempt to run programmatically (experimental)
        # run_worker(WorkerArgs(broker="app.worker:broker", modules=[]))
        # The above API might vary by version. 
        
    except ImportError:
        pass
