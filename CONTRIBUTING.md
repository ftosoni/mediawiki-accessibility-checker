# Contributing to MediaWiki Accessibility Checker

Thank you for your interest in contributing! We welcome contributions from the community to help improve the accessibility of MediaWiki projects.

## 🛠️ Development Setup

To set up a development environment, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ftosoni/mediawiki-accessibility-checker.git
   cd mediawiki-accessibility-checker
   ```

2. **Set up a Virtual Environment**:
   It is highly recommended to use a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

## 🚀 Running Locally

Start the FastAPI backend:
```bash
uvicorn backend.main:app --reload
```
The application will be available at `http://localhost:8000`.

## 🧪 Testing and Quality

Before submitting a Pull Request, please ensure your changes do not break existing functionality.

### Automated Tests
(Currently, we are expanding our test suite. Contributions are welcome!)

### Manual Testing
You can run audits through the UI at `/` or directly via the API endpoints.

## 📜 Technical Guidelines

Please review our technical considerations:
- **Python Compatibility**: Support Python 3.11+.
- **FastAPI**: We use FastAPI for the backend.
- **Playwright**: We use Playwright for browser automation.
- **Toolforge Limits**: Stay within the **6 GiB RAM limit** for Toolforge webservices.

## 🤝 Contribution Process

1. **Open an Issue**: For any major changes, please open an issue first to discuss what you would like to change.
2. **Create a Branch**: Use a descriptive branch name (e.g., `fix/timeout-error` or `feature/new-export-format`).
3. **Submit a Pull Request**: Provide a clear description of the changes and link to the relevant issue.