# utils/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

def send_reset_email(to_email: str, reset_token: str):
    """
    Send a password reset email with a reset link.
    """
    reset_link = f"http://localhost:8000/auth/reset-password?token={reset_token}"

    subject = "Password Reset Request"
    body = f"""
    <h3>Password Reset Request</h3>
    <p>Click the link below to reset your password (valid for 15 minutes):</p>
    <a href="{reset_link}">{reset_link}</a>
    """

    # Create MIME message
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
