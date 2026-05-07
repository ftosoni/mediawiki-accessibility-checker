#!/bin/bash
# MediaWiki Accessibility Checker - Toolforge Startup Script (Ubuntu 24.04 Noble Edition)

export HOME=/data/project/accessibility-checker
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
export PATH=$HOME/.local/bin:$PATH
export PROJECT_DIR=$(pwd)

echo "--- Toolforge Startup Initiated ---"

# 1. Setup local APT sandbox
mkdir -p $HOME/lib/apt/lists
mkdir -p $HOME/lib/apt/archives
mkdir -p $HOME/lib/status_dir
touch $HOME/lib/status_dir/status

# Create local sources.list pointing to Ubuntu Noble (24.04)
echo "deb http://archive.ubuntu.com/ubuntu/ noble main universe" > $HOME/lib/sources.list

# Create local apt.conf
cat > $HOME/lib/apt.conf <<EOF
Dir "$HOME/lib";
Dir::State::status "$HOME/lib/status_dir/status";
EOF

# 2. Force download missing Noble libraries
echo "--- Patching missing system libraries (Ubuntu 24.04) ---"
apt-get -c $HOME/lib/apt.conf -o Dir::Etc::SourceList=$HOME/lib/sources.list update

cd $HOME/lib
# Noble Numbat uses t64 suffixes for many core libraries
apt-get -c $HOME/lib/apt.conf -o Dir::Etc::SourceList=$HOME/lib/sources.list download \
    libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2t64

echo "Extracting .deb packages..."
for deb in *.deb; do 
    echo "Processing $deb..."
    dpkg -x "$deb" . 
done
rm -f *.deb

# 3. Set Library Paths
# We add all possible locations where the .so files might be
export LD_LIBRARY_PATH=$HOME/lib/usr/lib/x86_64-linux-gnu:$HOME/lib/lib/x86_64-linux-gnu:$HOME/lib/usr/lib:$LD_LIBRARY_PATH
echo "LD_LIBRARY_PATH is now: $LD_LIBRARY_PATH"

# Verify extraction
echo "Contents of local lib folder:"
find $HOME/lib/usr/lib/x86_64-linux-gnu -name "*.so*" 2>/dev/null | head -n 5

cd $PROJECT_DIR

# 4. Check/Install Playwright browsers
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "Installing Playwright Chromium..."
    python3 -m playwright install chromium
fi

# 5. Launch Gunicorn
echo "--- Launching Gunicorn ---"
gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers=1 --timeout 600 --bind 0.0.0.0:${PORT:-8000} --access-logfile -
