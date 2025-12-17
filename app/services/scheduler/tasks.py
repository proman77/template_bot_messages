import logging
import time

from aiogram import Bot
from taskiq import TaskiqDepends
from app.services.scheduler.taskiq_broker import broker
from app.services.scheduler.dependencies import get_bot

logger = logging.getLogger(__name__)

@broker.task
async def simple_task():
    print()
    print("Это простая задача без расписания")
    print()


@broker.task(task_name="periodic_task", schedule=[{"cron": "* * * * *"}])
async def periodic_task():
    print()
    print(
        f"{time.strftime('%H:%M:%S', time.localtime(time.time()))}: Это периодическая задача, выполняющаяся раз в минуту"
    )
    print()


@broker.task
async def dynamic_periodic_task():
    print()
    print(
        f"{time.strftime('%H:%M:%S', time.localtime(time.time()))}: Это динамически запланированная периодическая задача"
    )
    print()


@broker.task
async def scheduled_task():
    print()
    print(
        f"{time.strftime('%H:%M:%S', time.localtime(time.time()))}: Это запланированная разовая задача"
    )
    print()

@broker.task
async def test_di_task(bot: Bot = TaskiqDepends(get_bot)) -> str:
    """
    Test task to verify Dependency Injection.
    """
    try:
        me = await bot.get_me()
        logger.info(f"SUCCESS: Accessed Bot. ID: {me.id}, Username: {me.username}")
        return f"SUCCESS: Accessed Bot. ID: {me.id}, Username: {me.username}"
    except Exception as e:
        logger.error(f"FAILURE: {str(e)}", exc_info=True)
        return f"FAILURE: {str(e)}"
