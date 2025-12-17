import asyncio
import logging
from nats.js.errors import NotFoundError
from app.infrastructure.storage.nats_connect import connect_to_nats
from config.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_nats():
    config = get_config()
    logger.info("Connecting to NATS...")
    nc, js = await connect_to_nats(servers=config.nats.servers)
    
    streams_to_delete = ["taskiq_jetstream", "taskiq_tasks", "taskiq_tasks_v2", "taskiq_tasks_json"]
    
    for stream in streams_to_delete:
        try:
            logger.info(f"Deleting stream: {stream}...")
            await js.delete_stream(stream)
            logger.info(f"✅ Stream {stream} deleted.")
        except NotFoundError:
            logger.info(f"Stream {stream} not found.")
        except Exception as e:
            logger.warning(f"Error deleting {stream}: {e}")

    await nc.close()

if __name__ == "__main__":
    asyncio.run(reset_nats())
