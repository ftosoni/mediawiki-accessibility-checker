import sys
import asyncio
import os

# Fix for Windows: Playwright requires ProactorEventLoop to launch subprocesses
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Union

from backend.schemas import AccessibilityRequest, AccessibilityResponse, ExportRequest, ExportFormat
from backend.services.axe_service import AxeService
from backend.services.export_service import ExportService

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

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("frontend/interface.html")

async def _handle_export_response(results: AccessibilityResponse, format: ExportFormat):
    """Helper to handle the export conversion and Response object creation."""
    logo_path = os.path.join(os.getcwd(), "static", "images", "IMWD_UG_logo.jpg")
    
    if format == ExportFormat.JSON:
        content = ExportService.to_json(results)
        return Response(content=content, media_type="application/json", headers={"Content-Disposition": "attachment; filename=report.json"})
    
    elif format == ExportFormat.CSV:
        content = ExportService.to_csv(results)
        return Response(content=content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})
        
    elif format == ExportFormat.WIKITEXT:
        content = ExportService.to_wikitext(results)
        return Response(content=content, media_type="text/plain", headers={"Content-Disposition": "attachment; filename=report.txt"})
        
    elif format == ExportFormat.PDF:
        content = await ExportService.to_pdf(results, logo_path)
        return Response(content=content, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})
    
    return results

@app.get("/api/check", tags=["Audit"])
async def check_accessibility_get(
    url: str = Query(..., description="The URL to check"), 
    standard: str = Query("wcag22aa", description="Accessibility standard"),
    export: ExportFormat = Query(None, description="Directly export results to a specific format")
):
    """
    Check accessibility via GET request. 
    If 'export' is provided, returns the file directly.
    """
    try:
        results = await AxeService.run_axe(url=url, standard=standard)
        if export:
            return await _handle_export_response(results, export)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check", tags=["Audit"])
async def check_accessibility_post(request: AccessibilityRequest):
    """
    Check accessibility via POST request.
    If 'export' is provided in the body, returns the file directly.
    """
    try:
        if request.url:
            results = await AxeService.run_axe(url=request.url, standard=request.standard)
        elif request.html:
            results = await AxeService.run_axe(url=None, html=request.html, standard=request.standard)
        else:
            raise HTTPException(status_code=400, detail="Either url or html must be provided")
            
        if request.export:
            return await _handle_export_response(results, request.export)
        return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export", tags=["Export"])
async def export_report(request: ExportRequest):
    """
    Export audit results to various formats (PDF, JSON, CSV, Wikitext).
    This is useful for exporting results that were already cached or modified.
    """
    try:
        return await _handle_export_response(request.results, request.format)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
