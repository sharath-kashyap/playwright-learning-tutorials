# Playwright Learning Tutorials

Simple Playwright + pytest examples using synchronous Python APIs.

## Project Files

- `test_001.py`: Basic fixture that launches Chromium, opens Google, and validates page title.
- `test_002.py`: Session and function scoped fixtures for Playwright, browser, context, and page.

## Prerequisites

- Python 3.13+
- Windows PowerShell

## Setup

1. Create virtual environment (already done in this project):

```powershell
python -m venv .venv
```

2. Activate virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install pytest playwright
```

4. Install Playwright browser binaries:

```powershell
python -m playwright install chromium
```

## Run Tests

Run all tests:

```powershell
python -m pytest -s
```

Run one test file:

```powershell
python -m pytest -s .\test_001.py
python -m pytest -s .\test_002.py
```

You can also run each file directly because each file has a `__main__` entry that invokes pytest:

```powershell
python .\test_001.py
python .\test_002.py
```

## GitHub Update Workflow

This project is connected to:

`git@github.com:sharath-kashyap/playwright-learning-tutorials.git`

For every update:

```powershell
git add .
git commit -m "Describe your update"
git push
```

## Notes

- Browser is currently launched with `headless=False` in both tests, so a visible browser window opens during runs.
- `.venv`, `__pycache__`, and `.pytest_cache` are excluded via `.gitignore`.
