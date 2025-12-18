from aiogram_dialog import DialogManager


async def get_broadcast_data(dialog_manager: DialogManager, **kwargs):
    return {
        "lang_code": dialog_manager.dialog_data.get("lang_code", "не выбрано"),
        "content_type": dialog_manager.dialog_data.get("content_type", "неизвестно"),
        "has_text": bool(dialog_manager.dialog_data.get("text")),
        "text": dialog_manager.dialog_data.get("text", ""),
    }
