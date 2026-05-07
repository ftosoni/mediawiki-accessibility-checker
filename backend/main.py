import sys
import asyncio

# Fix for Windows: Playwright requires ProactorEventLoop to launch subprocesses
# This MUST be set at the very top of the entry point.
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.schemas import AccessibilityRequest, AccessibilityResponse
from backend.services.axe_service import AxeService

app = FastAPI(
    title="MediaWiki Accessibility Checker",
    description="Modern accessibility auditing tool powered by axe-core and Playwright",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("frontend/interface.html")

@app.post("/api/check", response_model=AccessibilityResponse)
async def check_accessibility(request: AccessibilityRequest):
    try:
        if request.url:
            return await AxeService.run_axe(url=request.url, standard=request.standard)
        elif request.html:
            return await AxeService.run_axe(url=None, html=request.html, standard=request.standard)
        else:
            raise HTTPException(status_code=400, detail="Either url or html must be provided")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
