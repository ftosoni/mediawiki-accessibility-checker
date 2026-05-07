#!/bin/bash
# MediaWiki Accessibility Checker - Toolforge Startup Script with Library Patching

export HOME=/data/project/accessibility-checker
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
export PATH=$HOME/.local/bin:$PATH
export PROJECT_DIR=$(pwd)

# Create a local directory for missing system libraries
mkdir -p $HOME/lib/apt/lists
mkdir -p $HOME/lib/apt/archives
mkdir -p $HOME/lib/usr/lib/x86_64-linux-gnu

# 2. THE LIBRARY HACK: Use a local APT config to download missing libs
if [ ! -f "$HOME/lib/usr/lib/x86_64-linux-gnu/libatk-1.0.so.0" ]; then
    echo "--- Patching missing system libraries (first run only) ---"
    
    # Create a local sources.list
    echo "deb http://archive.ubuntu.com/ubuntu/ noble main universe" > $HOME/lib/sources.list
    
    # Create a local apt.conf to work without sudo
    cat > $HOME/lib/apt.conf <<EOF
Dir "$HOME/lib";
Dir::State::status "$HOME/lib/status";
EOF
    touch $HOME/lib/status

    # Update local cache and download
    apt-get -c $HOME/lib/apt.conf -o Dir::Etc::SourceList=$HOME/lib/sources.list update
    
    cd $HOME/lib
    # Download the required libraries (Noble names use t64 suffix for many)
    apt-get -c $HOME/lib/apt.conf -o Dir::Etc::SourceList=$HOME/lib/sources.list download \
        libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 \
        libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2t64
    
    # Extract them
    echo "Extracting libraries..."
    for deb in *.deb; do dpkg -x $deb . ; done
    rm *.deb
    cd $PROJECT_DIR
fi

# Point the system to our local libraries
# We include multiple possible paths where the .so files might have landed
export LD_LIBRARY_PATH=$HOME/lib/usr/lib/x86_64-linux-gnu:$HOME/lib/lib/x86_64-linux-gnu:$HOME/lib/usr/lib:$LD_LIBRARY_PATH

echo "--- Starting Application ---"

# 3. Check and Install Playwright browsers
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "Installing Playwright Chromium..."
    python3 -m playwright install chromium
fi

# 4. Launch
echo "Launching Gunicorn..."
gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers=1 --timeout 600 --bind 0.0.0.0:${PORT:-8000} --access-logfile -
