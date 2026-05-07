#!/bin/bash
# MediaWiki Accessibility Checker - Zero-Dependency Bootstrap Script

export HOME=/data/project/accessibility-checker
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
export PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH

echo "--- Toolforge Bootstrap Starting ---"

# 1. Bootstrap Pip if missing
if ! python3 -m pip --version > /dev/null 2>&1; then
    echo "Pip not found. Bootstrapping..."
    curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# 2. Install/Update Dependencies
echo "Installing/Updating requirements..."
python3 -m pip install --upgrade pip --user
python3 -m pip install -r requirements.txt --user

# 3. Check and Install Playwright browsers
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "Installing Playwright Chromium (this will take a moment)..."
    python3 -m playwright install chromium
fi

# 4. Start the application
echo "--- Launching Gunicorn ---"
python3 -m gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers=1 --timeout 600 --bind 0.0.0.0:${PORT:-8000}
