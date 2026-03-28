"""
debug_email.py — Run this to test your SMTP credentials directly.
Place in your zip-watcher folder and run: python debug_email.py
"""

import smtplib
import os

# ── Option A: Read from .env file manually ──────────────────
env_path = os.path.join(os.path.dirname(__file__), ".env")
creds = {}

if os.path.exists(env_path):
    print(f"✅ Found .env file at: {env_path}\n")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
else:
    print(f"❌ .env file NOT found at: {env_path}")
    print("   → Make sure you renamed .env.template to .env\n")
    exit(1)

SMTP_USER     = creds.get("SMTP_USER", "")
SMTP_PASSWORD = creds.get("SMTP_PASSWORD", "")
SMTP_HOST     = creds.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(creds.get("SMTP_PORT", 587))

print(f"SMTP_HOST     : {SMTP_HOST}")
print(f"SMTP_PORT     : {SMTP_PORT}")
print(f"SMTP_USER     : {SMTP_USER}")
print(f"SMTP_PASSWORD : {SMTP_PASSWORD[:4]}{'*' * (len(SMTP_PASSWORD)-4)} ({len(SMTP_PASSWORD)} chars)")
print()

# ── Validate App Password format ────────────────────────────
clean_pw = SMTP_PASSWORD.replace(" ", "")
if len(clean_pw) != 16:
    print(f"⚠️  WARNING: App Password is {len(clean_pw)} chars after removing spaces.")
    print("   Google App Passwords must be exactly 16 characters.")
    print("   Check your .env file for extra spaces or newlines.\n")
else:
    print(f"✅ Password length OK (16 chars)\n")

# ── Attempt SMTP login ───────────────────────────────────────
print("Attempting SMTP connection...")
try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        server.set_debuglevel(1)   # Shows full SMTP conversation
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, clean_pw)
        print("\n✅ LOGIN SUCCESSFUL — credentials are correct!")
        print("   Your .env is configured properly. Re-run main.py.\n")
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTH FAILED: {e}")
    print("""
Fix checklist:
  1. Gmail 2-Step Verification must be ON
     → myaccount.google.com → Security → 2-Step Verification

  2. App Password must be generated AFTER enabling 2FA
     → myaccount.google.com → Security → 2-Step Verification
     → Scroll to bottom → App passwords
     → Select app: Mail, Select device: Windows Computer → Generate

  3. Copy the 16-char password WITH NO SPACES into .env:
     SMTP_PASSWORD=abcdabcdabcdabcd   ← correct
     SMTP_PASSWORD=abcd abcd abcd     ← wrong (spaces)

  4. Make sure you saved the .env file (not .env.template)

  5. If using Outlook instead of Gmail, change in .env:
     SMTP_HOST=smtp-mail.outlook.com
     SMTP_PORT=587
""")
except Exception as e:
    print(f"\n❌ Connection error: {e}")
    print("   Check your internet connection or firewall settings.")
