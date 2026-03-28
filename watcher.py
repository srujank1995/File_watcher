"""
watcher.py — Monitors watch directory for new ZIP files using watchdog.
Sets task_done=True and logs events on successful ZIP detection.
"""

import os
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mailer import send_success_mail
import state

logger = logging.getLogger(__name__)


class ZipHandler(FileSystemEventHandler):
    """Handles file system events in the watch directory."""

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        # Only process .zip files
        if not filename.lower().endswith(".zip"):
            logger.debug(f"Ignored non-ZIP file: {filename}")
            return

        detected_at = datetime.now()
        logger.info(f"📦 ZIP detected: {filename} at {detected_at.strftime('%H:%M:%S')}")

        # Record in state
        state.task_done = True
        state.daily_events.append({
            "filename": filename,
            "time": detected_at.strftime("%I:%M:%S %p CST")
        })

        # Send success email
        send_success_mail(filename, detected_at)


def start_watcher(watch_dir: str):
    """Start the watchdog observer on the given directory."""
    os.makedirs(watch_dir, exist_ok=True)
    event_handler = ZipHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    logger.info(f"👁️  Watcher started on: {watch_dir}")
    return observer


def stop_watcher(observer):
    """Gracefully stop the observer."""
    observer.stop()
    observer.join()
    logger.info("🛑 Watcher stopped.")
