from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from taskiq import TaskiqDepends, Context

from config.config import get_config
from app.infrastructure.database.connection.connect_to_pg import get_pg_pool

# Global instances to reuse within the process
_bot_instance = None
_db_pool_instance = None

def get_bot(context: Context = TaskiqDepends()) -> Bot:
    if hasattr(context.state, "bot"):
        return context.state.bot
    
    global _bot_instance
    if _bot_instance is None:
        config = get_config()
        _bot_instance = Bot(
            token=config.bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode(config.bot.parse_mode)),
        )
    return _bot_instance

async def get_db_pool(context: Context = TaskiqDepends()):
    if hasattr(context.state, "db_pool"):
        return context.state.db_pool
        
    global _db_pool_instance
    if _db_pool_instance is None:
        config = get_config()
        _db_pool_instance = await get_pg_pool(
            db_name=config.postgres.name,
            host=config.postgres.host,
            port=config.postgres.port,
            user=config.postgres.user,
            password=config.postgres.password,
        )
    return _db_pool_instance

async def get_db_connection(context: Context = TaskiqDepends()):
    """
    Get a database connection for Taskiq tasks.
    Returns a connection context manager.
    """
    # Get pool from context state
    if hasattr(context.state, "db_pool"):
        db_pool = context.state.db_pool
    else:
        db_pool = await get_db_pool(context)
    
    return db_pool.connection()

_redis_instance = None

async def get_redis(context: Context = TaskiqDepends()):
    if hasattr(context.state, "redis"):
        return context.state.redis
        
    global _redis_instance
    if _redis_instance is None:
        from app.infrastructure.cache.connect_to_redis import get_redis_pool
        config = get_config()
        _redis_instance = await get_redis_pool(
            db=config.redis.database,
            host=config.redis.host,
            port=config.redis.port,
            username=config.redis.username,
            password=config.redis.password,
        )
    return _redis_instance
