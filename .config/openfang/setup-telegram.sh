#!/bin/bash
# Telegram Bot Setup for OpenFang

if [ -z "$1" ]; then
    echo "Usage: setup-telegram.sh <BOT_TOKEN>"
    echo "Get your bot token from @BotFather on Telegram"
    exit 1
fi

BOT_TOKEN="$1"
CONFIG_FILE="$HOME/.config/openfang/config.toml"

echo "Configuring Telegram bot..."

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: OpenFang config not found at $CONFIG_FILE"
    exit 1
fi

# Backup original config
cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%s)"

# Update Telegram configuration
sed -i '/^\[channels\]/,/^\[/{
    s/^# telegram = { bot_token = "YOUR_BOT_TOKEN"/telegram = { bot_token = "'"$BOT_TOKEN"'"/
}' "$CONFIG_FILE"

# If the line doesn't exist, add it
if ! grep -q "telegram = { bot_token = \"$BOT_TOKEN\"" "$CONFIG_FILE"; then
    # Remove the commented line and add the real one
    sed -i '/^# telegram = { bot_token = "YOUR_BOT_TOKEN"/d' "$CONFIG_FILE"
    sed -i '/^# Format: telegram = { bot_token/a telegram = { bot_token = "'"$BOT_TOKEN"'", allowed_users = [] }' "$CONFIG_FILE"
fi

echo "Telegram bot configured!"
echo ""
echo "To complete setup:"
echo "1. Message your bot on Telegram to start a chat"
echo "2. Restart OpenFang: systemctl --user restart openfang"
echo "3. Check status: systemctl --user status openfang"
echo ""
echo "Your bot is ready at: https://t.me/$(echo $BOT_TOKEN | cut -d: -f1)"
