# Suggested commands (Windows / PowerShell)
- Install deps: `uv pip install -r requirements.txt`
- Install Playwright browsers: `uv run python -m playwright install chromium chromium-headless-shell`
- Run tests: `uv run pytest -q`
- Run login-state helper: `uv run python .\save_state.py`
- Inspect files: `Get-ChildItem`, `Get-Content`, `rg pattern .`
