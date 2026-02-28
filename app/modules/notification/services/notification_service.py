from app.core.logging.logger import add_to_log
import asyncio

class NotificationService:
    def __init__(self):
        # Notification service might not need session, but if it logged to DB it would.
        # For now, it's stateless/external.
        pass

    async def send_email(self, recipient: str, subject: str, body: str):
        """Dummy method to send email."""
        add_to_log("info", f"Sending email to {recipient}: {subject}")
        # Simulate delay
        await asyncio.sleep(0.1)
        add_to_log("info", "Email sent successfully")

    async def send_sms(self, phone: str, message: str):
        """Dummy method to send SMS."""
        add_to_log("info", f"Sending SMS to {phone}: {message}")
        await asyncio.sleep(0.1)
