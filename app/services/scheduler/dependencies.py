from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from taskiq import TaskiqDepends, Context

from config.config import get_config
from app.infrastructure.database.connection.connect_to_pg import get_pg_pool

# Global instances to reuse within the process
_bot_instance = None
_db_pool_instance = None

def get_bot() -> Bot:
    global _bot_instance
    if _bot_instance is None:
        config = get_config()
        _bot_instance = Bot(
            token=config.bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode(config.bot.parse_mode)),
        )
    return _bot_instance

async def get_db_pool():
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
