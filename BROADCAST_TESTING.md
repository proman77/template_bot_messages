# Инструкция по тестированию рассылки

## Запуск системы

1. **Запустить воркер Taskiq:**
   ```bash
   ./run_worker.bat
   ```
   Или вручную:
   ```bash
   export PYTHONPATH="$PWD/win_fix;$PYTHONPATH"
   python -m taskiq worker app.services.scheduler.taskiq_broker:broker app.services.scheduler.tasks --workers 1
   ```

2. **Запустить бота:**
   ```bash
   python main.py
   ```

## Тестирование рассылки через бота

1. Откройте бота в Telegram
2. Отправьте команду `/broadcast` (доступна только для ADMIN/OWNER)
3. Выберите целевой язык (ru/en/all)
4. Отправьте сообщение для рассылки (текст, фото, видео и т.д.)
5. Подтвердите отправку

**Результат:** Сообщение автоматически отправится всем активным пользователям с выбранным языком.

## Проверка логов

- **Логи воркера:** `worker_log.txt`
- **Логи бота:** `bot_log.txt` (если запущен в фоне)

Поиск по логам воркера:
```bash
grep "\[BROADCAST\]" worker_log.txt
grep "Successfully sent broadcast message" worker_log.txt
```

## Ручной запуск рассылки

Если нужно запустить существующую кампанию вручную:
```bash
export PYTHONPATH="$PWD/win_fix;$PYTHONPATH"
python trigger_manual.py <campaign_id>
```

## Проверка статуса кампаний

```bash
export PYTHONPATH="$PWD/win_fix;$PYTHONPATH"
python check_db_status.py
```
