# Run All Tests and Fix

Run tests with coverage and fix common issues.

```bash
cd backend

# Format and lint
uv run ruff format . && uv run ruff check . --fix

# Run tests with coverage
uv run python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80

# If tests fail, re-run failed tests only
uv run python -m pytest --lf -v --tb=short
```
