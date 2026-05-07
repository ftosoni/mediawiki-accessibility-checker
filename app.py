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
os.environ["PYTHONPATH"] = f"{os.getcwd()}:{os.environ.get('PYTHONPATH', '')}"

def setup():
    print("--- Checking Dependencies ---")
    sys.stdout.flush()
    try:
        # Install/Update requirements in user space
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user"], check=False)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--user"], check=False)
        
        # Install browsers
        browser_path = os.path.join(os.environ["PLAYWRIGHT_BROWSERS_PATH"], "chromium")
        if not os.path.exists(browser_path):
            print("--- Installing Playwright Chromium ---")
            sys.stdout.flush()
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
    except Exception as e:
        print(f"Setup error: {e}")
        sys.stdout.flush()

# 3. The Hijacker
if os.environ.get('HIJACKED') != 'true':
    os.environ['HIJACKED'] = 'true'
    setup()
    
    port = os.environ.get("PORT", "8000")
    print(f"--- Launching Gunicorn on port {port} ---")
    sys.stdout.flush()
    
    # Re-exec using the Python module to avoid PATH issues
    # We use 'python3 -m gunicorn'
    os.execvp(
        sys.executable, 
        [
            sys.executable,
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
