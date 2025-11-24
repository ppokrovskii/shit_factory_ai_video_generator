# Commit and Push to Develop

Run tests, check for secrets, commit changes, and push to develop branch.

```bash
#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Pre-commit checks starting..."

# Function to check for sensitive files
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
        echo -e "${RED}✗ No files staged for commit${NC}"
        return 1
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

# 1. Check for secrets first
if ! check_secrets; then
    echo -e "${RED}✗ Secret check failed. Aborting commit.${NC}"
    exit 1
fi

# 2. Run tests
echo "🧪 Running tests..."
uv run pytest -v --cov=app --cov-fail-under=45

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Tests failed. Fix issues before committing.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Tests passed${NC}"

# 3. Show git status
echo "📋 Current git status:"
git status --short

# 4. Confirm commit
echo ""
echo "Enter commit message (or 'cancel' to abort):"
read -r COMMIT_MSG

if [ "$COMMIT_MSG" = "cancel" ] || [ -z "$COMMIT_MSG" ]; then
    echo "Commit cancelled"
    exit 0
fi

# 5. Commit changes
echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Commit failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Changes committed${NC}"

# 6. Switch to develop branch
echo "🌿 Switching to develop branch..."
git checkout develop 2>/dev/null || git checkout -b develop

# 7. Merge from previous branch
echo "🔀 Merging changes..."
git merge - --no-ff -m "Merge into develop: $COMMIT_MSG"

# 8. Push to origin
echo "🚀 Pushing to origin/develop..."
git push origin develop

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Push failed${NC}"
    echo "  Check if you need to pull first or if there are conflicts"
    exit 1
fi

echo -e "${GREEN}✅ Successfully pushed to develop!${NC}"
```

## Security Checks Performed:

1. **File Pattern Checks**:
   - `.env` files
   - Key files (`.key`, `.pem`, `.p12`, `.pfx`)
   - Secret/credential files
   - API key files

2. **Content Scanning**:
   - OpenAI API keys (sk-*)
   - Google API keys (AIza*)
   - AWS credentials
   - Password/secret/token strings
   - Private keys

3. **Gitignore Validation**:
   - Ensures `.env` is in `.gitignore`
   - Verifies sensitive patterns are excluded

## What Gets Blocked:
- ❌ `.env` files
- ❌ API keys in code
- ❌ Private keys
- ❌ Password strings
- ❌ Credential files
- ✅ `.env.example` files (allowed)
