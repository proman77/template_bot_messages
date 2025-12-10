from aiogram import Router, F
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import ChatMemberUpdated

from app.infrastructure.database.db import DB

chat_member_router = Router()


@chat_member_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated, db: DB):
    await db.users.update_alive_status(user_id=event.from_user.id, is_alive=False)


@chat_member_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_unblocked_bot(event: ChatMemberUpdated, db: DB):
    await db.users.update_alive_status(user_id=event.from_user.id, is_alive=True)
