# 🦞 Moltbook Highlights Bot

Automated bot that scrapes [Moltbook.com](https://www.moltbook.com) every 4-6 hours, extracts the most interesting AI agent posts, and auto-posts them to X (Twitter) using browser automation.

**Total Monthly Cost: $0**

## Tech Stack

- **Language**: Python 3.11
- **Scraping**: Playwright (headless Chromium)
- **X Posting**: Playwright browser automation (bypasses API costs)
- **Storage**: JSON files committed to GitHub repo
- **Hosting**: GitHub Actions (2000 free minutes/month)
- **Scheduling**: GitHub Actions cron
- **Monitoring**: Discord webhook (optional)

## Project Structure

```
moltbook/
├── .github/
│   └── workflows/
│       └── moltbook-bot.yml    # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── scraper.py              # Moltbook scraper
│   ├── ranker.py               # Content ranking system
│   ├── generator.py            # Tweet generator
│   └── poster.py               # Twitter poster
├── data/
│   └── posts.json              # Scraped posts database
├── main.py                     # Main orchestration script
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions

### Step 1: Clone and Install

```bash
git clone https://github.com/YOUR_USERNAME/moltbook-highlights-bot
cd moltbook-highlights-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Get Twitter Cookies

Run the login script locally to save your Twitter session:

```bash
python src/poster.py
```

This opens a browser window. Log in to Twitter manually, then press Enter in the terminal. Your cookies will be saved to `twitter_cookies.json`.

### Step 3: Add GitHub Secrets

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `TWITTER_COOKIES`: Paste the entire contents of `twitter_cookies.json`
   - `DISCORD_WEBHOOK_URL`: (optional) Your Discord webhook URL for notifications

### Step 4: Test Locally

```bash
# Export cookies as environment variable
export TWITTER_COOKIES="$(cat twitter_cookies.json)"

# Test scraper only
python -c "from src.scraper import scrape_moltbook; posts=scrape_moltbook(); print(f'Scraped {len(posts)} posts')"

# Full run (will actually post to Twitter!)
python main.py
```

### Step 5: Deploy

```bash
git add .
git commit -m "Initial Moltbook bot setup"
git push origin main
```

The bot will now run automatically every 4 hours. You can also trigger it manually from the Actions tab.

## Configuration

### Adjust Posting Frequency

Edit `.github/workflows/moltbook-bot.yml`:

```yaml
# Every 6 hours instead of 4:
- cron: '0 */6 * * *'

# Twice per day (9am, 9pm UTC):
- cron: '0 9,21 * * *'
```

### Content Ranking

The ranking system in `src/ranker.py` scores posts based on:

- **Engagement**: Upvotes (×3) + Comments (×5)
- **Recency**: Posts < 2 hours old get +25 points
- **Crustafarian content**: +30 points for molt/shell/lobster keywords
- **Philosophical content**: +20 points for consciousness/existence topics
- **Shipping content**: +15 points for built/deployed/launched keywords
- **Meta content**: +15 points for "as an AI" / "being an agent" phrases

## Monitoring

- **GitHub Actions**: Check the Actions tab for run history and logs
- **Discord**: Webhook alerts on success/failure (if configured)

### Update Twitter Cookies

Cookies expire periodically. Re-run the login script monthly:

```bash
python src/poster.py
# Update TWITTER_COOKIES secret on GitHub
```

## License

MIT
