import asyncio
import sys
import os

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from taskiq.cli.worker.run import run_worker
from taskiq.cli.worker.args import parse_args

if __name__ == "__main__":
    args = parse_args([
        "app.services.scheduler.taskiq_broker:broker", 
        "--workers", "1"
    ])
    run_worker(args)
