# AI News Reporter

Automated AI news collection and reporting system. Collects news from web scraping and Tavily search API, summarizes with LLM (Claude or OpenAI), and delivers weekly reports via email, Slack, or file output.

## Features

- **Multi-source collection**: Tavily search API + configurable web scraping
- **Switchable LLM**: Claude (default) or OpenAI for summarization
- **Multiple delivery methods**: Email (SMTP), Slack webhook, File (Markdown/HTML/JSON)
- **Scheduled reports**: Cron-style scheduling with APScheduler
- **Deduplication**: Removes duplicate articles by URL and title similarity
- **Configurable**: YAML config for keywords, sites, and delivery options

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone and enter directory
cd ai_news_reporter

# Install dependencies
uv sync

# Copy configuration files
cp .env.example .env
cp config.example.yaml config.yaml
```

## Quick Start (Minimal Setup)

For a minimal setup with file output only, you need just 2 API keys:

### 1. Get Tavily API Key (News Search)

1. Go to [tavily.com](https://tavily.com/)
2. Sign up and get your API key
3. Add to `.env`:
   ```bash
   TAVILY_API_KEY=tvly-xxxxx
   ```

### 2. Get LLM API Key

**Option A: OpenAI**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create an API key
3. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-xxxxx
   ```
4. Set provider in `config.yaml`:
   ```yaml
   llm:
     provider: "openai"
   ```

**Option B: Claude (Anthropic)**
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create an API key
3. Add to `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
   ```
4. Set provider in `config.yaml` (this is the default):
   ```yaml
   llm:
     provider: "claude"
   ```

### 3. Run Your First Report

```bash
# Validate configuration
uv run ai-news validate

# Generate report
uv run ai-news run
```

Reports are saved to `./reports/` folder in Markdown, HTML, and JSON formats.

## Optional: Email Delivery Setup

To receive reports via email (Gmail example):

### 1. Enable Gmail App Password

1. Enable 2-Factor Authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Select app: "Mail", Select device: "Other" (enter "AI News Reporter")
4. Click "Generate" and copy the 16-character password

### 2. Configure .env

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App password, NOT your Gmail password
```

### 3. Enable in config.yaml

```yaml
delivery:
  email:
    enabled: true
    recipients:
      - "recipient@example.com"
    subject_prefix: "[AI News Weekly]"
```

## Optional: Slack Delivery Setup

To receive reports in Slack:

### 1. Create Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** > **From scratch**
3. Name: "AI News Reporter", select your workspace

### 2. Enable Incoming Webhooks

1. In the left sidebar, find **Features** section
2. Click **Incoming Webhooks**
3. Toggle the switch to **On**
4. Click **Add New Webhook to Workspace**
5. Select the channel to post to (e.g., `#ai-news`)
6. Copy the webhook URL

> **Note**: You may need workspace admin approval for this step.

### 3. Configure .env

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXX
```

### 4. Enable in config.yaml

```yaml
delivery:
  slack:
    enabled: true
```

## Configuration Reference

### Environment Variables (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `TAVILY_API_KEY` | Yes | Tavily API key for news search |
| `ANTHROPIC_API_KEY` | If using Claude | Anthropic API key |
| `OPENAI_API_KEY` | If using OpenAI | OpenAI API key |
| `SMTP_HOST` | If using email | SMTP server (e.g., `smtp.gmail.com`) |
| `SMTP_PORT` | If using email | SMTP port (e.g., `587`) |
| `SMTP_USER` | If using email | SMTP username/email |
| `SMTP_PASSWORD` | If using email | SMTP password or app password |
| `SLACK_WEBHOOK_URL` | If using Slack | Slack incoming webhook URL |

### Application Config (config.yaml)

```yaml
# Keywords to search
keywords:
  - "artificial intelligence"
  - "large language models"

# Sites to scrape
sites:
  - name: "TechCrunch AI"
    url: "https://techcrunch.com/category/artificial-intelligence/"
    enabled: true
    selectors:
      article: "article"
      title: "h2 a"

# Search settings
search:
  enabled: true
  time_range: "week"
  max_results_per_keyword: 10

# Schedule settings
schedule:
  enabled: true
  type: "weekly"
  day_of_week: "monday"
  time: "09:00"
  timezone: "Asia/Tokyo"

# Delivery methods
delivery:
  file:
    enabled: true
    output_dir: "./reports"
    formats: ["markdown", "html", "json"]
  email:
    enabled: false
    recipients: ["user@example.com"]
  slack:
    enabled: false
```

## Usage

### Run Report Manually

```bash
uv run ai-news run
```

### Validate Configuration

```bash
uv run ai-news validate
```

### Custom Config Path

```bash
uv run ai-news run --config /path/to/config.yaml
```

## Automated Weekly Reports (Cron Setup)

To receive reports automatically every week without manual commands:

### Setup Steps

1. Edit `config.yaml` - set your schedule:
   ```yaml
   schedule:
     enabled: true
     type: "weekly"           # daily or weekly
     day_of_week: "monday"    # for weekly
     time: "09:00"            # 24-hour format
     timezone: "Asia/Tokyo"
   ```

2. Run the setup script:
   ```bash
   ./setup_cron.sh
   ```

The script reads schedule settings from `config.yaml` and sets up cron automatically.

### Manual Setup

If you prefer to set up cron manually:

```bash
# Open crontab editor
crontab -e

# Add this line for weekly Monday 9:00 AM reports:
0 9 * * 1 cd /path/to/ai_news_reporter && .venv/bin/ai-news run >> cron.log 2>&1
```

Cron schedule format: `minute hour day-of-month month day-of-week`
- `0 9 * * 1` = Monday 9:00 AM
- `0 9 * * 5` = Friday 9:00 AM
- `0 9 * * *` = Daily 9:00 AM

### Check Cron Status

```bash
# View current cron jobs
crontab -l

# View logs
tail -f cron.log
```

### Remove Cron Job

```bash
crontab -e
# Delete the ai-news line and save
```

## Project Structure

```
ai_news_reporter/
├── src/ai_news_reporter/
│   ├── main.py           # CLI entry point
│   ├── core/             # Config and exceptions
│   ├── collectors/       # Tavily + web scraper
│   ├── llm/              # Claude + OpenAI + factory
│   ├── processors/       # Summarizer + deduplicator
│   ├── delivery/         # File, email, Slack
│   ├── scheduler/        # APScheduler cron
│   └── models/           # Article, Report
├── config.yaml           # User config
├── .env                  # API keys
└── reports/              # Generated reports
```

## License

MIT
