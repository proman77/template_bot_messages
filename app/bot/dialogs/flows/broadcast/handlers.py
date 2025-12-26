import logging
from typing import Any

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from app.bot.dialogs.flows.broadcast.states import BroadcastSG
from app.infrastructure.database.db import DB
from app.infrastructure.database.models.broadcast_status import BroadcastStatus

logger = logging.getLogger(__name__)


async def on_language_selected(callback: CallbackQuery, button: Button, manager: DialogManager, lang_code: str):
    manager.dialog_data["lang_code"] = lang_code
    await manager.switch_to(BroadcastSG.INPUT_MESSAGE)


async def on_message_input(message: Message, message_input: Any, manager: DialogManager):
    # Capture message details
    content_type = message.content_type.value
    text = message.text or message.caption
    file_id = None
    
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.animation:
        file_id = message.animation.file_id
    elif message.document:
        file_id = message.document.file_id

    reply_markup = None
    if message.reply_markup:
        reply_markup = message.reply_markup.model_dump(exclude_none=True)

    # Store in dialog_data
    manager.dialog_data.update({
        "content_type": content_type,
        "text": text,
        "file_id": file_id,
        "reply_markup": reply_markup,
    })
    
    await manager.switch_to(BroadcastSG.PREVIEW)


async def on_finish(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: DB = manager.middleware_data.get("db")
    admin_id = callback.from_user.id
    
    # 1. Create campaign
    campaign = await db.broadcast.create_campaign(admin_id=admin_id)
    
    # 2. Add message
    await db.broadcast.add_message(
        campaign_id=campaign.id,
        language_code=manager.dialog_data["lang_code"],
        content_type=manager.dialog_data["content_type"],
        text=manager.dialog_data.get("text"),
        file_id=manager.dialog_data.get("file_id"),
        caption=manager.dialog_data.get("text") if manager.dialog_data.get("file_id") else None,
        reply_markup=manager.dialog_data.get("reply_markup")
    )
    
    # 3. Set to pending (ready for loader)
    from app.infrastructure.database.models.broadcast_status import BroadcastStatus
    await db.broadcast.update_status(campaign.id, BroadcastStatus.PENDING)
    
    # 4. Initialize Redis keys immediately to avoid "unknown" status in UI
    redis = manager.middleware_data.get("_cache_pool")
    if redis:
        await redis.set(f"broadcast:{campaign.id}:status", BroadcastStatus.PENDING)
        await redis.set(f"broadcast:{campaign.id}:sent", 0)
        await redis.set(f"broadcast:{campaign.id}:fail", 0)
        await redis.set(f"broadcast:{campaign.id}:total", 0)
        logger.info(f"[BROADCAST] Initialized Redis keys for campaign {campaign.id}")

    # 5. Trigger Taskiq Loader (delayed to ensure DB commit)
    import asyncio
    from app.services.scheduler.broadcast_tasks import start_broadcast_task
    
    async def _kick_broadcast(c_id: int):
        try:
            await asyncio.sleep(1)  # Wait for DB transaction to commit
            kiq_result = await start_broadcast_task.kiq(campaign_id=c_id)
            logger.info(f"[BROADCAST] Taskiq loader triggered for campaign {c_id}. Task ID: {kiq_result.task_id}")
        except Exception as e:
            logger.error(f"[BROADCAST] Failed to trigger Taskiq loader for campaign {c_id}: {e}")
        
    asyncio.create_task(_kick_broadcast(campaign.id))
    
    manager.dialog_data["campaign_id"] = campaign.id
    await callback.answer("Рассылка запущена!")
    await manager.switch_to(BroadcastSG.MONITORING)


async def on_pause(callback: CallbackQuery, button: Button, manager: DialogManager):
    campaign_id = manager.dialog_data.get("campaign_id")
    redis = manager.middleware_data.get("_cache_pool")
    if campaign_id and redis:
        await redis.set(f"broadcast:{campaign_id}:status", BroadcastStatus.PAUSED)
        await callback.answer("Рассылка приостановлена")


async def on_resume(callback: CallbackQuery, button: Button, manager: DialogManager):
    campaign_id = manager.dialog_data.get("campaign_id")
    redis = manager.middleware_data.get("_cache_pool")
    if campaign_id and redis:
        await redis.set(f"broadcast:{campaign_id}:status", BroadcastStatus.SENDING)
        await callback.answer("Рассылка возобновлена")


async def on_stop(callback: CallbackQuery, button: Button, manager: DialogManager):
    campaign_id = manager.dialog_data.get("campaign_id")
    redis = manager.middleware_data.get("_cache_pool")
    db: DB = manager.middleware_data.get("db")
    
    if campaign_id and redis:
        await redis.set(f"broadcast:{campaign_id}:status", "stopped")
        if db:
            await db.broadcast.update_status(campaign_id, BroadcastStatus.CANCELLED)
        await callback.answer("Рассылка остановлена")
        await manager.done()
