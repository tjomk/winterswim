"""
Telegram notification service.

Sends notifications to a Telegram chat via bot API.
"""

import logging
from typing import Optional
from django.conf import settings
import urllib.request
import urllib.parse
import json

logger = logging.getLogger(__name__)


class TelegramNotificationService:
    """
    Service for sending Telegram notifications.

    Uses the Telegram Bot API to send messages to a configured chat.
    """

    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        self.enabled = bool(self.bot_token and self.chat_id)

        if not self.enabled:
            logger.warning(
                "Telegram notifications are disabled. "
                "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to enable."
            )

    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send a message to the configured Telegram chat.

        Args:
            message: The message text to send (supports HTML formatting)
            parse_mode: Telegram parse mode ('HTML' or 'Markdown')

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram notifications disabled, skipping message")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            data = urllib.parse.urlencode({
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True,
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data, method='POST')

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))

                if result.get('ok'):
                    logger.info("Telegram notification sent successfully")
                    return True
                else:
                    logger.error(f"Telegram API error: {result}")
                    return False

        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    def notify_new_submission(self, location) -> bool:
        """
        Send a notification about a new location submission.

        Args:
            location: The Location model instance that was submitted

        Returns:
            bool: True if notification was sent successfully
        """
        admin_url = f"{settings.ALLOWED_HOSTS[0]}/admin/locations/location/{location.pk}/change/"
        if not admin_url.startswith('http'):
            admin_url = f"http://{admin_url}"

        message = (
            f"🏊 <b>New Winter Swimming Location Submitted</b>\n\n"
            f"<b>Name:</b> {location.name}\n"
            f"<b>Type:</b> {location.get_location_type_display()}\n"
            f"<b>Location:</b> {location.address or 'No address provided'}\n"
        )

        if location.description:
            # Truncate long descriptions
            desc = location.description[:200]
            if len(location.description) > 200:
                desc += "..."
            message += f"<b>Description:</b> {desc}\n"

        if location.submitted_by_name:
            message += f"<b>Submitted by:</b> {location.submitted_by_name}\n"

        message += f"\n<a href='{admin_url}'>Review in Admin</a>"

        return self.send_message(message)


# Singleton instance
telegram_service = TelegramNotificationService()
