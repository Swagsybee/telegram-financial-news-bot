import os
import time
import logging
import sqlite3
import feedparser
import requests
import schedule
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
CHECK_INTERVAL_MINUTES = 15
POST_LIMIT_PER_CYCLE = 3

# RSS Feeds
FEEDS = {
    "Reuters": "https://feeds.feedburner.com/reuters/businessNews",
    "CNBC": "https://www.cnbc.com/id/10000664/device/rss/rss.html"
}

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Database Setup for Deduplication
def init_db():
    conn = sqlite3.connect('news_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posted_articles (url TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

def is_already_posted(url):
    conn = sqlite3.connect('news_data.db')
    c = conn.cursor()
    c.execute("SELECT 1 FROM posted_articles WHERE url=?", (url,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_as_posted(url):
    conn = sqlite3.connect('news_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO posted_articles (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()

# Telegram Integration
def send_telegram_message(headline, source, url):
    message = (
        f"🚨 *MARKET UPDATE*\n\n"
        f"{headline}\n\n"
        f"📊 *Source:*\n{source}\n\n"
        f"🔗 *Read more:*\n{url}"
    )
    
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        logging.info(f"Successfully posted: {headline[:50]}...")
        return True
    except Exception as e:
        logging.error(f"Error sending to Telegram: {e}")
        return False

# News Processing
def check_news():
    logging.info("Checking feeds for new articles...")
    posts_this_cycle = 0
    
    for source_name, feed_url in FEEDS.items():
        if posts_this_cycle >= POST_LIMIT_PER_CYCLE:
            break
            
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if posts_this_cycle >= POST_LIMIT_PER_CYCLE:
                    break
                    
                headline = entry.title
                article_url = entry.link
                
                if not is_already_posted(article_url):
                    if send_telegram_message(headline, source_name, article_url):
                        mark_as_posted(article_url)
                        posts_this_cycle += 1
                        # Small delay to avoid Telegram rate limits
                        time.sleep(2)
        except Exception as e:
            logging.error(f"Error parsing {source_name} feed: {e}")

# Main Loop
if __name__ == "__main__":
    init_db()
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logging.error("Missing environment variables. Please check your .env file.")
        exit(1)
        
    logging.info("Starting Telegram Financial News Bot...")
    
    # Run once at startup
    check_news()
    
    # Schedule regular checks
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_news)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
