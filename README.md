# MediaWiki Accessibility Checker (axe-core)

A modern, high-performance accessibility auditing tool for the MediaWiki ecosystem. Powered by **FastAPI**, **Playwright**, and **axe-core**.

## Features
- **URL Audit**: Check any live MediaWiki page or external URL.
- **HTML Snippet Audit**: Paste raw HTML for quick validation.
- **Deep Scanning**: Supports Shadow DOM and dynamic content.
- **Codex Design**: Beautiful, responsive interface based on the Wikimedia Design System.
- **Standards**: WCAG 2.1 & 2.2 (A, AA, AAA).

## Tech Stack
- **Backend**: Python 3.9+, FastAPI, Playwright (Chromium).
- **Frontend**: Vanilla JS, CSS (Codex), HTML5.
- **Engine**: axe-core.

## Local Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

3. **Run the application**:
   ```bash
   uvicorn backend.main:app --reload
   ```

4. **Access the tool**:
   Open [http://localhost:8000](http://localhost:8000) in your browser.

## Deployment on Toolforge

This tool is designed to run on Wikimedia Toolforge.

1. **Create a new tool**:
   ```bash
   become <toolname>
   ```

2. **Configure Kubernetes**:
   Ensure your `webservice` is configured to use the Python environment.

3. **Install dependencies in your Toolforge environment**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Start the webservice**:
   ```bash
   webservice python3.11 start
   ```

## License
GPL 2.0
