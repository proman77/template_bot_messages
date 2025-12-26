from aiogram_dialog import DialogManager


async def get_broadcast_data(dialog_manager: DialogManager, **kwargs):
    return {
        "lang_code": dialog_manager.dialog_data.get("lang_code", "не выбрано"),
        "content_type": dialog_manager.dialog_data.get("content_type", "неизвестно"),
        "has_text": bool(dialog_manager.dialog_data.get("text")),
        "text": dialog_manager.dialog_data.get("text", ""),
    }


async def get_monitoring_data(dialog_manager: DialogManager, **kwargs):
    campaign_id = dialog_manager.dialog_data.get("campaign_id")
    redis = dialog_manager.middleware_data.get("_cache_pool")
    
    if not campaign_id or not redis:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"[GETTER] Missing data: campaign_id={campaign_id}, redis_exists={bool(redis)}")
        return {
            "total": 0, "sent": 0, "fail": 0, "status": "unknown", 
            "progress": 0, "bar": "░" * 10, "is_sending": False, 
            "is_paused": False, "is_completed": False
        }

    total = await redis.get(f"broadcast:{campaign_id}:total") or 0
    sent = await redis.get(f"broadcast:{campaign_id}:sent") or 0
    fail = await redis.get(f"broadcast:{campaign_id}:fail") or 0
    status = await redis.get(f"broadcast:{campaign_id}:status") or b"unknown"
    
    total = int(total)
    sent = int(sent)
    fail = int(fail)
    status = status.decode()
    
    processed = sent + fail
    progress = (processed / total * 100) if total > 0 else 0
    
    # Simple progress bar
    bar_length = 10
    filled = int(progress / 10)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    return {
        "total": total,
        "sent": sent,
        "fail": fail,
        "status": status,
        "progress": round(progress, 1),
        "bar": bar,
        "is_sending": status == "sending",
        "is_paused": status == "paused",
        "is_completed": status == "completed" or processed >= total and total > 0
    }
