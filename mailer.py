"""
mailer.py — Email sending functions
Handles: Success, Pre-deadline warning, High alert, Daily summary
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_RECIPIENTS

logger = logging.getLogger(__name__)


def _send(subject: str, body_html: str, recipients: list):
    """Internal helper — builds and sends one email via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_USER
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipients, msg.as_string())
        logger.info(f"✅ Email sent | Subject: {subject} | To: {recipients}")
    except Exception as e:
        logger.error(f"❌ Email FAILED | Subject: {subject} | Error: {e}")


# ─────────────────────────────────────────────────────────────
# 1. SUCCESS EMAIL — ZIP was detected in watch directory
# ─────────────────────────────────────────────────────────────
def send_success_mail(filename: str, detected_at: datetime):
    subject = f"✅ [ZIP WATCHER] File Received: {filename}"
    body = f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px;">
        <h2 style="color:#2e7d32;">✅ ZIP File Successfully Received</h2>
        <table style="border-collapse:collapse;width:100%;max-width:500px;">
            <tr><td style="padding:8px;background:#f5f5f5;font-weight:bold;">File Name</td>
                <td style="padding:8px;">{filename}</td></tr>
            <tr><td style="padding:8px;background:#f5f5f5;font-weight:bold;">Detected At</td>
                <td style="padding:8px;">{detected_at.strftime('%A, %B %d %Y — %I:%M:%S %p CST')}</td></tr>
            <tr><td style="padding:8px;background:#f5f5f5;font-weight:bold;">Status</td>
                <td style="padding:8px;color:#2e7d32;"><b>SD-Task marked COMPLETE ✔</b></td></tr>
        </table>
        <p style="color:#555;margin-top:20px;">No further action required for today's window.</p>
    </body></html>
    """
    _send(subject, body, ALERT_RECIPIENTS)


# ─────────────────────────────────────────────────────────────
# 2. PRE-DEADLINE WARNING — 30 minutes before deadline
# ─────────────────────────────────────────────────────────────
def send_warning_mail(deadline: datetime):
    subject = "⚠️ [ZIP WATCHER] REMINDER — 30 Minutes to SD-Task Deadline!"
    body = f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px;">
        <h2 style="color:#e65100;">⚠️ Action Required: SD-Task Deadline Approaching</h2>
        <p style="font-size:16px;">The SD-Task ZIP file has <b>NOT yet been received</b>.</p>
        <table style="border-collapse:collapse;width:100%;max-width:500px;">
            <tr><td style="padding:8px;background:#fff3e0;font-weight:bold;">Deadline</td>
                <td style="padding:8px;color:#e65100;"><b>{deadline.strftime('%A, %B %d %Y — %I:%M %p CST')}</b></td></tr>
            <tr><td style="padding:8px;background:#fff3e0;font-weight:bold;">Time Remaining</td>
                <td style="padding:8px;"><b>~30 Minutes</b></td></tr>
            <tr><td style="padding:8px;background:#fff3e0;font-weight:bold;">Action</td>
                <td style="padding:8px;">Please paste the ZIP file into the watch directory NOW</td></tr>
        </table>
        <p style="color:#c62828;margin-top:20px;font-size:15px;">
            ⚡ If not completed before deadline, a HIGH ALERT will be triggered.
        </p>
    </body></html>
    """
    _send(subject, body, ALERT_RECIPIENTS)


# ─────────────────────────────────────────────────────────────
# 2b. PRE-DEADLINE WARNING (15 MIN) — 15 minutes before deadline
# ─────────────────────────────────────────────────────────────
def send_warning_15min_mail(deadline: datetime):
    subject = "⚠️ [ZIP WATCHER] URGENT — 15 Minutes to SD-Task Deadline!"
    body = f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px;background:#fffacd;">
        <h2 style="color:#d32f2f;">⚠️ URGENT: SD-Task Deadline in 15 Minutes!</h2>
        <p style="font-size:16px;color:#d32f2f;">The SD-Task ZIP file has <b>NOT yet been received</b>.</p>
        <table style="border-collapse:collapse;width:100%;max-width:500px;">
            <tr><td style="padding:8px;background:#ffcccc;font-weight:bold;">Deadline</td>
                <td style="padding:8px;color:#d32f2f;"><b>{deadline.strftime('%A, %B %d %Y — %I:%M %p CST')}</b></td></tr>
            <tr><td style="padding:8px;background:#ffcccc;font-weight:bold;">Time Remaining</td>
                <td style="padding:8px;color:#d32f2f;"><b>~15 Minutes ⏰</b></td></tr>
            <tr><td style="padding:8px;background:#ffcccc;font-weight:bold;">Action</td>
                <td style="padding:8px;"><b>IMMEDIATE ACTION REQUIRED</b> — Paste the ZIP file NOW</td></tr>
        </table>
        <p style="color:#b71c1c;margin-top:20px;font-size:15px;">
            🚨 If not completed within 15 minutes, a CRITICAL ALERT will be sent.
        </p>
    </body></html>
    """
    _send(subject, body, ALERT_RECIPIENTS)


# ─────────────────────────────────────────────────────────────
# 3. HIGH ALERT — 5 minutes AFTER deadline, task not done
# ─────────────────────────────────────────────────────────────
def send_high_alert_mail(deadline: datetime):
    subject = "🚨 [ZIP WATCHER] HIGH ALERT — SD-Task NOT Performed!"
    body = f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px;background:#fff8f8;">
        <h2 style="color:#b71c1c;">🚨 CRITICAL: SD-Task Was Not Completed</h2>
        <p style="font-size:16px;color:#b71c1c;">
            The ZIP file was <b>NOT received</b> before the deadline.<br>
            Immediate action or escalation is required.
        </p>
        <table style="border-collapse:collapse;width:100%;max-width:500px;">
            <tr><td style="padding:8px;background:#ffebee;font-weight:bold;">Missed Deadline</td>
                <td style="padding:8px;color:#b71c1c;"><b>{deadline.strftime('%A, %B %d %Y — %I:%M %p CST')}</b></td></tr>
            <tr><td style="padding:8px;background:#ffebee;font-weight:bold;">Alert Triggered</td>
                <td style="padding:8px;">{datetime.now().strftime('%I:%M:%S %p CST')}</td></tr>
            <tr><td style="padding:8px;background:#ffebee;font-weight:bold;">SD-Task Status</td>
                <td style="padding:8px;color:#b71c1c;"><b>❌ NOT PERFORMED</b></td></tr>
        </table>
        <p style="margin-top:20px;font-size:14px;color:#555;">
            Please investigate immediately and escalate to the responsible team.
        </p>
    </body></html>
    """
    _send(subject, body, ALERT_RECIPIENTS)


# ─────────────────────────────────────────────────────────────
# 4. DAILY SUMMARY EMAIL — End of day recap
# ─────────────────────────────────────────────────────────────
def send_daily_summary(events: list, task_done: bool, deadline: datetime):
    day_label   = deadline.strftime('%A, %B %d %Y')
    status_text = "✅ COMPLETED" if task_done else "❌ MISSED"
    status_color = "#2e7d32" if task_done else "#b71c1c"

    rows = ""
    if events:
        for ev in events:
            rows += f"""
            <tr>
                <td style="padding:6px;border:1px solid #ddd;">{ev['filename']}</td>
                <td style="padding:6px;border:1px solid #ddd;">{ev['time']}</td>
            </tr>"""
    else:
        rows = "<tr><td colspan='2' style='padding:8px;text-align:center;color:#999;'>No files received</td></tr>"

    subject = f"📋 [ZIP WATCHER] Daily Summary — {day_label}"
    body = f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px;">
        <h2 style="color:#1565c0;">📋 Daily ZIP Watcher Summary</h2>
        <p><b>Date:</b> {day_label} &nbsp;|&nbsp;
           <b>Deadline:</b> {deadline.strftime('%I:%M %p CST')} &nbsp;|&nbsp;
           <b>SD-Task:</b> <span style="color:{status_color};"><b>{status_text}</b></span>
        </p>
        <h3 style="margin-top:24px;">Files Received Today</h3>
        <table style="border-collapse:collapse;width:100%;max-width:600px;">
            <thead>
                <tr style="background:#1565c0;color:white;">
                    <th style="padding:8px;text-align:left;">File Name</th>
                    <th style="padding:8px;text-align:left;">Received At</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="margin-top:24px;color:#555;font-size:13px;">
            — Automated ZIP Watcher System
        </p>
    </body></html>
    """
    _send(subject, body, ALERT_RECIPIENTS)
