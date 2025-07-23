# cmbs_reminder_system/agents/notification.py
from .base import Agent

class NotificationAgent(Agent):
    """
    Handles dispatching reminders via various channels (e.g., email, Slack).
    """
    def __init__(self):
        super().__init__("NotificationAgent")

    def send_reminder(self, recipient: str, subject: str, message: str) -> bool:
        print(f"\n--- [{self.name}] Sending Reminder ---")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Message (truncated):\n{message[:500]}...")
        print(f"------------------------------------\n")
        return True