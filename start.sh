#!/bin/bash
# MediaWiki Accessibility Checker - Toolforge Startup Script

# 1. Force the home directory and playwright paths
export HOME=/data/project/accessibility-checker
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright

echo "--- Starting MediaWiki Accessibility Checker ---"
echo "Environment: HOME=$HOME"

# 2. Setup/Update requirements if needed (Optional, but safe)
# pip install -r requirements.txt --user

# 3. Check and Install Playwright browsers if missing
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "Installing Playwright Chromium (this may take a minute)..."
    python3 -m playwright install chromium
fi

# 4. Start the application
echo "Launching Gunicorn..."
gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers=1 --timeout 600 --bind 0.0.0.0
