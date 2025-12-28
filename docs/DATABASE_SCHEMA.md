# Схема Базы Данных

В данном документе приведено детальное описание таблиц базы данных PostgreSQL, используемых в проекте.

---

## 1. Таблица `users`
Хранит информацию о пользователях бота.

| Поле | Тип данных | Описание |
| :--- | :--- | :--- |
| **id** | SERIAL | Внутренний первичный ключ. |
| **user_id** | BIGINT | Уникальный ID пользователя в Telegram. |
| **username** | VARCHAR | Никнейм пользователя (@username). |
| **full_name** | VARCHAR | Полное имя пользователя. |
| **language** | VARCHAR(10) | Язык интерфейса (например, 'ru', 'en'). |
| **role** | VARCHAR(30) | Роль пользователя (user, admin, owner). |
| **is_alive** | BOOLEAN | Статус активности (True, если бот не заблокирован). |
| **banned** | BOOLEAN | Флаг блокировки пользователя в системе. |
| **created_at** | TIMESTAMPTZ | Дата и время регистрации. |
| **updated_at** | TIMESTAMPTZ | Дата и время последнего обновления профиля. |
| **tz_region** | VARCHAR(50) | Регион часового пояса. |
| **tz_offset** | VARCHAR(10) | Смещение часового пояса. |
| **longitude** | REAL | Долгота (геопозиция). |
| **latitude** | REAL | Широта (геопозиция). |

---

## 2. Таблица `broadcast_campaigns`
Хранит информацию о созданных рассылках.

| Поле | Тип данных | Описание |
| :--- | :--- | :--- |
| **id** | SERIAL | Первичный ключ кампании. |
| **admin_id** | BIGINT | ID администратора, создавшего рассылку. |
| **status** | VARCHAR(20) | Статус рассылки (`created`, `sending`, `completed`, `paused`). |
| **created_at** | TIMESTAMPTZ | Дата создания кампании. |
| **updated_at** | TIMESTAMPTZ | Дата последнего изменения статуса. |
| **scheduled_at** | TIMESTAMPTZ | Запланированное время старта (опционально). |

---

## 3. Таблица `broadcast_messages`
Хранит контент сообщений для каждой кампании (с поддержкой мультиязычности).

| Поле | Тип данных | Описание |
| :--- | :--- | :--- |
| **id** | SERIAL | Первичный ключ сообщения. |
| **campaign_id** | INTEGER | Ссылка на кампанию (`broadcast_campaigns.id`). |
| **language_code** | VARCHAR(10) | Язык сообщения или `all`. |
| **content_type** | VARCHAR(20) | Тип контента (`text`, `photo`, `video`, `animation` и др.). |
| **file_id** | TEXT | ID файла в Telegram (для медиа). |
| **text** | TEXT | Текст сообщения. |
| **caption** | TEXT | Подпись к медиафайлу. |
| **reply_markup** | JSONB | Инлайн-клавиатура в формате JSON. |

---

## Связи (Relations)
- `broadcast_messages.campaign_id` -> `broadcast_campaigns.id` (ON DELETE CASCADE)
