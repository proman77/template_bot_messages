import asyncio
import logging
import sys

from app.services.scheduler.taskiq_broker import broker
from app.services.scheduler.tasks import test_di_task
from app.infrastructure.database.connection.connect_to_pg import get_pg_pool
from config.config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_connections():
    config = get_config()
    
    logger.info("--- Checking Database Connection ---")
    try:
        pool = await get_pg_pool(
            db_name=config.postgres.name,
            host=config.postgres.host,
            port=config.postgres.port,
            user=config.postgres.user,
            password=config.postgres.password,
        )
        async with pool.connection() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Database connection successful")
        await pool.close()
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

    logger.info("--- Checking NATS Connection ---")
    try:
        # Broker startup checks NATS
        await broker.startup()
        logger.info("✅ NATS connection successful")
        await broker.shutdown()
    except Exception as e:
        logger.error(f"❌ NATS connection failed: {e}")
        return False
        
    return True

async def run_integration_test():
    if not await check_connections():
        logger.error("Skipping integration test due to connection failures.")
        return

    logger.info("--- Starting Integration Test ---")
    
    # Ensure broker is started (as a client)
    await broker.startup()
    
    try:
        logger.info("Sending task 'test_di_task'...")
        # Send the task
        task = await test_di_task.kiq()
        logger.info(f"Task sent. ID: {task.task_id}")
        
        logger.info("Waiting for result...")
        # Wait for result (timeout 10s)
        result = await task.wait_result(timeout=10)
        
        logger.info(f"Result received: {result.return_value}")
        
        if "SUCCESS" in str(result.return_value):
            logger.info("✅ INTEGRATION TEST PASSED!")
        else:
            logger.error("❌ INTEGRATION TEST FAILED!")
            
    except Exception as e:
        logger.error(f"❌ Error during test: {e}")
    finally:
        await broker.shutdown()

if __name__ == "__main__":
    asyncio.run(run_integration_test())
