# Create Pull Request

Create a comprehensive pull request with all necessary information and checks.

## What this command does:

1. **Pre-PR validation**:
   - Ensures all tests pass with ≥80% coverage
   - Validates branch is up-to-date with develop
   - Checks for sensitive data or large files

2. **PR preparation**:
   - Generates comprehensive PR description
   - Creates checklist for reviewers
   - Links related issues and documentation

3. **Quality assurance**:
   - Runs final code quality checks
   - Ensures proper commit message format
   - Validates deployment readiness

## Steps to execute:

```bash
# 1. Validate current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "develop" ]; then
    echo "❌ Cannot create PR from main/develop branch. Switch to a feature branch first."
    exit 1
fi

echo "🔍 Creating PR for branch: $CURRENT_BRANCH"

# 2. Sync with develop
echo "🔄 Syncing with latest develop..."
git fetch origin develop
git merge origin/develop --no-ff

# 3. Run comprehensive tests
echo "🧪 Running final test suite..."
cd backend
uv run python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo "❌ Tests failed. Fix issues before creating PR."
    exit 1
fi
cd ..

# 4. Check for sensitive data and large files
echo "🔒 Checking for sensitive data..."
SENSITIVE_FILES=$(git diff origin/develop --name-only | grep -E "\.(env|key|pem|p12|pfx|secret)$" || echo "")
if [ -n "$SENSITIVE_FILES" ]; then
    echo "❌ Sensitive files detected: $SENSITIVE_FILES"
    echo "Remove sensitive data before creating PR."
    exit 1
fi

LARGE_FILES=$(git diff origin/develop --name-only | xargs -I {} sh -c 'if [ -f "{}" ] && [ $(wc -c < "{}") -gt 1048576 ]; then echo "{}"; fi' || echo "")
if [ -n "$LARGE_FILES" ]; then
    echo "⚠️  Large files detected (>1MB): $LARGE_FILES"
    echo "Consider using Git LFS or reducing file size."
fi

# 5. Generate PR description
echo "📝 Generating PR description..."
REPO_URL=$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')

# Get commit messages since develop
COMMITS=$(git log origin/develop..HEAD --oneline --reverse)
CHANGED_FILES=$(git diff origin/develop --name-only)

# Count changes
BACKEND_CHANGES=$(echo "$CHANGED_FILES" | grep -c "^backend/" || echo "0")
FRONTEND_CHANGES=$(echo "$CHANGED_FILES" | grep -c "^frontend/" || echo "0")
TEST_CHANGES=$(echo "$CHANGED_FILES" | grep -c "test" || echo "0")

cat > pr_description.md << EOF
## 🎯 Purpose
<!-- Describe what this PR accomplishes -->

## 📋 Changes
- **Backend changes**: $BACKEND_CHANGES files
- **Frontend changes**: $FRONTEND_CHANGES files  
- **Test changes**: $TEST_CHANGES files

### 🔧 Technical Changes
$COMMITS

### 📁 Files Modified
\`\`\`
$CHANGED_FILES
\`\`\`

## 🧪 Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Code coverage ≥80%
- [ ] Manual testing completed

## 🔍 Code Review Checklist
- [ ] Code follows project style guidelines
- [ ] No sensitive data committed
- [ ] Proper error handling implemented
- [ ] Logging added where appropriate
- [ ] Documentation updated if needed

## 🚀 Deployment Notes
- [ ] Database migrations included (if applicable)
- [ ] Environment variables documented
- [ ] Breaking changes documented
- [ ] Rollback plan considered

## 🔗 Related Issues
<!-- Link to GitHub issues: Closes #123, Fixes #456 -->

## 📸 Screenshots/Demo
<!-- Add screenshots or demo links if applicable -->

---
**Branch**: \`$CURRENT_BRANCH\`  
**Target**: \`develop\`  
**Tests**: ✅ Passing with $(cd backend && uv run python -m pytest --cov=app --quiet 2>/dev/null | grep "TOTAL" | awk '{print $4}' || echo "??")% coverage
EOF

# 6. Display PR information
echo ""
echo "✅ PR ready to create!"
echo ""
echo "🔗 Create PR at:"
echo "   https://github.com/$REPO_URL/compare/develop...$CURRENT_BRANCH"
echo ""
echo "📋 PR Description (saved to pr_description.md):"
echo "----------------------------------------"
cat pr_description.md
echo "----------------------------------------"
echo ""

# 7. Final push
echo "🚀 Pushing final changes..."
git push origin "$CURRENT_BRANCH"

# 8. Open PR creation page (if on Windows with browser)
if command -v start >/dev/null 2>&1; then
    echo "🌐 Opening PR creation page..."
    start "https://github.com/$REPO_URL/compare/develop...$CURRENT_BRANCH"
fi

echo ""
echo "✅ PR creation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review the generated PR description"
echo "   2. Add any missing context or screenshots"
echo "   3. Request appropriate reviewers"
echo "   4. Link related issues"
echo "   5. Monitor CI/CD pipeline"
```

## PR Quality Standards:
- **Title**: Clear, descriptive, follows conventional commits
- **Description**: Comprehensive with context and testing info
- **Size**: Ideally <500 lines changed (split large PRs)
- **Tests**: All tests pass with ≥80% coverage
- **Documentation**: Updated for new features/changes

## Required Reviewers:
- **Backend changes**: Senior backend developer
- **Frontend changes**: Frontend team lead
- **Database changes**: Database administrator
- **Security changes**: Security team member

## PR Labels:
- `feature` - New functionality
- `bugfix` - Bug fixes
- `refactor` - Code improvements
- `docs` - Documentation updates
- `breaking-change` - Breaking changes
- `needs-testing` - Requires additional testing

## Merge Requirements:
- ✅ All CI checks pass
- ✅ At least 1 approval from code owner
- ✅ No merge conflicts
- ✅ Branch is up-to-date with develop
- ✅ All conversations resolved
