import os
import subprocess
import sys
import time

# 1. Setup Environment
# Ensure we are in the right directory
os.chdir("/data/project/accessibility-checker/www/python/src")

HOME = "/data/project/accessibility-checker"
os.environ["HOME"] = HOME
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = f"{HOME}/.cache/ms-playwright"
os.environ["PATH"] = f"{HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin:{os.environ.get('PATH', '')}"

def setup():
    # 2. Ensure dependencies and browsers are present
    try:
        # Install requirements if not already there
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--user"], check=False)
        
        # Install browsers
        browser_path = os.path.join(os.environ["PLAYWRIGHT_BROWSERS_PATH"], "chromium")
        if not os.path.exists(browser_path):
            print("--- Installing Playwright Browsers ---")
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
    except Exception as e:
        print(f"Setup error: {e}")

# 3. The Hijacker
# We run this immediately on import
if os.environ.get('HIJACKED') != 'true':
    os.environ['HIJACKED'] = 'true'
    setup()
    
    port = os.environ.get("PORT", "8000")
    print(f"--- Hijacking uWSGI -> Gunicorn on {port} ---")
    sys.stdout.flush()
    time.sleep(1) # Give logs a moment to catch up
    
    # Use full path to gunicorn if possible
    gunicorn_bin = os.path.expanduser("~/.local/bin/gunicorn")
    if not os.path.exists(gunicorn_bin):
        gunicorn_bin = "gunicorn"

    os.execvp(
        gunicorn_bin, 
        [
            "gunicorn", 
            "backend.main:app", 
            "-k", "uvicorn.workers.UvicornWorker", 
            "--workers", "1", 
            "--timeout", "600", 
            "--bind", f"0.0.0.0:{port}"
        ]
    )

# 4. Dummy app for uWSGI (if execvp fails)
def app(environ, start_response):
    start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
    return [b"Hijack failed. Check uwsgi.log for errors."]
