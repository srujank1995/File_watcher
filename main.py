"""
main.py — Entry point for ZIP Watcher System.
Run this script to start the watcher + scheduler.
Stop with Ctrl+C.
"""

import time
import logging
import os
import sys
from datetime import datetime

from config import WATCH_DIR, LOG_FILE, ACTIVE_DAYS, SCHEDULE
from watcher import start_watcher, stop_watcher
from scheduler import build_scheduler

# ─────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def print_banner():
    day_names = {1:"Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday", 5:"Saturday"}
    logger.info("=" * 60)
    logger.info("  ZIP WATCHER — Automated SD-Task Monitor")
    logger.info("=" * 60)
    logger.info(f"  Watch Directory : {WATCH_DIR}")
    logger.info("  Active Schedule :")
    for wd, cfg in SCHEDULE.items():
        logger.info(f"    {day_names[wd]:<12} → Deadline {cfg['hour']:02d}:{cfg['minute']:02d} CST")
    logger.info("=" * 60)


def main():
    print_banner()

    # Start file watcher
    observer = start_watcher(WATCH_DIR)

    # Start APScheduler
    scheduler = build_scheduler()
    scheduler.start()
    logger.info("⏰ Scheduler started. All jobs registered.")
    logger.info("🟢 System running. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(30)   # Heartbeat — keeps process alive
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutdown requested.")
    finally:
        stop_watcher(observer)
        scheduler.shutdown(wait=False)
        logger.info("✅ ZIP Watcher stopped cleanly.")


if __name__ == "__main__":
    main()
