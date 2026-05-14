import time
import logging
import schedule
from datetime import datetime, timedelta

from config import (
    CHECK_INTERVAL_MINUTES,
    POST_LIMIT_PER_CYCLE,
    HEARTBEAT_INTERVAL_HOURS,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHANNEL_ID,
    ADMIN_CHAT_ID,
    LOG_FILE
)
from database import (
    init_db,
    is_already_posted,
    mark_as_posted,
    get_last_heartbeat_time,
    update_last_heartbeat_time,
    get_first_run_status,
    set_first_run_completed
)
from telegram_client import send_article_message, send_admin_message
from feed_parser import get_new_articles

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_for_new_articles(is_first_run=False):
    logger.info("Checking feeds for new articles...")
    posts_this_cycle = 0
    articles = get_new_articles()

    for article in articles:
        if posts_this_cycle >= POST_LIMIT_PER_CYCLE:
            break

        headline = article["headline"]
        source = article["source"]
        url = article["url"]
        published_at = article["published_at"]

        if not is_already_posted(url):
            if is_first_run:
                # Seed database without posting to Telegram on first run
                mark_as_posted(url, published_at)
                logger.info(f"Seeding database with existing article: {headline[:50]}...")
            else:
                if send_article_message(headline, source, url):
                    mark_as_posted(url, published_at)
                    posts_this_cycle += 1
                    # Small delay to avoid Telegram rate limits
                    time.sleep(2)
        else:
            logger.info(f"Article already posted or seeded: {headline[:50]}...")

def send_heartbeat():
    last_heartbeat = get_last_heartbeat_time()
    now = datetime.now()

    if not last_heartbeat or (now - last_heartbeat) > timedelta(hours=HEARTBEAT_INTERVAL_HOURS):
        message = f"💚 Bot is alive! Last checked: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        send_admin_message(message)
        update_last_heartbeat_time()

def main():
    init_db()

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logger.error("Missing critical environment variables (TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID).")
        send_admin_message("🚨 Bot startup failed: Missing Telegram bot token or channel ID.")
        exit(1)

    logger.info("Starting Telegram Financial News Bot...")

    if not get_first_run_status():
        logger.info("First run detected. Seeding database with existing articles...")
        check_for_new_articles(is_first_run=True)
        set_first_run_completed()
        send_admin_message("✅ Bot first run completed. Database seeded. Will start posting new articles now.")
    else:
        logger.info("Not first run. Proceeding with normal operation.")

    # Run once at startup (after potential seeding)
    check_for_new_articles()

    # Schedule regular checks
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_for_new_articles)
    schedule.every(HEARTBEAT_INTERVAL_HOURS).hours.do(send_heartbeat)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.critical(f"Critical error in main loop: {e}", exc_info=True)
            send_admin_message(f"🔥 Critical bot error: {e}")
            time.sleep(60) # Wait a bit before retrying to prevent spamming

if __name__ == "__main__":
    main()
