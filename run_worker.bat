@echo off
set PYTHONPATH=%CD%\win_fix;%PYTHONPATH%
echo Starting Taskiq worker with Windows SelectorEventLoop fix...
python -m taskiq worker app.services.scheduler.taskiq_broker:broker app.services.scheduler.tasks --workers 1
