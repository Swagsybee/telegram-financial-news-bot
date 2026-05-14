# Telegram Financial News Bot

An automated Python bot that monitors Reuters Business and CNBC Finance RSS feeds and posts new articles to a Telegram channel with professional formatting and deduplication.

## Features
- **Real-time Monitoring**: Checks Reuters and CNBC RSS feeds every 15 minutes.
- **Professional Formatting**: Custom templates for market updates.
- **Deduplication**: Persistent SQLite database ensures no article is posted twice.
- **Rate Limiting**: Limits to 3 posts per cycle to prevent spamming.
- **Production Ready**: Includes error handling and logging.

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

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_handle
```

### 4. Local Installation
1. Clone this repository or download the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```

## Hosting Instructions (Free)

### Option 1: PythonAnywhere (Recommended for Beginners)
1. Create a free account at [PythonAnywhere](https://www.pythonanywhere.com/).
2. Upload `bot.py`, `requirements.txt`, and your `.env` file.
3. Open a "Bash Console" and run:
   ```bash
   pip install --user -r requirements.txt
   python bot.py
   ```
4. *Note: Free accounts require a daily manual restart unless you use a "Scheduled Task" (paid feature).*

### Option 2: Render (Background Worker)
1. Push your code to a GitHub repository.
2. Create a new **Background Worker** on [Render](https://render.com/).
3. Connect your GitHub repo.
4. Set the "Start Command" to `python bot.py`.
5. Add your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID` in the **Environment** tab.

### Option 3: Railway
1. Push code to GitHub.
2. Create a new project on [Railway](https://railway.app/).
3. Link your repository. Railway will automatically detect the Python environment.
4. Add environment variables in the project settings.

## Files
- `bot.py`: Main automation script.
- `requirements.txt`: Python dependencies.
- `news_data.db`: SQLite database (created automatically on first run).
- `bot.log`: Log file for monitoring performance.
