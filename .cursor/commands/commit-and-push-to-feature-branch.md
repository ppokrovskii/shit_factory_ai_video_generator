# Commit and Push to Feature Branch

Create feature branch, run security checks, commit changes, and push.

```bash
#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check for sensitive files and secrets
check_secrets() {
    echo "🔒 Checking for sensitive files and secrets..."
    
    # Check if .env is properly ignored
    if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo -e "${RED}✗ .env not found in .gitignore${NC}"
        echo "  Add .env to .gitignore before committing"
        return 1
    fi
    
    # Get list of staged files
    STAGED_FILES=$(git diff --cached --name-only)
    
    if [ -z "$STAGED_FILES" ]; then
        echo -e "${YELLOW}⚠ No files staged for commit${NC}"
    fi
    
    # Check for sensitive file patterns
    SENSITIVE_PATTERNS=(
        "\.env$"
        "\.env\..*"
        ".*\.key$"
        ".*\.pem$"
        ".*\.p12$"
        ".*\.pfx$"
        ".*\.secret$"
        ".*\.credentials$"
        ".*_secret\..*"
        ".*_credentials\..*"
        ".*api[_-]?key.*"
        "secrets/"
        "credentials/"
    )
    
    SENSITIVE_FOUND=false
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        matches=$(echo "$STAGED_FILES" | grep -E "$pattern" || true)
        if [ -n "$matches" ]; then
            echo -e "${RED}✗ Sensitive file detected: $matches${NC}"
            SENSITIVE_FOUND=true
        fi
    done
    
    if [ "$SENSITIVE_FOUND" = true ]; then
        echo -e "${RED}✗ Sensitive files found in staging area${NC}"
        echo "  Remove them with: git reset HEAD <file>"
        return 1
    fi
    
    # Check for common secrets in file content
    echo "🔍 Scanning file contents for secrets..."
    
    SECRET_PATTERNS=(
        "OPENAI_API_KEY.*=.*['\"]?sk-[a-zA-Z0-9]{20,}['\"]?"
        "GOOGLE_API_KEY.*=.*['\"]?AIza[a-zA-Z0-9_-]{35}['\"]?"
        "AWS_SECRET_ACCESS_KEY.*=.*['\"]?[a-zA-Z0-9/+=]{40}['\"]?"
        "password.*=.*['\"][^'\"]{8,}['\"]"
        "secret.*=.*['\"][^'\"]{8,}['\"]"
        "token.*=.*['\"][a-zA-Z0-9_-]{20,}['\"]"
        "-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----"
    )
    
    for file in $STAGED_FILES; do
        if [ -f "$file" ]; then
            for pattern in "${SECRET_PATTERNS[@]}"; do
                if grep -qE "$pattern" "$file" 2>/dev/null; then
                    # Exclude .env.example files
                    if [[ ! "$file" =~ \.example$ ]]; then
                        echo -e "${RED}✗ Potential secret found in: $file${NC}"
                        echo "  Pattern: $pattern"
                        SENSITIVE_FOUND=true
                    fi
                fi
            done
        fi
    done
    
    if [ "$SENSITIVE_FOUND" = true ]; then
        echo -e "${RED}✗ Potential secrets found in staged files${NC}"
        echo "  Review the files and remove sensitive data"
        return 1
    fi
    
    echo -e "${GREEN}✓ No sensitive files or secrets detected${NC}"
    return 0
}

# 1. Get feature name
echo "🚀 Feature branch workflow"
echo "Enter feature name (e.g., feature/add-image-cli):"
read -r FEATURE_NAME

if [ -z "$FEATURE_NAME" ]; then
    echo -e "${RED}✗ Feature name is required${NC}"
    exit 1
fi

# Ensure feature name has 'feature/' prefix
if [[ ! "$FEATURE_NAME" =~ ^feature/ ]]; then
    FEATURE_NAME="feature/$FEATURE_NAME"
fi

# 2. Create/switch to feature branch
echo "🌿 Setting up feature branch: $FEATURE_NAME"
git checkout develop 2>/dev/null && git pull origin develop
git checkout -b "$FEATURE_NAME" 2>/dev/null || git checkout "$FEATURE_NAME"

# 3. Check for secrets before anything else
echo "🔍 Running security checks..."
git add .
if ! check_secrets; then
    echo -e "${RED}✗ Security check failed. Aborting commit.${NC}"
    git reset HEAD .
    exit 1
fi

# 4. Run tests
echo "🧪 Running tests..."
uv run pytest -v --cov=app

TEST_RESULT=$?
if [ $TEST_RESULT -ne 0 ]; then
    echo -e "${YELLOW}⚠ Tests failed but continuing (feature branch)${NC}"
    echo "  Fix tests before creating PR"
fi

# 5. Show git status
echo "📋 Files to be committed:"
git status --short

# 6. Get commit message
echo ""
echo "Enter commit message:"
read -r COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    echo -e "${RED}✗ Commit message is required${NC}"
    exit 1
fi

# 7. Commit changes
echo "💾 Committing changes..."
git commit -m "[$FEATURE_NAME] $COMMIT_MSG"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Commit failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Changes committed${NC}"

# 8. Push to origin
echo "🚀 Pushing to origin/$FEATURE_NAME..."
git push -u origin "$FEATURE_NAME"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Push failed${NC}"
    echo "  You may need to resolve conflicts or check permissions"
    exit 1
fi

echo -e "${GREEN}✅ Successfully pushed to $FEATURE_NAME!${NC}"

# 9. Show PR link
REPO_URL=$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/' | sed 's/\.git$//')
echo ""
echo "🔗 Create PR:"
echo "   https://github.com/$REPO_URL/compare/develop...$FEATURE_NAME"
```

## Security Features:

### Pre-Commit Checks:
- ✅ Verifies `.env` is in `.gitignore`
- ✅ Scans for sensitive file patterns
- ✅ Detects API keys in code
- ✅ Checks for private keys
- ✅ Identifies password/secret strings
- ✅ Allows `.env.example` files

### Workflow:
1. Create/switch to feature branch
2. **Security scan** (blocks commit if secrets found)
3. Run tests (warning only for feature branches)
4. Commit with security validation
5. Push to remote
6. Generate PR link

### What Gets Blocked:
- ❌ `.env` files
- ❌ API keys (OpenAI, Google, AWS)
- ❌ Private keys and certificates
- ❌ Password/secret strings
- ❌ Credential files

### Allowed:
- ✅ `.env.example` files
- ✅ Documentation with example keys
- ✅ Test fixtures with mock keys
