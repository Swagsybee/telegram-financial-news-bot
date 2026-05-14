import requests
import time
import logging
import html

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, ADMIN_CHAT_ID

logger = logging.getLogger(__name__)

def _send_message(chat_id, text, parse_mode="Markdown", disable_web_page_preview=False):
    """Internal function to send a message to Telegram with retry logic."""
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview
    }

    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429: # Too Many Requests (rate limit)
                retry_after = response.json().get("parameters", {}).get("retry_after", 5) # Default to 5 seconds
                logger.warning(f"Rate limit hit. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                retries += 1
            else:
                logger.error(f"Telegram API HTTP error: {e} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending to Telegram: {e}")
            return False
    logger.error(f"Failed to send message after {max_retries} retries due to rate limits.")
    return False

def send_article_message(headline, source, url):
    """Sends a formatted article message to the main Telegram channel."""
    # HTML Escaping for headline
    escaped_headline = html.escape(headline)

    message = (
        f"🚨 *MARKET UPDATE*\n\n"
        f"{escaped_headline}\n\n"
        f"📊 *Source:*\n{source}\n\n"
        f"🔗 *Read more:*\n{url}"
    )
    return _send_message(TELEGRAM_CHANNEL_ID, message, parse_mode="Markdown")

def send_admin_message(message):
    """Sends a message to the admin chat for alerts or heartbeats."""
    if ADMIN_CHAT_ID:
        return _send_message(ADMIN_CHAT_ID, message, parse_mode="Markdown")
    else:
        logger.warning("ADMIN_CHAT_ID is not set. Cannot send admin messages.")
        return False
