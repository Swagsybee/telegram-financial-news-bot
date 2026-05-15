import os
import time
import logging
import sqlite3
import feedparser
import requests
import schedule
import re
import html
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # Optional: for crash alerts

CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))
POST_LIMIT_PER_CYCLE = int(os.getenv("POST_LIMIT_PER_CYCLE", "3"))
KEYWORD_FILTER_ENABLED = os.getenv("KEYWORD_FILTER_ENABLED", "true").lower() == "true"
FIRST_RUN_GRACE_MINUTES = int(os.getenv("FIRST_RUN_GRACE_MINUTES", "15"))

# ─────────────────────────────────────────────
# RSS Feeds (updated Reuters URL)
# ─────────────────────────────────────────────
FEEDS = {
    "Reuters": "https://www.reutersagency.com/feed/?taxonomy=markets&post_type=reuters-best",
    "CNBC": "https://www.cnbc.com/id/10000664/device/rss/rss.html"
}

# ─────────────────────────────────────────────
# Keyword Allowlist (case-insensitive)
# ─────────────────────────────────────────────
KEYWORD_ALLOWLIST = [
    "market", "stock", "equity", "fed", "federal reserve", "earnings",
    "economy", "economic", "finance", "financial", "trading", "trade",
    "investor", "investment", "wall street", "nasdaq", "s&p", "s&p 500",
    "dow", "dow jones", "bond", "treasury", "yield", "inflation", "gdp",
    "recession", "bull", "bear", "ipo", "merger", "acquisition", "commodity",
    "oil", "gold", "crypto", "bitcoin", "forex", "interest rate", "fomc"
]

# ─────────────────────────────────────────────
# Logging Setup
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ─────────────────────────────────────────────
# Database: Enhanced schema with timestamps
# ─────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("news_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posted_articles (
            url TEXT PRIMARY KEY,
            headline TEXT,
            source TEXT,
            published_at TIMESTAMP,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Track first run to prevent initial flood
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_bot_state(key, default=None):
    conn = sqlite3.connect("news_data.db")
    c = conn.cursor()
    c.execute("SELECT value FROM bot_state WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else default

def set_bot_state(key, value):
    conn = sqlite3.connect("news_data.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO bot_state (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()

def is_already_posted(url):
    conn = sqlite3.connect("news_data.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM posted_articles WHERE url=?", (url,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_as_posted(url, headline, source, published_at):
    conn = sqlite3.connect("news_data.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO posted_articles (url, headline, source, published_at) VALUES (?, ?, ?, ?)",
        (url, headline, source, published_at)
    )
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────
def escape_markdown(text):
    """Escape Telegram MarkdownV1 special characters."""
    return re.sub(r"([*_`\[\]()])", r"\\\1", text)

def escape_html_entities(text):
    """Unescape HTML entities like &amp; -> &."""
    return html.unescape(text)

def matches_keyword_filter(headline, description=""):
    """Check if article matches keyword allowlist."""
    if not KEYWORD_FILTER_ENABLED:
        return True
    text = f"{headline} {description}".lower()
    return any(keyword.lower() in text for keyword in KEYWORD_ALLOWLIST)

def parse_published_date(entry):
    """Extract published datetime from feed entry."""
    # Try common RSS date fields
    for attr in ["published_parsed", "updated_parsed", "created_parsed"]:
        if hasattr(entry, attr) and getattr(entry, attr):
            t = getattr(entry, attr)
            return datetime(*t[:6], tzinfo=timezone.utc)
    # Fallback: try string parsing
    for attr in ["published", "updated", "created"]:
        if hasattr(entry, attr) and getattr(entry, attr):
            try:
                return datetime.strptime(getattr(entry, attr), "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                pass
    return datetime.now(timezone.utc)

def is_within_grace_period(published_dt, minutes=FIRST_RUN_GRACE_MINUTES):
    """Check if article is recent enough to post."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    return published_dt >= cutoff

# ─────────────────────────────────────────────
# Telegram Integration with Retry
# ─────────────────────────────────────────────
def send_telegram_message(headline, source, url, max_retries=3):
    headline_clean = escape_html_entities(headline)
    headline_safe = escape_markdown(headline_clean)
    source_safe = escape_markdown(source)
    url_safe = escape_markdown(url)

    message = (
        f"🚨 *MARKET UPDATE*\n\n"
        f"{headline_safe}\n\n"
        f"📊 *Source:*\n{source_safe}\n\n"
        f"🔗 *Read more:*\n{url_safe}"
    )

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, json=payload, timeout=15)
            if response.status_code == 429:
                retry_after = response.json().get("parameters", {}).get("retry_after", 2 ** attempt)
                logging.warning(f"Rate limited. Retrying after {retry_after}s...")
                time.sleep(retry_after)
                continue
            response.raise_for_status()
            logging.info(f"✅ Posted: {headline_clean[:60]}...")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Telegram API error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logging.error(f"❌ Failed to post after {max_retries} attempts: {headline_clean[:60]}")
                return False
    return False

def send_admin_alert(message):
    """Send alert to admin chat if configured."""
    if not ADMIN_CHAT_ID:
        return
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": f"⚠️ *Bot Alert*\n\n{escape_markdown(message)}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(api_url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Failed to send admin alert: {e}")

# ─────────────────────────────────────────────
# News Processing
# ─────────────────────────────────────────────
def check_news():
    logging.info("🔍 Checking feeds for new articles...")
    posts_this_cycle = 0
    is_first_run = get_bot_state("first_run_complete") != "true"

    if is_first_run:
        logging.info("🚀 First run detected. Seeding database without posting...")

    all_entries = []

    # Fetch all feeds
    for source_name, feed_url in FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo:
                logging.warning(f"⚠️ {source_name} feed may be malformed: {feed.bozo_exception}")
            for entry in feed.entries:
                headline = getattr(entry, "title", "No Title")
                article_url = getattr(entry, "link", "")
                description = getattr(entry, "summary", "")
                published_dt = parse_published_date(entry)

                all_entries.append({
                    "headline": headline,
                    "url": article_url,
                    "source": source_name,
                    "published_dt": published_dt,
                    "description": description
                })
        except Exception as e:
            logging.error(f"❌ Error parsing {source_name} feed: {e}")
            continue

    # Sort by published date (newest first)
    all_entries.sort(key=lambda x: x["published_dt"], reverse=True)

    for entry in all_entries:
        if posts_this_cycle >= POST_LIMIT_PER_CYCLE:
            break

        headline = entry["headline"]
        url = entry["url"]
        source = entry["source"]
        published_dt = entry["published_dt"]
        description = entry["description"]

        if not url:
            continue

        if is_already_posted(url):
            continue

        # First run: seed DB only, do not post
        if is_first_run:
            mark_as_posted(url, headline, source, published_dt)
            continue

        # After first run: apply filters
        if not is_within_grace_period(published_dt):
            logging.debug(f"⏭️ Skipping old article: {headline[:50]}...")
            mark_as_posted(url, headline, source, published_dt)  # Mark to avoid re-checking
            continue

        if not matches_keyword_filter(headline, description):
            logging.debug(f"⏭️ Skipping off-topic article: {headline[:50]}...")
            mark_as_posted(url, headline, source, published_dt)
            continue

        if send_telegram_message(headline, source, url):
            mark_as_posted(url, headline, source, published_dt)
            posts_this_cycle += 1
            time.sleep(1.5)  # Rate limit buffer

    if is_first_run:
        set_bot_state("first_run_complete", "true")
        logging.info("✅ First run complete. Database seeded. Future runs will post new articles.")
        if ADMIN_CHAT_ID:
            send_admin_alert("🚀 Bot started successfully! Database seeded. Ready to post new articles.")

    logging.info(f"📊 Cycle complete. Posted {posts_this_cycle}/{POST_LIMIT_PER_CYCLE} articles.")

# ─────────────────────────────────────────────
# Main Loop with Graceful Error Handling
# ─────────────────────────────────────────────
def main():
    init_db()

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logging.error("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID. Check your .env file.")
        exit(1)

    logging.info("🤖 Starting Telegram Financial News Bot...")
    logging.info(f"   ⏱️  Check interval: {CHECK_INTERVAL_MINUTES} min")
    logging.info(f"   📬 Post limit: {POST_LIMIT_PER_CYCLE}/cycle")
    logging.info(f"   🔑 Keyword filter: {'ON' if KEYWORD_FILTER_ENABLED else 'OFF'}")

    # Run first check immediately
    try:
        check_news()
    except Exception as e:
        logging.error(f"❌ Critical error during first check: {e}")
        send_admin_alert(f"Critical error on startup: {str(e)[:200]}")

    # Schedule regular checks
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_news)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped by user.")
    except Exception as e:
        logging.error(f"💥 Fatal error in main loop: {e}")
        send_admin_alert(f"💥 Bot crashed in main loop: {str(e)[:200]}")
        raise

if __name__ == "__main__":
    main()
