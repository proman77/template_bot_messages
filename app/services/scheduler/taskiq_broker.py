import logging
import sys
import asyncio
from typing import Any

import ormsgpack
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from taskiq import TaskiqEvents, TaskiqScheduler, TaskiqState, TaskiqDepends
from taskiq.abc.serializer import TaskiqSerializer
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_nats import PullBasedJetStreamBroker
from taskiq_redis import RedisScheduleSource, RedisAsyncResultBackend

from app.infrastructure.database.connection.connect_to_pg import get_pg_pool
from config.config import get_config

# Fix for Windows ProactorEventLoop issue with psycopg
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

config = get_config()


class ORMsgPackSerializer(TaskiqSerializer):
    def dumpb(self, message: Any) -> bytes:
        return ormsgpack.packb(message, option=ormsgpack.OPT_SERIALIZE_PYDANTIC)

    def loadb(self, message: bytes) -> Any:
        return ormsgpack.unpackb(message)


redis_url = f"redis://{config.redis.host}:{config.redis.port}/{config.redis.database}"
if config.redis.username and config.redis.password:
    redis_url = f"redis://{config.redis.username}:{config.redis.password}@{config.redis.host}:{config.redis.port}/{config.redis.database}"

broker = PullBasedJetStreamBroker(
    servers=config.nats.servers,
    queue="taskiq_tasks_json",
).with_result_backend(
    RedisAsyncResultBackend(redis_url=redis_url)
)

redis_source = RedisScheduleSource(url=redis_url)

scheduler = TaskiqScheduler(broker, [redis_source, LabelScheduleSource(broker)])


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    logging.basicConfig(level=config.logs.level_name, format=config.logs.format)
    logger = logging.getLogger(__name__)
    logger.info("🚀 WORKER STARTUP EVENT TRIGGERED! Initializing dependencies...")

    state.logger = logger

    # Initialize Bot
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode(config.bot.parse_mode)),
    )
    state.bot = bot
    
    # Initialize DB Pool
    db_pool = await get_pg_pool(
        db_name=config.postgres.name,
        host=config.postgres.host,
        port=config.postgres.port,
        user=config.postgres.user,
        password=config.postgres.password,
    )
    state.db_pool = db_pool
    
    # Register dependencies
    # Note: We can access these in tasks via context or dependency injection if we set up a provider
    # For now, we store them in state. 
    # To use in tasks: 
    # async def my_task(context: Context = TaskiqDepends()):
    #     bot = context.state.bot


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    if hasattr(state, "bot"):
        await state.bot.session.close()
    
    if hasattr(state, "db_pool"):
        await state.db_pool.close()
        
    state.logger.info("Worker stopped")
