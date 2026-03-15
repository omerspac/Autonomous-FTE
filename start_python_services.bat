@echo off
REM Start Python Watchers and Orchestrator
start /B python AI_Employee/watchers/gmail_watcher.py
start /B python AI_Employee/watchers/whatsapp_watcher.py
start /B python AI_Employee/watchers/filesystem_watcher.py
start /B python run_silver.py
echo Python services started in background.
