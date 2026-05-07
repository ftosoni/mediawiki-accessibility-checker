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

# Create local sources.list with [trusted=yes]
cat > $APT_DIR/etc/apt/sources.list <<EOF
deb [trusted=yes] http://archive.ubuntu.com/ubuntu/ noble main universe
deb [trusted=yes] http://archive.ubuntu.com/ubuntu/ noble-updates main universe
deb [trusted=yes] http://archive.ubuntu.com/ubuntu/ noble-security main universe
EOF

# Create a robust local apt.conf
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
if [ ! -f "$HOME/lib/usr/lib/x86_64-linux-gnu/libatspi.so.0" ]; then
    echo "--- Patching missing system libraries (Ubuntu 24.04 Noble) ---"
    
    # Update local cache
    apt-get -c $APT_DIR/etc/apt/apt.conf update --allow-insecure-repositories --allow-unauthenticated
    
    cd $HOME/lib
    # Download main batch
    apt-get -c $APT_DIR/etc/apt/apt.conf download --allow-unauthenticated \
        libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 \
        libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
        libasound2t64 libxfixes3 libxext6 libxrender1 libx11-6 libx11-xcb1 libxcb1 \
        libdbus-1-3 libnspr4 libnss3 libfontconfig1 libfreetype6 libglib2.0-0t64 \
        libxshmfence1 libxxf86vm1 libsecret-1-0 libwayland-client0 libwayland-server0 \
        libgles2 libegl1 libvulkan1 libpci3 libdbus-glib-1-2 libatspi2.0-0t64 || true
    
    # DIRECT CRAWLER FOR LIBATSPI: Search the pool directory directly
    echo "Crawling Ubuntu pool for libatspi..."
    python3 - <<EOF
import urllib.request
import re
import os

pools = [
    "http://archive.ubuntu.com/ubuntu/pool/main/a/at-spi2-core/",
    "http://archive.ubuntu.com/ubuntu/pool/main/a/at-spi2-atk/",
]
found = False
for base_url in pools:
    try:
        print(f"Checking {base_url}...")
        req = urllib.request.Request(base_url, headers={'User-Agent': 'https://accessibility-checker.toolforge.org (contact: https://meta.wikimedia.org/wiki/User_talk:Super_nabla)'})
        response = urllib.request.urlopen(req).read().decode('utf-8')
        links = re.findall(r'href="(libatspi[^"]+?_amd64\.deb)"', response)
        if links:
            latest = sorted(links)[-1]
            print(f"Found match: {latest}")
            req = urllib.request.Request(base_url + latest, headers={'User-Agent': 'https://accessibility-checker.toolforge.org (contact: https://meta.wikimedia.org/wiki/User_talk:Super_nabla)'})
            with urllib.request.urlopen(req) as resp, open("libatspi_crawled.deb", 'wb') as out:
                out.write(resp.read())
            print("Download successful.")
            found = True
            break
    except Exception as e:
        print(f"Crawler failed for {base_url}: {e}")

if not found:
    print("CRITICAL: Could not find libatspi in any pool!")
EOF

    echo "Extracting .deb packages..."
    for deb in *.deb; do 
        [ -f "$deb" ] || continue
        if [ $(stat -c%s "$deb") -lt 2000 ]; then
            rm -f "$deb"
            continue
        fi
        echo "Processing $deb..."
        dpkg -x "$deb" . 
    done
    rm -f *.deb
fi

# 3. Set Library Paths
export LD_LIBRARY_PATH=$HOME/lib/usr/lib/x86_64-linux-gnu:$HOME/lib/lib/x86_64-linux-gnu:$HOME/lib/usr/lib:$LD_LIBRARY_PATH

# MOLE HUNTER: Diagnostics
echo "--- Mole Hunter Diagnostics ---"
BROWSER_BIN=$(find $PLAYWRIGHT_BROWSERS_PATH -name "chrome-headless-shell" | head -n 1)
if [ -n "$BROWSER_BIN" ]; then
    echo "Checking dependencies for: $BROWSER_BIN"
    ldd "$BROWSER_BIN" | grep "not found" || echo "All dependencies found!"
fi

# 4. Check/Install Playwright browsers
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "Installing Playwright Chromium..."
    python3 -m playwright install chromium
fi

cd $PROJECT_DIR

# 5. Launch Gunicorn
echo "--- Launching Gunicorn ---"
gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers=1 --timeout 600 --bind 0.0.0.0:${PORT:-8000} --access-logfile -
