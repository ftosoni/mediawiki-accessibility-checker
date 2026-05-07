import os
import subprocess
import sys
import time

# 1. Setup Environment
HOME = "/data/project/accessibility-checker"
os.environ["HOME"] = HOME
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = f"{HOME}/.cache/ms-playwright"
os.environ["PATH"] = f"{HOME}/.local/bin:{os.environ.get('PATH', '')}"

# 2. Install/Check Browsers (only on first run)
browser_path = os.path.join(os.environ["PLAYWRIGHT_BROWSERS_PATH"], "chromium")
if not os.path.exists(browser_path):
    print("--- First Run: Installing Playwright Browsers ---")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])

# 3. Hijack the Process
# Toolforge provides the PORT via environment variable
port = os.environ.get("PORT", "8000")

print(f"--- Hijacking uWSGI and Launching Gunicorn on port {port} ---")
sys.stdout.flush()

# This replaces the current uWSGI process with Gunicorn
os.execvp(
    "gunicorn", 
    [
        "gunicorn", 
        "backend.main:app", 
        "-k", "uvicorn.workers.UvicornWorker", 
        "--workers", "1", 
        "--timeout", "600", 
        "--bind", f"0.0.0.0:{port}"
    ]
)
