"""
state.py — Shared mutable state across modules.
Avoids circular imports between watcher and scheduler.
"""

task_done: bool = False          # True once a ZIP is detected today
daily_events: list = []          # List of {filename, time} dicts for summary
