# MediaWiki Accessibility Checker

[![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/ftosoni/mediawiki-accessibility-checker/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/ftosoni/mediawiki-accessibility-checker)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg?style=flat-square)](https://www.python.org/)
[![CI](https://github.com/ftosoni/mediawiki-accessibility-checker/actions/workflows/python-ci.yml/badge.svg?branch=main&style=flat-square)](https://github.com/ftosoni/mediawiki-accessibility-checker/actions/workflows/python-ci.yml)
[![Code Style: Wikimedia](https://img.shields.io/badge/code%20style-wikimedia-blueviolet.svg?style=flat-square)](https://www.mediawiki.org/wiki/Manual:Coding_conventions/JavaScript)
[![License](https://img.shields.io/github/license/ftosoni/mediawiki-accessibility-checker?style=flat-square)](./LICENSE)

A modern, high-performance accessibility auditing tool designed for the MediaWiki ecosystem. 
Built on **axe-core** and **Playwright**, it provides deep WCAG 2.2 AA validation with professional reporting capabilities.
The UI is built using the **Wikimedia Codex Design System** for a seamless experience within the Wikimedia environment.

As seen on [accessibility-checker.toolforge.org](https://accessibility-checker.toolforge.org/).

## ✨ Key Features

- **🌐 Deep MediaWiki Integration**: Optimized for auditing Wikipedia, Commons, and other MediaWiki-based projects.
- **🛡️ WCAG 2.2 AA Compliance**: Defaulted to the latest accessibility standards for comprehensive auditing.
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

We use the Toolforge buildservice for deployment to ensure dependencies and Procfile instructions are correctly processed.

### 1. Clean Existing Build
Stop any running service and clear the old build cache:
```bash
# Stop and clean existing build
toolforge webservice buildservice stop --mount=all
toolforge build clean -y
```

### 2. Build the Application
Start a new build directly from the GitHub repository:
```bash
# Start build from repository
toolforge build start https://github.com/ftosoni/mediawiki-accessibility-checker
```

### 3. Launch Webservice
Once the build is complete, launch the service with elevated memory (6GiB recommended for Playwright):
```bash
# Start webservice with 6GiB RAM
toolforge webservice buildservice start --mount=all -m 6Gi
```

## 🛠️ Technology Stack

- **Audit Engine**: [axe-core](https://github.com/dequelabs/axe-core)
- **Browser Automation**: [Playwright](https://playwright.dev/)
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Design System**: [Wikimedia Codex](https://doc.wikimedia.org/codex/latest/)
- **PDF Generation**: Playwright Print-to-PDF


## 📄 Licence
[MPL-2.0 License](./LICENSE). Created by [Francesco Tosoni (Super nabla)](https://meta.wikimedia.org/wiki/Special:MyLanguage/User:Super_nabla). 
Powered by axe-core.
