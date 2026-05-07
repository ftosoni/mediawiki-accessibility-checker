import os
import subprocess
import sys

# satisfy uWSGI requirement
def app(environ, start_response):
    start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
    return [b"Bootstrap failed. Check uwsgi.log."]

# Hijack immediately
if os.environ.get('HIJACKED') != 'true':
    os.environ['HIJACKED'] = 'true'
    print("--- Handing over to start.sh ---", flush=True)
    sys.stdout.flush()
    
    # Switch to the project directory and run start.sh
    os.chdir("/data/project/accessibility-checker/www/python/src")
    os.execvp("bash", ["bash", "start.sh"])
