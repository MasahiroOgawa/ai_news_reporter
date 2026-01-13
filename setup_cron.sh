#!/bin/bash
# AI News Reporter - Cron Setup Script
# Reads schedule settings from config.yaml

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv"
AI_NEWS_CMD="$VENV_PATH/bin/ai-news"
CONFIG_FILE="$SCRIPT_DIR/config.yaml"
LOG_FILE="$SCRIPT_DIR/cron.log"

echo "==================================="
echo "AI News Reporter - Cron Setup"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -f "$AI_NEWS_CMD" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv "$VENV_PATH"
    "$VENV_PATH/bin/pip" install -e "$SCRIPT_DIR"
    echo "Virtual environment created."
fi

# Check if .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo ""
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and add your API keys:"
    echo "  cp $SCRIPT_DIR/.env.example $SCRIPT_DIR/.env"
    echo "  nano $SCRIPT_DIR/.env"
    exit 1
fi

# Check if config.yaml exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo ""
    echo "ERROR: config.yaml not found!"
    echo "Please copy config.example.yaml to config.yaml and customize:"
    echo "  cp $SCRIPT_DIR/config.example.yaml $SCRIPT_DIR/config.yaml"
    echo "  nano $SCRIPT_DIR/config.yaml"
    exit 1
fi

# Validate configuration
echo "Validating configuration..."
"$AI_NEWS_CMD" validate
echo ""

# Parse schedule settings from config.yaml
SCHEDULE_TYPE=$(grep -A10 "^schedule:" "$CONFIG_FILE" | grep "type:" | head -1 | sed 's/.*type:[[:space:]]*"\?\([^"]*\)"\?.*/\1/' | tr -d ' ')
SCHEDULE_DAY=$(grep -A10 "^schedule:" "$CONFIG_FILE" | grep "day_of_week:" | head -1 | sed 's/.*day_of_week:[[:space:]]*"\?\([^"]*\)"\?.*/\1/' | tr -d ' ')
SCHEDULE_TIME=$(grep -A10 "^schedule:" "$CONFIG_FILE" | grep "time:" | head -1 | sed 's/.*time:[[:space:]]*"\?\([^"]*\)"\?.*/\1/' | tr -d ' ')

# Default values
SCHEDULE_TYPE=${SCHEDULE_TYPE:-weekly}
SCHEDULE_DAY=${SCHEDULE_DAY:-monday}
SCHEDULE_TIME=${SCHEDULE_TIME:-09:00}

# Parse time to hour and minute
HOUR=$(echo "$SCHEDULE_TIME" | cut -d: -f1)
MINUTE=$(echo "$SCHEDULE_TIME" | cut -d: -f2)

# Convert day name to cron day number (0=Sunday, 1=Monday, ..., 6=Saturday)
case "$SCHEDULE_DAY" in
    sunday)    DAY_NUM=0 ;;
    monday)    DAY_NUM=1 ;;
    tuesday)   DAY_NUM=2 ;;
    wednesday) DAY_NUM=3 ;;
    thursday)  DAY_NUM=4 ;;
    friday)    DAY_NUM=5 ;;
    saturday)  DAY_NUM=6 ;;
    *)         DAY_NUM=1 ;;
esac

# Build cron schedule
if [ "$SCHEDULE_TYPE" = "daily" ]; then
    CRON_SCHEDULE="$MINUTE $HOUR * * *"
    SCHEDULE_DESC="Daily at $SCHEDULE_TIME"
else
    CRON_SCHEDULE="$MINUTE $HOUR * * $DAY_NUM"
    SCHEDULE_DESC="Weekly on $SCHEDULE_DAY at $SCHEDULE_TIME"
fi

# Create cron entry
CRON_ENTRY="$CRON_SCHEDULE cd $SCRIPT_DIR && $AI_NEWS_CMD run >> $LOG_FILE 2>&1"

echo "==================================="
echo "Schedule from config.yaml"
echo "==================================="
echo "Type: $SCHEDULE_TYPE"
echo "Day: $SCHEDULE_DAY"
echo "Time: $SCHEDULE_TIME"
echo ""
echo "Cron schedule: $SCHEDULE_DESC"
echo ""
echo "Cron entry:"
echo "$CRON_ENTRY"
echo ""

read -p "Add this to your crontab? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    # Remove existing ai-news entries and add new one
    (crontab -l 2>/dev/null | grep -v "ai-news run" || true; echo "$CRON_ENTRY") | crontab -
    echo ""
    echo "Cron job added successfully!"
    echo ""
    echo "To verify: crontab -l"
    echo "To view logs: tail -f $LOG_FILE"
else
    echo ""
    echo "Cron job not added."
fi

echo ""
echo "Setup complete!"
