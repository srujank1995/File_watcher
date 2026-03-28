"""
scheduler.py — APScheduler jobs for:
  • Pre-deadline warning  (deadline - 30 min)
  • Post-deadline alert   (deadline + 30 min)
  • Daily summary         (11:00 PM CST each active day)
  • Midnight state reset
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from config import SCHEDULE, ACTIVE_DAYS, PRE_ALERT_OFFSET_MINUTES, POST_ALERT_OFFSET_MINUTES, SUMMARY_HOUR, SUMMARY_MINUTE
from mailer import send_warning_mail, send_high_alert_mail, send_daily_summary
import state

logger = logging.getLogger(__name__)

CST = pytz.timezone("America/Chicago")


def _get_deadline_today() -> datetime:
    """Return today's deadline as a timezone-aware datetime in CST."""
    now_cst = datetime.now(CST)
    day_config = SCHEDULE.get(now_cst.weekday())
    if not day_config:
        return None
    return now_cst.replace(hour=day_config["hour"], minute=day_config["minute"], second=0, microsecond=0)


def job_pre_deadline_warning():
    """Triggered 30 min before deadline. Warn only if task is not yet done."""
    deadline = _get_deadline_today()
    if deadline is None:
        return
    if state.task_done:
        logger.info("Pre-deadline check: task already done ✅ — skipping warning.")
        return
    logger.warning("⚠️  Pre-deadline warning triggered. Sending warning email.")
    send_warning_mail(deadline)


def job_post_deadline_alert():
    """Triggered 30 min after deadline. High alert if task was never done."""
    deadline = _get_deadline_today()
    if deadline is None:
        return
    if state.task_done:
        logger.info("Post-deadline check: task was completed ✅ — no alert needed.")
        return
    logger.error("🚨 Post-deadline alert triggered. SD-Task NOT performed!")
    send_high_alert_mail(deadline)


def job_daily_summary():
    """Triggered at SUMMARY_HOUR each active day. Sends recap email."""
    deadline = _get_deadline_today()
    if deadline is None:
        return
    logger.info("📋 Daily summary triggered.")
    send_daily_summary(
        events=list(state.daily_events),
        task_done=state.task_done,
        deadline=deadline
    )


def job_reset_state():
    """Midnight reset — clear flags for the new day."""
    state.task_done = False
    state.daily_events.clear()
    logger.info("🔄 State reset for new day.")


def build_scheduler() -> BackgroundScheduler:
    """
    Build and return a BackgroundScheduler with all jobs registered.
    Days: Tue(1), Wed(2), Thu(3), Fri(4) → 4:15 AM CST
          Sat(5)                          → 6:00 AM CST
    """
    scheduler = BackgroundScheduler(timezone=CST)

    # APScheduler day_of_week: mon=0, tue=1 ... sat=5, sun=6
    # Map Python weekday int → APScheduler abbreviation
    day_map = {1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat"}

    for weekday, cfg in SCHEDULE.items():
        day_abbr  = day_map[weekday]
        dl_hour   = cfg["hour"]
        dl_minute = cfg["minute"]

        # Compute pre/post times
        deadline_dt   = datetime(2000, 1, 1, dl_hour, dl_minute)
        pre_dt        = deadline_dt - timedelta(minutes=PRE_ALERT_OFFSET_MINUTES)
        post_dt       = deadline_dt + timedelta(minutes=POST_ALERT_OFFSET_MINUTES)

        # ── Pre-deadline warning ───────────────────────────────────
        scheduler.add_job(
            job_pre_deadline_warning,
            CronTrigger(day_of_week=day_abbr, hour=pre_dt.hour, minute=pre_dt.minute, timezone=CST),
            id=f"pre_warning_{day_abbr}",
            name=f"Pre-deadline warning ({day_abbr})",
            replace_existing=True,
            misfire_grace_time=120,
        )
        logger.info(f"  Scheduled PRE-WARNING  {day_abbr.upper()} {pre_dt.strftime('%H:%M')} CST")

        # ── Post-deadline high alert ───────────────────────────────
        scheduler.add_job(
            job_post_deadline_alert,
            CronTrigger(day_of_week=day_abbr, hour=post_dt.hour, minute=post_dt.minute, timezone=CST),
            id=f"post_alert_{day_abbr}",
            name=f"Post-deadline alert ({day_abbr})",
            replace_existing=True,
            misfire_grace_time=120,
        )
        logger.info(f"  Scheduled POST-ALERT   {day_abbr.upper()} {post_dt.strftime('%H:%M')} CST")

        # ── Daily summary ──────────────────────────────────────────
        scheduler.add_job(
            job_daily_summary,
            CronTrigger(day_of_week=day_abbr, hour=SUMMARY_HOUR, minute=SUMMARY_MINUTE, timezone=CST),
            id=f"summary_{day_abbr}",
            name=f"Daily summary ({day_abbr})",
            replace_existing=True,
            misfire_grace_time=300,
        )
        logger.info(f"  Scheduled SUMMARY      {day_abbr.upper()} {SUMMARY_HOUR:02d}:{SUMMARY_MINUTE:02d} CST")

    # ── Midnight state reset (every day) ──────────────────────────
    scheduler.add_job(
        job_reset_state,
        CronTrigger(hour=0, minute=0, timezone=CST),
        id="midnight_reset",
        name="Midnight state reset",
        replace_existing=True,
    )
    logger.info("  Scheduled MIDNIGHT RESET  daily at 00:00 CST")

    return scheduler
