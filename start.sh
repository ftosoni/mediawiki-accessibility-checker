#!/bin/bash
# MediaWiki Accessibility Checker - Toolforge Startup Script (Ubuntu 24.04 Noble Edition)

export HOME=/data/project/accessibility-checker
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
export PATH=$HOME/.local/bin:$PATH
export PROJECT_DIR=$(pwd)

echo "--- Toolforge Startup Initiated ---"

# 1. Setup FULL local APT sandbox structure
APT_DIR=$HOME/lib/apt_sandbox
mkdir -p $APT_DIR/etc/apt/preferences.d
mkdir -p $APT_DIR/etc/apt/sources.list.d
mkdir -p $APT_DIR/var/lib/apt/lists/partial
mkdir -p $APT_DIR/var/cache/apt/archives/partial
mkdir -p $APT_DIR/var/lib/dpkg
touch $APT_DIR/var/lib/dpkg/status

# Create local sources.list
echo "deb http://archive.ubuntu.com/ubuntu/ noble main universe" > $APT_DIR/etc/apt/sources.list

# Create a robust local apt.conf that overrides ALL paths and security
cat > $APT_DIR/etc/apt/apt.conf <<EOF
Dir "$APT_DIR";
Dir::State "$APT_DIR/var/lib/apt";
Dir::State::status "$APT_DIR/var/lib/dpkg/status";
Dir::Cache "$APT_DIR/var/cache/apt";
Dir::Etc "$APT_DIR/etc/apt";
Acquire::AllowInsecureRepositories "true";
Acquire::AllowDowngradeToInsecureRepositories "true";
APT::Get::AllowUnauthenticated "true";
EOF

# 2. Patch missing Noble libraries
# We check for libXfixes.so.3 to ensure we pick up the latest additions
if [ ! -f "$HOME/lib/usr/lib/x86_64-linux-gnu/libXfixes.so.3" ]; then
    echo "--- Patching missing system libraries (Ubuntu 24.04 Noble) ---"
    
    # Update local cache
    apt-get -c $APT_DIR/etc/apt/apt.conf update --allow-insecure-repositories
    
    cd $HOME/lib
    # Expanded list of Playwright dependencies for Noble
    apt-get -c $APT_DIR/etc/apt/apt.conf download --allow-unauthenticated \
        libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 \
        libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
        libasound2t64 libxfixes3 libxext6 libxrender1 libx11-6 libx11-xcb1 libxcb1 libdbus-1-3
    
    echo "Extracting .deb packages..."
    for deb in *.deb; do 
        [ -f "$deb" ] || continue
        echo "Processing $deb..."
        dpkg -x "$deb" . 
    done
    rm -f *.deb
fi

# 3. Set Library Paths
export LD_LIBRARY_PATH=$HOME/lib/usr/lib/x86_64-linux-gnu:$HOME/lib/lib/x86_64-linux-gnu:$HOME/lib/usr/lib:$LD_LIBRARY_PATH
echo "LD_LIBRARY_PATH is active."

# 4. Check/Install Playwright browsers
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "Installing Playwright Chromium..."
    python3 -m playwright install chromium
fi

cd $PROJECT_DIR

# 5. Launch Gunicorn
echo "--- Launching Gunicorn ---"
gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers=1 --timeout 600 --bind 0.0.0.0:${PORT:-8000} --access-logfile -
