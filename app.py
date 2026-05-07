import os
import subprocess
import sys
import time

# 1. Setup Environment
os.chdir("/data/project/accessibility-checker/www/python/src")

HOME = "/data/project/accessibility-checker"
os.environ["HOME"] = HOME
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = f"{HOME}/.cache/ms-playwright"
os.environ["PYTHONPATH"] = f"{os.getcwd()}:{os.environ.get('PYTHONPATH', '')}"

# In Toolforge webservices, sys.executable is often uwsgi. 
# We need the real python3 binary.
PYTHON_BIN = "/usr/bin/python3"
if not os.path.exists(PYTHON_BIN):
    PYTHON_BIN = "python3" # Fallback to path

def setup():
    print("--- Checking Dependencies ---", flush=True)
    try:
        # Install/Update requirements in user space
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
    print(f"--- Launching Gunicorn on port {port} ---", flush=True)
    time.sleep(1)
    
    # Re-exec using the REAL python3 binary
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
