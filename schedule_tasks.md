# AI Employee Scheduling Guide

To ensure your AI Employee remains autonomous, you should schedule the provided scripts to run automatically.

## 1. Daily Task Runner
**Script:** `scripts/daily_runner.py`  
**Frequency:** Every night at 11:59 PM.  
**Action:** Processes any remaining items in `Needs_Action` and generates a summary in `Logs/`.

### Windows (PowerShell)
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Path\To\Autonomous-FTE\scripts\daily_runner.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 11:59PM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AI_Employee_Daily_Runner" -Description "Processes daily AI tasks and generates summary."
```

### Linux (Cron)
```bash
59 23 * * * /usr/bin/python3 /path/to/Autonomous-FTE/scripts/daily_runner.py >> /path/to/Autonomous-FTE/AI_Employee/vault/Logs/daily_cron.log 2>&1
```

---

## 2. Weekly Audit & Briefing
**Script:** `scripts/weekly_audit.py`  
**Frequency:** Every Sunday and Monday at 8:00 AM.  
**Action:** 
- **Sunday:** Generates a business audit in `Logs/`.
- **Monday:** Places a CEO Briefing in the `Inbox/`.

### Windows (PowerShell)
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Path\To\Autonomous-FTE\scripts\weekly_audit.py"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday,Monday -At 8:00AM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AI_Employee_Weekly_Audit" -Description "Generates Sunday Audit and Monday CEO Briefing."
```

### Linux (Cron)
```bash
0 8 * * 0,1 /usr/bin/python3 /path/to/Autonomous-FTE/scripts/weekly_audit.py >> /path/to/Autonomous-FTE/AI_Employee/vault/Logs/weekly_cron.log 2>&1
```

## 3. Monday Morning CEO Briefing
**Script:** `scripts/ceo_briefing_generator.py`  
**Frequency:** Every Monday at 7:00 AM.  
**Action:** Compiles financial and task metrics into a comprehensive Markdown report in `Briefings/`.

### Windows (PowerShell)
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Path\To\Autonomous-FTE\scripts\ceo_briefing_generator.py"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7:00AM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AI_Employee_CEO_Briefing" -Description "Generates Monday morning business report."
```

### Linux (Cron)
```bash
0 7 * * 1 /usr/bin/python3 /path/to/Autonomous-FTE/scripts/ceo_briefing_generator.py >> /path/to/Autonomous-FTE/AI_Employee/vault/Logs/briefing_cron.log 2>&1
```

---

## Tips for Reliable Scheduling

1.  **Use Absolute Paths**: Always use full paths (e.g., `C:\Users\Name\...` or `/home/user/...`) in your scheduler commands.
2.  **Environment**: Ensure the Python environment you use has all requirements installed. If using a virtualenv, point to the python executable *inside* the `bin/` or `Scripts/` folder of that environment.
3.  **Logs**: Check the `AI_Employee/vault/Logs/` directory if a task fails to run.
