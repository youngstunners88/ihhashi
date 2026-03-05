#!/bin/bash
# OpenFang Startup Script with PinchTab Integration

export HOME="/home/teacherchris37"
export PATH="$HOME/.openfang/bin:$HOME/.local/bin:$HOME/.nvm/versions/node/v20.20.0/bin:/usr/local/bin:/usr/bin:/bin"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Add custom tools to PATH
export PATH="$HOME/.config/openfang/tools:$PATH"

# Ensure directories exist
mkdir -p ~/.config/openfang/logs
mkdir -p ~/.config/openfang/data

echo "Starting OpenFang with PinchTab integration..."
echo "Groq API configured: llama-3.3-70b-versatile"
echo "Tools available: pinchtab-tool, shell, http, browser"

# Start OpenFang
exec openfang start "$@"
