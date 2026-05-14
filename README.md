# Telegram Financial News Bot

An automated Python bot that monitors Reuters Business and CNBC Finance RSS feeds and posts new, relevant articles to a Telegram channel with professional formatting and advanced features.

## Features
- **Real-time Monitoring**: Checks Reuters and CNBC RSS feeds every 15 minutes.
- **Keyword Filtering (Allowlist)**: Only posts market/finance-related stories (e.g., market, stocks, economy, inflation, Fed, earnings, GDP).
- **First-Run Protection**: Seeds the database with existing articles on initial execution without posting to Telegram, preventing a flood of old news.
- **Admin Heartbeat/Crash Alerts**: Sends periodic health check messages to an admin chat and alerts on critical errors.
- **Telegram API Retry Logic**: Implements exponential backoff for 429 (rate limit) errors from the Telegram API.
- **HTML Escaping**: Properly escapes special characters in headlines to prevent broken messages.
- **Published-Date Filtering**: Only posts articles published within the last 30 minutes, in addition to URL deduplication.
- **Professional Formatting**: Custom templates for market updates.
- **Deduplication**: Persistent SQLite database ensures no article is posted twice.
- **Rate Limiting**: Limits to 3 posts per cycle to prevent spamming.
- **Modular Code Structure**: Organized into separate files for better maintainability and scalability.

## Setup Instructions

### 1. Create a Telegram Bot
1. Open Telegram and search for [@BotFather](https://t.me/botfather).
2. Send `/newbot` and follow the instructions to get your **API Token**.
3. Save this token as `TELEGRAM_BOT_TOKEN`.

### 2. Get Your Channel ID
1. Create a new public channel in Telegram.
2. Add your bot as an **Administrator** to the channel.
3. Your channel ID is usually its handle (e.g., `@MyFinanceChannel`). 
   *Note: For private channels, you may need the numerical ID.*

### 3. Get Your Admin Chat ID
1. Find your own Telegram User ID or a private group chat ID where you want to receive admin alerts.
2. You can use bots like `@userinfobot` to get your User ID.
3. Save this ID as `ADMIN_CHAT_ID`.

### 4. Environment Configuration
Create a `.env` file in the project root (or use the `.env.example` as a template):
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_handle
ADMIN_CHAT_ID=your_admin_chat_id_here
```

### 5. Local Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/Swagsybee/telegram-financial-news-bot.git
   cd telegram-financial-news-bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python src/main.py
   ```

## Hosting Instructions (Free)

### Option 1: PythonAnywhere (Recommended for Beginners)
1. Create a free account at [PythonAnywhere](https://www.pythonanywhere.com/).
2. Upload the entire `telegram-financial-news-bot` folder (including `src`, `requirements.txt`, and your `.env` file).
3. Open a "Bash Console" and navigate to the project directory.
4. Run:
   ```bash
   pip install --user -r requirements.txt
   python src/main.py
   ```
5. *Note: Free accounts require a daily manual restart unless you use a "Scheduled Task" (paid feature).*

### Option 2: Render (Background Worker)
1. Push your code to a GitHub repository (which you have already done).
2. Create a new **Background Worker** on [Render](https://render.com/).
3. Connect your GitHub repo.
4. Set the "Start Command" to `python src/main.py`.
5. Add your `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`, and `ADMIN_CHAT_ID` in the **Environment** tab.

### Option 3: Railway
1. Push code to GitHub.
2. Create a new project on [Railway](https://railway.app/).
3. Link your repository. Railway will automatically detect the Python environment.
4. Add environment variables in the project settings.

## Files
- `src/`:
  - `main.py`: Main bot logic, scheduling, and first-run protection.
  - `config.py`: Environment variables and constants.
  - `database.py`: SQLite database operations for deduplication and bot state.
  - `telegram_client.py`: Telegram API interactions with retry logic and HTML escaping.
  - `feed_parser.py`: RSS feed parsing, keyword filtering, and date filtering.
- `requirements.txt`: Python dependencies.
- `README.md`: Project documentation and setup instructions.
- `.env.example`: Template for environment variables.
- `news_data.db`: SQLite database (created automatically on first run).
- `bot.log`: Log file for monitoring performance.
