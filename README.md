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
MPL-2.0
- **📄 Multi-Format Exports**: Generate professional reports in **PDF**, **JSON**, **CSV**, and **Wikitext** (ready for Wiki pages).
- **🎨 Codex UI**: A beautiful, responsive interface that follows Wikimedia's modern design standards.
- **🔍 Intelligent DOM Enrichment**: Automatically retrieves full HTML snippets and image previews, even for truncated axe-core results.
- **🚀 RESTful API**: Fully documented OpenAPI/Swagger interface with support for both GET and POST audits.

## 🚀 API usage

The tool provides a high-performance RESTful API. You can run audits directly via the browser address bar:

```bash
# Direct PDF Export via GET
https://accessibility-checker.toolforge.org/api/check?url=https://it.wikipedia.org/wiki/Ciao&export=pdf
```

Automatic documentation is available at `/docs`.

## 🛠️ Setup

### Backend (Python)
Create and activate a virtual environment, then install dependencies:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
# Install Playwright browsers
playwright install chromium
```

### Running Locally
Start the FastAPI backend from the root directory:

```bash
# From the project root
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
The server will be available at `http://localhost:8000`.

---

## 🚀 Deployment (Toolforge)

Follow these steps to deploy on Wikimedia Toolforge.

### 1. Build Service
Toolforge uses the buildservice to containerize the application. Ensure your `Procfile` is present in the root.

```bash
become accessibility-checker

# Start build from repository
toolforge build start https://github.com/ftosoni/mediawiki-accessibility-checker

# Start webservice
toolforge webservice buildservice start --mount=all
```

### 2. Static Assets
Ensure the `static/images/` directory contains the required branding assets (like `IMWD_UG_logo.jpg`) for the PDF export service.

---

## 🛠️ Technology Stack

- **Audit Engine**: [axe-core](https://github.com/dequelabs/axe-core)
- **Browser Automation**: [Playwright](https://playwright.dev/)
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Design System**: [Wikimedia Codex](https://doc.wikimedia.org/codex/latest/)
- **PDF Generation**: Playwright Print-to-PDF


## 📄 Licence
[MPL-2.0 License](./LICENSE). Created by [Francesco Tosoni (Super nabla)](https://meta.wikimedia.org/wiki/Special:MyLanguage/User:Super_nabla). 
Powered by axe-core.
