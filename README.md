# Telegram Financial News Bot

An automated Python bot that monitors Reuters Business and CNBC Finance RSS feeds and posts new articles to a Telegram channel with professional formatting, deduplication, and keyword filtering.

---

## Features

- **Real-time Monitoring** — Checks Reuters and CNBC RSS feeds every 15 minutes
- **Smart Deduplication** — Persistent SQLite database ensures no article is posted twice
- **Keyword Filtering** — Only posts market-relevant articles (stocks, Fed, earnings, crypto, etc.)
- **First-Run Protection** — Seeds the database on startup without flooding your channel
- **Rate Limiting** — Max 3 posts per cycle with built-in delays to respect Telegram limits
- **Retry Logic** — Exponential backoff for Telegram API failures and rate limits
- **Admin Alerts** — Optional crash and startup notifications to a private admin chat
- **Production Ready** — Error handling, logging to file + console, graceful shutdown

---

## Project Structure

```
telegram-financial-news-bot/
├── bot.py              # Main automation script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── news_data.db        # SQLite database (auto-created)
└── bot.log             # Log file (auto-created)
```

---

## Prerequisites

- Python 3.10 or higher
- A Telegram account
- A Telegram channel (public or private)
- A Telegram bot (via [@BotFather](https://t.me/BotFather))

---

## Local Setup

### 1. Clone or Download

```bash
git clone https://github.com/YOUR_USERNAME/telegram-financial-news-bot.git
cd telegram-financial-news-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_handle

# Optional but recommended
ADMIN_CHAT_ID=your_telegram_user_id

# Optional overrides
CHECK_INTERVAL_MINUTES=15
POST_LIMIT_PER_CYCLE=3
KEYWORD_FILTER_ENABLED=true
FIRST_RUN_GRACE_MINUTES=15
```

### 4. Run the Bot

```bash
python bot.py
```

**On first run**, the bot will scan both feeds and record all current articles in the database **without posting anything**. From the next cycle onward, it will only post new articles that match the keyword filter.

---

## Telegram Setup Guide

### Step 1: Create a Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Save the **API Token** you receive

### Step 2: Create a Channel

1. In Telegram, create a new channel (public recommended for easier setup)
2. Give it a handle like `@MyFinanceNews`
3. Add your bot as an **Administrator** with permission to **Post Messages**

### Step 3: Get Your IDs

| ID | How to Get |
|---|---|
| **Channel ID** | If public: use the handle (`@MyFinanceNews`). If private: use [@userinfobot](https://t.me/userinfobot) or [@getidsbot](https://t.me/getidsbot) |
| **Admin Chat ID** | Message [@userinfobot](https://t.me/userinfobot) from your personal account. It will reply with your numeric user ID. |

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | — | Bot API token from @BotFather |
| `TELEGRAM_CHANNEL_ID` | ✅ | — | Target channel handle or numeric ID |
| `ADMIN_CHAT_ID` | ❌ | — | Your personal Telegram user ID for alerts |
| `CHECK_INTERVAL_MINUTES` | ❌ | `15` | Minutes between feed checks |
| `POST_LIMIT_PER_CYCLE` | ❌ | `3` | Max articles posted per check |
| `KEYWORD_FILTER_ENABLED` | ❌ | `true` | Enable/disable keyword filtering |
| `FIRST_RUN_GRACE_MINUTES` | ❌ | `15` | Only post articles newer than this |

---

## Cloud Deployment

### Option A: Render (Recommended for Beginners)

1. Push your code to a **public or private** GitHub repository
2. Go to [render.com](https://render.com) and create a new **Background Worker**
3. Connect your GitHub repository
4. **Start Command**: `python bot.py`
5. Add your environment variables in the **Environment** tab
6. Click **Deploy**

> **Note:** Render's free tier spins down after 15 minutes of inactivity. For a bot that needs to run every 15 minutes, this is actually fine — the cron-like schedule will wake it up. For 24/7 uptime, use a paid plan.

### Option B: Railway

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) and create a new project
3. Choose **Deploy from GitHub repo**
4. Select your repository — Railway auto-detects Python
5. Go to **Variables** and add all environment variables
6. Deploy — no start command needed (auto-detected)

> **Note:** Railway's free tier has usage limits. Monitor your dashboard.

### Option C: PythonAnywhere

1. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Open a **Bash console** and clone your repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/telegram-financial-news-bot.git
   cd telegram-financial-news-bot
   pip install --user -r requirements.txt
   ```
3. Create a **Scheduled Task** (paid feature) or run manually:
   ```bash
   python bot.py
   ```

> **Note:** Free accounts require a daily manual restart unless you upgrade.

### Option D: VPS / Dedicated Server

For 24/7 reliable operation, use a cheap VPS (DigitalOcean, Hetzner, AWS Lightsail, etc.):

```bash
# On your server
git clone https://github.com/YOUR_USERNAME/telegram-financial-news-bot.git
cd telegram-financial-news-bot
pip install -r requirements.txt

# Create .env file with your variables
nano .env

# Run with nohup or systemd
nohup python bot.py &
```

**Recommended:** Set up a `systemd` service for auto-restart on crash:

```ini
# /etc/systemd/system/telegram-news-bot.service
[Unit]
Description=Telegram Financial News Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/telegram-financial-news-bot
Environment="TELEGRAM_BOT_TOKEN=your_token"
Environment="TELEGRAM_CHANNEL_ID=@your_channel"
ExecStart=/usr/bin/python3 /home/youruser/telegram-financial-news-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-news-bot
sudo systemctl start telegram-news-bot
sudo systemctl status telegram-news-bot
```

---

## Keyword Filter

The bot uses an allowlist to ensure only market-relevant articles are posted. Default keywords include:

`market`, `stock`, `equity`, `fed`, `earnings`, `economy`, `finance`, `trading`, `investor`, `nasdaq`, `s&p`, `bond`, `treasury`, `inflation`, `gdp`, `recession`, `crypto`, `bitcoin`, `forex`, `ipo`, `merger`, `oil`, `gold`

To customize, edit the `KEYWORD_ALLOWLIST` list in `bot.py`.

To disable filtering entirely, set `KEYWORD_FILTER_ENABLED=false` in your environment.

---

## Monitoring & Logs

### Log File
All activity is logged to `bot.log` in the project root:

```bash
tail -f bot.log
```

### Admin Alerts
If `ADMIN_CHAT_ID` is set, the bot will send you:
- ✅ **Startup confirmation** when first run completes
- 💥 **Crash alerts** if the bot encounters a fatal error

### Health Check
You can verify the bot is running by checking the log timestamp:

```bash
grep "Checking feeds" bot.log | tail -5
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| `Missing environment variables` error | `.env` not loaded or vars not set | Ensure `.env` exists or set vars in your hosting dashboard |
| Bot not posting anything | First run protection active | Wait 15 minutes for the next cycle |
| `400 Bad Request` from Telegram | Unescaped Markdown in headline | Already fixed in this version — update if using old code |
| `429 Too Many Requests` | Telegram rate limit | Bot auto-retries with backoff. If persistent, increase `time.sleep()` delay |
| Old articles being posted | No published-date check | Already fixed — bot now skips articles older than 15 minutes |
| Off-topic articles posted | Keyword filter disabled or missing | Set `KEYWORD_FILTER_ENABLED=true` and verify `KEYWORD_ALLOWLIST` |
| Feed parse error | RSS URL changed or down | Check the feed URL in a browser. Update `FEEDS` dict in `bot.py` if needed |
| Bot stops after some time | Hosting platform idle timeout | Use a paid plan or ping service (UptimeRobot) to keep alive |

---

## Security Notes

- **Never commit your real `.env` file to GitHub.** It contains your bot token.
- **Never share your `TELEGRAM_BOT_TOKEN`.** Anyone with it can control your bot.
- Use environment variables in production hosting platforms, not hardcoded values.

---

## License

MIT License — free to use, modify, and distribute.

---

## Credits

Original concept by [@Swagsybee](https://github.com/Swagsybee/telegram-financial-news-bot).  
This fork includes critical production fixes: Markdown escaping, first-run protection, keyword filtering, retry logic, and admin alerts.
