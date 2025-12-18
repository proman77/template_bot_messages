# Этап 4: Система Рассылок (Broadcast Engine) — MVP

## 1. Модели Данных (`src/database/models/broadcast.py`) — ✅ ВЫПОЛНЕНО

Созданы следующие компоненты:
- **Enum**: `app/infrastructure/database/models/broadcast_status.py` (статусы кампании, вынесено для предотвращения циклических импортов).
- **Pydantic Models**: `app/infrastructure/database/models/broadcast.py` (DTO для кампаний и сообщений).
- **Table Logic**: `app/infrastructure/database/tables/broadcast.py` (SQL запросы для CRUD).
- **Registration**: Таблица зарегистрирована в `app/infrastructure/database/db.py`.

### SQL Схема для миграции:
Миграция `e79f1139cc83_add_broadcast_tables` успешно применена.

---
## 2. Админка (Aiogram-dialog) — ✅ ВЫПОЛНЕНО
*   **Команда:** Добавлена команда `/broadcast` (только для ADMIN/OWNER).
*   **Диалог:** Создан поток `app/bot/dialogs/flows/broadcast/`.
*   **Выбор языка:** Реализован выбор целевого языка (ru/en/all).
*   **Захват сообщения:** Бот принимает любое сообщение (текст, фото, видео, анимация) и извлекает из него контент и кнопки (`reply_markup`).
*   **Предпросмотр:** Перед запуском админ видит сводку по сообщению.
*   **Сохранение:** При подтверждении кампания создается в БД со статусом `pending`.

---
## 3. Taskiq: Загрузчик (The Loader) — ✅ ВЫПОЛНЕНО
*   **Задача:** `start_broadcast_task(campaign_id)` в `app/services/scheduler/broadcast_tasks.py`.
*   **Логика:**
    1.  Ставит статус `sending`.
    2.  Читает пользователей из БД через `db.users.get_active_users(language)`.
    3.  Для каждого юзера вызывает задачу `send_one_message.kiq()`.
    4.  По завершении ставит статус `completed`.

---
## 4. Taskiq: Рассыльщик (The Sender) — ✅ ВЫПОЛНЕНО
*   **Задача:** `send_one_message(user_id, campaign_id)`.
*   **Логика:**
    1.  Проверяет статус кампании (если `paused` — прерывает).
    2.  Определяет контент (текст, фото, видео и т.д.).
    3.  Отправляет сообщение через `bot.send_...`.
    4.  **Обработка ошибок:**
        *   `TelegramForbiddenError` -> ставит `is_alive = False` пользователю.
        *   `TelegramRetryAfter` -> засыпает и выбрасывает исключение для ретрая Taskiq.

---
## 5. Особенности работы на Windows (Compatibility) — ✅ ВЫПОЛНЕНО
*   **Проблема:** `psycopg` требует `SelectorEventLoop`, в то время как Windows по умолчанию использует `ProactorEventLoop`.
*   **Решение:**
    1.  Создан механизм `win_fix/sitecustomize.py`, который принудительно устанавливает `SelectorEventLoopPolicy` для всех процессов Python.
    2.  Реализовано monkeypatching `asyncio` для предотвращения сброса настроек в дочерних процессах Taskiq.
    3.  **Запуск:** Для корректной работы воркера на Windows создан файл `run_worker.bat`.
*   **Архитектура:** Enums (`BroadcastStatus`, `UserRole`) перенесены в `app/infrastructure/database/models/`, чтобы избежать циклических импортов при загрузке задач воркером.