import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from taskiq import TaskiqDepends

from app.infrastructure.database.models.broadcast_status import BroadcastStatus
from app.infrastructure.database.db import DB
from app.services.scheduler.dependencies import get_bot, get_db_connection, get_redis
from app.services.scheduler.taskiq_broker import broker

logger = logging.getLogger(__name__)


@broker.task
async def send_one_message(
    user_id: int,
    campaign_id: int,
    bot: Bot = TaskiqDepends(get_bot),
    db_conn = TaskiqDepends(get_db_connection),
    redis = TaskiqDepends(get_redis),
):
    logger.info(f"[SENDER] Task started for user {user_id}, campaign {campaign_id}")
    from app.infrastructure.database.db import DB
    from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
    
    async with db_conn as raw_connection:
        connection = PsycopgConnection(raw_connection)
        db = DB(connection)
        
        # 1. Check if campaign is still active (using Redis for speed)
        while True:
            status = await redis.get(f"broadcast:{campaign_id}:status")
            if status:
                status = status.decode()
                if status == BroadcastStatus.PAUSED:
                    logger.info(f"[SENDER] Campaign {campaign_id} is PAUSED, waiting...")
                    # If paused, wait and check again
                    await asyncio.sleep(5)
                    continue
                if status in [BroadcastStatus.CANCELLED, "stopped"]:
                    logger.info(f"[SENDER] Campaign {campaign_id} is {status}, stopping task.")
                    return
            break
        
        # Fallback to DB if not in Redis or for extra safety
        campaign = await db.broadcast.get_campaign(campaign_id)
        if not campaign or campaign.status == BroadcastStatus.PAUSED:
            return

        # 2. Get messages for this campaign
        messages = await db.broadcast.get_campaign_messages(campaign_id)
        if not messages:
            return

        # 3. Get user to check language
        user = await db.users.get_user(user_id=user_id)
        if not user:
            logger.warning(f"[SENDER] User {user_id} not found in DB. Skipping.")
            return

        # 4. Find appropriate message
        msg = next((m for m in messages if m.language_code == user.language), None)
        if not msg:
            msg = next((m for m in messages if m.language_code == "all"), None)

        if not msg:
            logger.warning(f"[SENDER] No suitable message found for user {user_id} (lang: {user.language}). Skipping.")
            return

        # 5. Send message based on content type
        try:
            if msg.content_type == "text":
                await bot.send_message(
                    chat_id=user_id,
                    text=msg.text,
                    reply_markup=msg.reply_markup,
                )
            elif msg.content_type == "photo":
                await bot.send_photo(
                    chat_id=user_id,
                    photo=msg.file_id,
                    caption=msg.caption,
                    reply_markup=msg.reply_markup,
                )
            elif msg.content_type == "video":
                await bot.send_video(
                    chat_id=user_id,
                    video=msg.file_id,
                    caption=msg.caption,
                    reply_markup=msg.reply_markup,
                )
            elif msg.content_type == "animation":
                await bot.send_animation(
                    chat_id=user_id,
                    animation=msg.file_id,
                    caption=msg.caption,
                    reply_markup=msg.reply_markup,
                )
            elif msg.content_type == "document":
                await bot.send_document(
                    chat_id=user_id,
                    document=msg.file_id,
                    caption=msg.caption,
                    reply_markup=msg.reply_markup,
                )
            logger.info(f"Successfully sent broadcast message to user {user_id}")
            await redis.incr(f"broadcast:{campaign_id}:sent")
        except TelegramForbiddenError:
            logger.info(f"User {user_id} blocked the bot. Marking as inactive.")
            await db.users.update_alive_status(user_id=user_id, is_alive=False)
            await redis.incr(f"broadcast:{campaign_id}:fail")
        except TelegramRetryAfter as e:
            logger.warning(f"Rate limit hit. Sleeping for {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
            # Taskiq will retry this task if configured, or we can manually re-kiq
            raise e
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {e}")
            await redis.incr(f"broadcast:{campaign_id}:fail")


@broker.task
async def start_broadcast_task(
    campaign_id: int,
    db_conn = TaskiqDepends(get_db_connection),
    redis = TaskiqDepends(get_redis),
):
    from app.infrastructure.database.db import DB
    from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
    
    async with db_conn as raw_connection:
        connection = PsycopgConnection(raw_connection)
        db = DB(connection)
        
        logger.info(f"[BROADCAST] Starting broadcast task for campaign {campaign_id}")
        
        # 1. Update status to sending
        await db.broadcast.update_status(campaign_id, BroadcastStatus.SENDING)
        logger.info(f"[BROADCAST] Campaign {campaign_id} status updated to SENDING")
        
        # Initialize Redis counters and status
        await redis.set(f"broadcast:{campaign_id}:status", BroadcastStatus.SENDING)
        await redis.set(f"broadcast:{campaign_id}:sent", 0)
        await redis.set(f"broadcast:{campaign_id}:fail", 0)

        # 2. Get campaign and messages
        campaign = await db.broadcast.get_campaign(campaign_id)
        logger.info(f"[BROADCAST] Campaign {campaign_id} retrieved: {campaign}")
        
        messages = await db.broadcast.get_campaign_messages(campaign_id)
        logger.info(f"[BROADCAST] Found {len(messages) if messages else 0} messages for campaign {campaign_id}")
        
        if not messages:
            logger.error(f"No messages found for campaign {campaign_id}")
            await db.broadcast.update_status(campaign_id, BroadcastStatus.CANCELLED)
            return

        # 3. Determine target language (from first message for simplicity in MVP)
        target_lang = messages[0].language_code
        logger.info(f"[BROADCAST] Target language for campaign {campaign_id}: {target_lang}")

        # 4. Fetch target users
        user_ids = await db.users.get_active_users(language=target_lang)
        total_users = len(user_ids)
        await redis.set(f"broadcast:{campaign_id}:total", total_users)
        
        logger.info(f"[BROADCAST] Starting broadcast for campaign {campaign_id} to {total_users} users: {user_ids}")

        # 5. Dispatch individual send tasks
        for user_id in user_ids:
            logger.info(f"[BROADCAST] Dispatching send_one_message for user {user_id}, campaign {campaign_id}")
            task = await send_one_message.kiq(user_id, campaign_id)
            logger.info(f"[BROADCAST] Task dispatched: {task.task_id}")

        # 6. Mark loader as finished
        await db.broadcast.update_status(campaign_id, BroadcastStatus.COMPLETED)
        await redis.set(f"broadcast:{campaign_id}:status", BroadcastStatus.COMPLETED)
        logger.info(f"Broadcast loader finished for campaign {campaign_id}")
