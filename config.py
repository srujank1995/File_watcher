"""
config.py — Central configuration for ZIP Watcher System
Update all values below before running.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# WATCH DIRECTORY
# ─────────────────────────────────────────────
WATCH_DIR = r"D:\Test_watcher"           # Directory to monitor for ZIP files
ARCHIVE_DIR = r"D:\Test_watcher\Archive" # Auto-archive not selected; kept for reference

# ─────────────────────────────────────────────
# EMAIL SETTINGS (loaded from .env)
# ─────────────────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("SMTP_USER", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")

# Who receives the alerts
ALERT_RECIPIENTS = [
    "abc@gmail.com",
    "xyz@gmail.com",

]

# ─────────────────────────────────────────────
# SCHEDULE (all times in CST = UTC-6)
# weekday() → Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
# ─────────────────────────────────────────────
SCHEDULE = {
    1: {"hour": 4,  "minute": 15},  # Tuesday
    2: {"hour": 4,  "minute": 15},  # Wednesday
    3: {"hour": 4,  "minute": 15},  # Thursday
    4: {"hour": 4,  "minute": 15},  # Friday
    5: {"hour": 6,  "minute": 0},   # Saturday
    # 0 = Monday → OFF
    # 6 = Sunday → OFF
}

ACTIVE_DAYS = list(SCHEDULE.keys())   # [1, 2, 3, 4, 5]

# Alert offsets (minutes)
PRE_ALERT_OFFSET_MINUTES  = 30   # warn 30 min BEFORE deadline
POST_ALERT_OFFSET_MINUTES = 30   # high alert 30 min AFTER deadline

# ─────────────────────────────────────────────
# DAILY SUMMARY TIME (CST)
# ─────────────────────────────────────────────
SUMMARY_HOUR   = 23   # 11:00 PM CST each active day
SUMMARY_MINUTE = 0

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
LOG_FILE = r"logs\activity.log"
