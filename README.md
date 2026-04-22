# 🚀 ZIP Watcher System — Automated SD-Task Monitor
**Windows | SMTP (Gmail/Outlook) | Python 3.x**

---

## What This Does

| Event | Action |
|---|---|
| ZIP file pasted into watch folder | ✅ Success email sent immediately |
| 30 min before deadline | ⚠️ Warning email — "Do SD-Task now!" |
| 30 min after deadline (no ZIP) | 🚨 High Alert email — "Task NOT performed!" |
| 11:00 PM each active day | 📋 Daily summary email |

### Schedule
| Day | Deadline (CST) |
|---  |---             |
| Tuesday – Friday | 4:15 AM |
| Saturday | 6:00 AM |
| Sunday & Monday | OFF |

---

## Quick Setup (5 Steps)

### 1. Install Python 3.11+
Download from https://python.org — check "Add to PATH" during install.

### 2. Install dependencies
```cmd
cd C:\zip-watcher
pip install -r requirements.txt
```

### 3. Configure .env
Copy `.env.template` → `.env` and fill in SMTP credentials:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password   ← Gmail App Password
```

> **Gmail:** Go to myaccount.google.com → Security → 2-Step Verification → App Passwords → Generate one for "Mail".

> **Outlook:** Use smtp-mail.outlook.com / port 587, and your normal Outlook password (or App Password if MFA is on).

### 4. Edit config.py
```python
WATCH_DIR = r"C:\YourWatchFolder"          # Folder to monitor

ALERT_RECIPIENTS = [
    "you@example.com",
    "manager@example.com",
]
```

### 5. Run it
```cmd
python main.py
```
You'll see live logs in the console and in `logs\activity.log`.

---

## Running as a Windows Service (Always On)

So the script runs even when no one is logged in:

1. Download NSSM from https://nssm.cc/download
2. Extract to `C:\nssm\`
3. Edit `install_service.bat` — update `PYTHON_EXE` and `SCRIPT_PATH`
4. Right-click → **Run as Administrator**

To stop/uninstall the service:
```cmd
net stop ZipWatcher
nssm remove ZipWatcher confirm
```

---

## File Structure
```
zip-watcher/
├── main.py           ← Entry point — run this
├── config.py         ← All settings (paths, schedule, email)
├── watcher.py        ← Watchdog file monitor
├── scheduler.py      ← APScheduler jobs
├── mailer.py         ← All 4 email types
├── state.py          ← Shared flags (task_done, daily_events)
├── .env              ← SMTP credentials (keep secret!)
├── .env.template     ← Template — copy to .env
├── requirements.txt
├── install_service.bat
└── logs/
    └── activity.log
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| No emails received | Check .env credentials, verify App Password is correct |
| Gmail blocks login | Enable 2FA → generate App Password |
| Wrong timezone | Script uses `America/Chicago` (CST/CDT auto-adjusts for DST) |
| ZIP not detected | Ensure file is fully copied before watchdog fires; large files may need a brief delay |
| Service won't start | Check `logs\service_stderr.log` for errors |
"# File_watcher" 


## 🔄 System Flowchart

flowchart TD
A[Start Monitoring Service] --> B{Is Today Active Day?}

B -- No --> Z[No Action (Sunday & Monday)]
B -- Yes --> C[Start Watch Folder Monitoring]

C --> D{ZIP File Detected?}

D -- Yes --> E[Mark Task Done]
E --> F[Send Success Email]
F --> G[Log Event]

D -- No --> H{Time Check}
H --> I[30 Min Before Deadline]
I --> J[Send Warning Email]
H --> K[Deadline Passed + 30 Min]
K --> L{Task Done?}

L -- No --> M[Send High Alert Email]
L -- Yes --> G

G --> N{Is Time 11:00 PM?}

N -- Yes --> O[Send Daily Summary Email]
N -- No --> C

O --> C
