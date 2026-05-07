#!/bin/bash
# MediaWiki Accessibility Checker - Toolforge Startup Script

# 1. Setup Environment
export HOME=/data/project/accessibility-checker
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
export PATH=$HOME/.local/bin:$PATH

# Create a local directory for missing system libraries
mkdir -p $HOME/lib

# 2. THE LIBRARY HACK: Download missing libs if they aren't there
# This solves the 'libatk-1.0.so.0' and other missing library errors
if [ ! -f "$HOME/lib/usr/lib/x86_64-linux-gnu/libatk-1.0.so.0" ]; then
    echo "--- Patching missing system libraries (first run only) ---"
    cd $HOME/lib
    # Download the debian packages (does not need sudo)
    apt-get download libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
    # Extract them
    for deb in *.deb; do dpkg-x $deb . ; done
    rm *.deb
    cd $HOME/mediawiki-accessibility-checker
fi

# Point the system to our local libraries
export LD_LIBRARY_PATH=$HOME/lib/usr/lib/x86_64-linux-gnu:$HOME/lib/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

echo "--- Starting Application ---"

# 3. Check and Install Playwright browsers
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "Installing Playwright Chromium..."
    python3 -m playwright install chromium
fi

# 4. Launch exactly like your working project
echo "Launching Gunicorn..."
gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers=1 --timeout 600 --bind 0.0.0.0:${PORT:-8000} --access-logfile -
