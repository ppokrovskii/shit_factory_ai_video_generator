# Commit and Push to Develop

Run tests, commit changes, and push to develop branch.

```bash
# Run tests
cd backend && uv run python -m pytest tests/ -v --cov=app --cov-fail-under=80

# Commit and push
cd .. && git add . && git status
git commit -m "Enter your commit message here"
git checkout develop 2>/dev/null || git checkout -b develop
git merge - --no-ff
git push origin develop
```
