import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update, User

from app.infrastructure.database.db import DB
from app.infrastructure.database.models.user import UserModel
from app.bot.enums.roles import UserRole
from config.config import get_config

logger = logging.getLogger(__name__)


class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")

        if user is None:
            return await handler(event, data)

        db: DB = data.get("db")

        if db is None:
            logger.error("Database object is not provided in middleware data.")
            raise RuntimeError("Missing `db` in middleware context.")

        config = get_config()
        role = UserRole.ADMIN if user.id in config.bot.admins else UserRole.USER

        user_row: UserModel = await db.users.upsert_user(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            language=user.language_code or config.i18n.default_locale,
            role=role,
        )

        data.update(user_row=user_row)

        return await handler(event, data)
