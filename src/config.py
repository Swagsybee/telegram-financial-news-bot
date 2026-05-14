import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID") # New: For heartbeat and crash alerts

# Bot Operation Configuration
CHECK_INTERVAL_MINUTES = 15
POST_LIMIT_PER_CYCLE = 3
PUBLISH_TIME_WINDOW_MINUTES = 30 # New: Only post articles published within this time

# RSS Feed Configuration
FEEDS = {
    "Reuters": "https://feeds.feedburner.com/reuters/businessNews",
    "CNBC": "https://www.cnbc.com/id/10000664/device/rss/rss.html"
}

# Keyword Filtering (Allowlist) - New Feature
KEYWORD_ALLOWLIST = [
    "market", "markets", "stock", "stocks", "economy", "economic",
    "inflation", "deflation", "fed", "federal reserve", "interest rate",
    "earnings", "gdp", "recession", "bull market", "bear market",
    "investing", "investment", "finance", "financial", "trading",
    "dow jones", "s&p 500", "nasdaq", "treasury", "bond", "currency",
    "forex", "commodities", "oil", "gold", "silver", "cryptocurrency",
    "bitcoin", "ethereum", "banking", "bank", "ceo", "cfo", "merger",
    "acquisition", "ipo", "public offering", "venture capital",
    "private equity", "dividend", "yield", "portfolio", "analyst",
    "forecast", "outlook", "growth", "profit", "revenue", "debt",
    "credit", "tax", "budget", "fiscal", "monetary policy", "central bank"
]

# Database Configuration
DATABASE_NAME = "news_data.db"

# Logging Configuration
LOG_FILE = "bot.log"

# Health Check Configuration
HEARTBEAT_INTERVAL_HOURS = 6 # Send admin heartbeat every 6 hours
