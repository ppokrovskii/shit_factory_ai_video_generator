# Commit and Push to Feature Branch

Create feature branch, commit changes, and push.

```bash
# Get feature name and setup
echo "Feature name (e.g., feature/suno-integration):"
read FEATURE_NAME

# Create/switch to feature branch
git checkout develop && git pull origin develop
git checkout -b "$FEATURE_NAME" 2>/dev/null || git checkout "$FEATURE_NAME"

# Run tests and commit
cd backend && uv run python -m pytest tests/ -v --cov=app
cd .. && git add . && git status

echo "Commit message:"
read COMMIT_MSG
git commit -m "[$FEATURE_NAME] $COMMIT_MSG"
git push -u origin "$FEATURE_NAME"

# Show PR link
echo "Create PR: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')/compare/develop...$FEATURE_NAME"
```
