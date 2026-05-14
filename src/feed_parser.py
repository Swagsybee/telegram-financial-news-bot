import feedparser
import logging
from datetime import datetime, timedelta

from config import FEEDS, KEYWORD_ALLOWLIST, PUBLISH_TIME_WINDOW_MINUTES

logger = logging.getLogger(__name__)

def _is_relevant(title):
    """Checks if the article title contains any of the keywords in the allowlist."""
    title_lower = title.lower()
    for keyword in KEYWORD_ALLOWLIST:
        if keyword in title_lower:
            return True
    return False

def _is_recent(published_parsed):
    """Checks if the article was published within the last PUBLISH_TIME_WINDOW_MINUTES."""
    if not published_parsed:
        return False
    
    published_time = datetime(*published_parsed[:6])
    time_difference = datetime.now() - published_time
    
    return time_difference < timedelta(minutes=PUBLISH_TIME_WINDOW_MINUTES)

def get_new_articles():
    """Fetches and filters new articles from configured RSS feeds."""
    all_articles = []
    for source_name, feed_url in FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.title
                link = entry.link
                published_parsed = getattr(entry, 'published_parsed', None)

                if _is_relevant(title) and _is_recent(published_parsed):
                    all_articles.append({
                        "headline": title,
                        "source": source_name,
                        "url": link,
                        "published_at": datetime(*published_parsed[:6]).isoformat() if published_parsed else None
                    })
        except Exception as e:
            logger.error(f"Error parsing {source_name} feed: {e}")
    return all_articles
