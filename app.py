import os
import subprocess
import sys
import time

# 1. Setup Environment
os.chdir("/data/project/accessibility-checker/www/python/src")

HOME = "/data/project/accessibility-checker"
os.environ["HOME"] = HOME
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = f"{HOME}/.cache/ms-playwright"

# 2. Find the REAL Python
# We check common Toolforge/Buildpack locations
POSSIBLE_PYTHONS = [
    "/usr/bin/python3",
    "/usr/bin/python",
    # Heroku/Buildpack locations
    "/layers/heroku_python/venv/bin/python",
    "/workspace/venv/bin/python",
    # Local user location
    f"{HOME}/.local/bin/python3",
    sys.executable # Last resort
]

PYTHON_BIN = None
for p in POSSIBLE_PYTHONS:
    try:
        # Check if this python has pip
        result = subprocess.run([p, "-m", "pip", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            PYTHON_BIN = p
            print(f"--- Found working Python: {p} ---", flush=True)
            break
    except:
        continue

if not PYTHON_BIN:
    print("--- WARNING: No Python with 'pip' found. Falling back to sys.executable ---", flush=True)
    PYTHON_BIN = sys.executable

def setup():
    print("--- Checking Dependencies ---", flush=True)
    try:
        # Try to install/verify requirements
        subprocess.run([PYTHON_BIN, "-m", "pip", "install", "-r", "requirements.txt", "--user"], check=False)
        
        # Install browsers
        browser_path = os.path.join(os.environ["PLAYWRIGHT_BROWSERS_PATH"], "chromium")
        if not os.path.exists(browser_path):
            print("--- Installing Playwright Chromium ---", flush=True)
            subprocess.run([PYTHON_BIN, "-m", "playwright", "install", "chromium"], check=False)
    except Exception as e:
        print(f"Setup error: {e}", flush=True)

# 3. The Hijacker
if os.environ.get('HIJACKED') != 'true':
    os.environ['HIJACKED'] = 'true'
    setup()
    
    port = os.environ.get("PORT", "8000")
    print(f"--- Launching Gunicorn via {PYTHON_BIN} on port {port} ---", flush=True)
    sys.stdout.flush()
    time.sleep(1)
    
    # Re-exec using the found Python
    os.execvp(
        PYTHON_BIN, 
        [
            PYTHON_BIN,
            "-m", "gunicorn", 
            "backend.main:app", 
            "-k", "uvicorn.workers.UvicornWorker", 
            "--workers", "1", 
            "--timeout", "600", 
            "--bind", f"0.0.0.0:{port}"
        ]
    )

# 4. Fallback App
def app(environ, start_response):
    start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
    return [b"Hijack failed. Check uwsgi.log for details."]
