import logging
logger = logging.getLogger(__name__)
logger.warning("DEBUG: Loading tasks module...")
from aiogram import Bot
from taskiq import TaskiqDepends
from app.services.scheduler.taskiq_broker import broker
logger.warning(f"DEBUG: Broker ID in tasks.py: {id(broker)}")
from app.services.scheduler.dependencies import get_bot

@broker.task
async def simple_task():
    print("Simple task executed")

print("Defining test_di_task_v2...")
@broker.task
async def test_di_task_v2(bot: Bot = TaskiqDepends(get_bot)) -> str:
    """
    Test task to verify Dependency Injection.
    It tries to access the Bot instance via TaskiqDepends.
    """
    logger.info("DEBUG: Executing test_di_task_v2 inside worker!")
    try:
        logger.info(f"DEBUG: Bot instance injected: {bot}")
        
        logger.info("DEBUG: Calling get_me()...")
        me = await bot.get_me()
        logger.info(f"DEBUG: get_me() success: {me.username}")
        
        return f"SUCCESS: Accessed Bot. ID: {me.id}, Username: {me.username}"
    except Exception as e:
        logger.error(f"DEBUG: Task FAILED with error: {e}", exc_info=True)
        return f"FAILURE: {str(e)}"
