from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Column, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialogs.flows.broadcast.getters import get_broadcast_data, get_monitoring_data
from app.bot.dialogs.flows.broadcast.handlers import (
    on_finish,
    on_language_selected,
    on_message_input,
    on_pause,
    on_resume,
    on_stop,
)
from app.bot.dialogs.flows.broadcast.states import BroadcastSG

broadcast_dialog = Dialog(
    # 1. Select Language
    Window(
        Const("📢 <b>Создание рассылки</b>\n\nВыберите язык аудитории:"),
        Column(
            Button(Const("🇷🇺 Русский"), id="lang_ru", on_click=lambda c, b, m: on_language_selected(c, b, m, "ru")),
            Button(Const("🇺🇸 English"), id="lang_en", on_click=lambda c, b, m: on_language_selected(c, b, m, "en")),
            Button(Const("🌍 Все языки"), id="lang_all", on_click=lambda c, b, m: on_language_selected(c, b, m, "all")),
        ),
        Cancel(Const("❌ Отмена")),
        state=BroadcastSG.SELECT_LANG,
    ),
    # 2. Input Message
    Window(
        Format("Отправьте или перешлите сообщение для рассылки (язык: {lang_code})"),
        MessageInput(on_message_input),
        SwitchTo(Const("⬅️ Назад"), id="back", state=BroadcastSG.SELECT_LANG),
        state=BroadcastSG.INPUT_MESSAGE,
        getter=get_broadcast_data,
    ),
    # 3. Preview
    Window(
        Const("👀 <b>Предпросмотр</b>\n"),
        Format("Язык: {lang_code}"),
        Format("Тип контента: {content_type}"),
        Format("\nТекст:\n{text}", when="has_text"),
        Column(
            Button(Const("✅ Запустить рассылку"), id="finish", on_click=on_finish),
            SwitchTo(Const("🔄 Изменить сообщение"), id="retry", state=BroadcastSG.INPUT_MESSAGE),
            Cancel(Const("❌ Отмена")),
        ),
        state=BroadcastSG.PREVIEW,
        getter=get_broadcast_data,
    ),
    # 4. Monitoring
    Window(
        Const("📊 <b>Статус рассылки</b>\n"),
        Format("Статус: {status}"),
        Format("Прогресс: {bar} {progress}%"),
        Format("📤 Отправлено: {sent}"),
        Format("❌ Ошибок: {fail}"),
        Format("👥 Всего: {total}"),
        Column(
            Button(Const("⏸ Пауза"), id="pause", on_click=on_pause, when="is_sending"),
            Button(Const("▶️ Продолжить"), id="resume", on_click=on_resume, when="is_paused"),
            Button(Const("⏹ Остановить"), id="stop", on_click=on_stop, when=~F["is_completed"]),
            Button(Const("🔄 Обновить"), id="refresh"), # Default behavior is just to refresh the window
            Cancel(Const("✅ Завершить"), when="is_completed"),
        ),
        state=BroadcastSG.MONITORING,
        getter=get_monitoring_data,
    ),
)
