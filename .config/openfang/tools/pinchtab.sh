#!/bin/bash
# PinchTab Tool for OpenFang
# Provides browser automation capabilities

PINCHTAB_PORT=9867
PINCHTAB_HOST="localhost"

# Start PinchTab if not running
ensure_pinchtab() {
    if ! curl -s "http://${PINCHTAB_HOST}:${PINCHTAB_PORT}/health" > /dev/null 2>&1; then
        echo "Starting PinchTab server..."
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        nohup pinchtab > ~/.config/openfang/pinchtab.log 2>&1 &
        sleep 3
    fi
}

# Create a new browser instance
create_instance() {
    local profile="${1:-default}"
    curl -s -X POST "http://${PINCHTAB_HOST}:${PINCHTAB_PORT}/instances" \
        -H "Content-Type: application/json" \
        -d "{\"profile\":\"${profile}\"}" | jq -r '.id'
}

# Navigate to URL
navigate() {
    local tab_id="$1"
    local url="$2"
    curl -s -X POST "http://${PINCHTAB_HOST}:${PINCHTAB_PORT}/instances/${tab_id}/navigate" \
        -H "Content-Type: application/json" \
        -d "{\"url\":\"${url}\"}"
}

# Get page snapshot (interactive elements)
snapshot() {
    local tab_id="$1"
    curl -s "http://${PINCHTAB_HOST}:${PINCHTAB_PORT}/instances/${tab_id}/snapshot?filter=interactive"
}

# Click element
click() {
    local tab_id="$1"
    local ref="$2"
    curl -s -X POST "http://${PINCHTAB_HOST}:${PINCHTAB_PORT}/instances/${tab_id}/action" \
        -H "Content-Type: application/json" \
        -d "{\"kind\":\"click\",\"ref\":\"${ref}\"}"
}

# Fill input
fill() {
    local tab_id="$1"
    local ref="$2"
    local text="$3"
    curl -s -X POST "http://${PINCHTAB_HOST}:${PINCHTAB_PORT}/instances/${tab_id}/action" \
        -H "Content-Type: application/json" \
        -d "{\"kind\":\"fill\",\"ref\":\"${ref}\",\"value\":\"${text}\"}"
}

# Extract text
extract_text() {
    local tab_id="$1"
    curl -s "http://${PINCHTAB_HOST}:${PINCHTAB_PORT}/instances/${tab_id}/text"
}

# Close instance
close_instance() {
    local tab_id="$1"
    curl -s -X DELETE "http://${PINCHTAB_HOST}:${PINCHTAB_PORT}/instances/${tab_id}"
}

# Main command handler
case "$1" in
    start)
        ensure_pinchtab
        echo "PinchTab is running on port ${PINCHTAB_PORT}"
        ;;
    create)
        ensure_pinchtab
        create_instance "$2"
        ;;
    nav)
        ensure_pinchtab
        tab_id="$2"
        url="$3"
        navigate "$tab_id" "$url"
        ;;
    snap)
        ensure_pinchtab
        tab_id="$2"
        snapshot "$tab_id"
        ;;
    click)
        ensure_pinchtab
        tab_id="$2"
        ref="$3"
        click "$tab_id" "$ref"
        ;;
    fill)
        ensure_pinchtab
        tab_id="$2"
        ref="$3"
        text="$4"
        fill "$tab_id" "$ref" "$text"
        ;;
    text)
        ensure_pinchtab
        tab_id="$2"
        extract_text "$tab_id"
        ;;
    close)
        ensure_pinchtab
        tab_id="$2"
        close_instance "$tab_id"
        ;;
    search)
        # Quick search helper
        ensure_pinchtab
        query="$2"
        tab_id=$(create_instance "search")
        navigate "$tab_id" "https://www.google.com/search?q=${query// /+}"
        sleep 2
        extract_text "$tab_id"
        close_instance "$tab_id"
        ;;
    *)
        echo "PinchTab Tool for OpenFang"
        echo "Usage: pinchtab-tool <command> [args]"
        echo ""
        echo "Commands:"
        echo "  start              - Start PinchTab server"
        echo "  create [profile]   - Create new browser instance"
        echo "  nav <id> <url>     - Navigate to URL"
        echo "  snap <id>          - Get page snapshot with interactive elements"
        echo "  click <id> <ref>   - Click element by reference"
        echo "  fill <id> <ref> <text> - Fill input field"
        echo "  text <id>          - Extract page text"
        echo "  close <id>         - Close browser instance"
        echo "  search <query>     - Quick Google search"
        ;;
esac
