import sqlite3
import logging
from datetime import datetime, timedelta

from config import DATABASE_NAME

logger = logging.getLogger(__name__)

def init_db():
    """Initializes the SQLite database and creates the necessary tables."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS posted_articles (
            url TEXT PRIMARY KEY,
            published_at TEXT
        )""")
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")

def is_already_posted(url):
    """Checks if an article URL has already been posted."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("SELECT 1 FROM posted_articles WHERE url=?", (url,))
        result = c.fetchone()
        conn.close()
        return result is not None
    except sqlite3.Error as e:
        logger.error(f"Error checking if article is posted: {e}")
        return False # Assume not posted to avoid blocking new articles on DB error

def mark_as_posted(url, published_at=None):
    """Marks an article as posted in the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO posted_articles (url, published_at) VALUES (?, ?)", (url, published_at))
        conn.commit()
        conn.close()
        logger.info(f"Article marked as posted: {url}")
    except sqlite3.Error as e:
        logger.error(f"Error marking article as posted: {e}")

def get_last_heartbeat_time():
    """Retrieves the last heartbeat time from the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS bot_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        c.execute("SELECT value FROM bot_state WHERE key='last_heartbeat'",)
        result = c.fetchone()
        conn.close()
        return datetime.fromisoformat(result[0]) if result else None
    except sqlite3.Error as e:
        logger.error(f"Error retrieving last heartbeat time: {e}")
        return None

def update_last_heartbeat_time():
    """Updates the last heartbeat time in the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("INSERT OR REPLACE INTO bot_state (key, value) VALUES (?, ?)", ('last_heartbeat', now))
        conn.commit()
        conn.close()
        logger.info("Last heartbeat time updated.")
    except sqlite3.Error as e:
        logger.error(f"Error updating last heartbeat time: {e}")

def get_first_run_status():
    """Retrieves the first run status from the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS bot_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        c.execute("SELECT value FROM bot_state WHERE key='first_run_completed'",)
        result = c.fetchone()
        conn.close()
        return result is not None and result[0] == 'True'
    except sqlite3.Error as e:
        logger.error(f"Error retrieving first run status: {e}")
        return False

def set_first_run_completed():
    """Sets the first run completed status in the database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO bot_state (key, value) VALUES (?, ?)", ('first_run_completed', 'True'))
        conn.commit()
        conn.close()
        logger.info("First run status set to completed.")
    except sqlite3.Error as e:
        logger.error(f"Error setting first run completed status: {e}")
