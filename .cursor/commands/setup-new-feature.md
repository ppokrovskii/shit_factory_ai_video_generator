# Setup New Feature

Initialize a new feature branch with proper structure and boilerplate code.

## What this command does:

1. **Feature planning**:
   - Creates feature branch with proper naming
   - Sets up directory structure
   - Creates initial files and tests

2. **Development setup**:
   - Generates boilerplate code templates
   - Creates corresponding test files
   - Sets up API endpoints if needed

3. **Documentation**:
   - Creates feature documentation
   - Updates project documentation
   - Sets up tracking and requirements

## Steps to execute:

```bash
# 1. Get feature information
echo "🚀 Setting up new feature..."
echo ""
echo "Enter feature name (e.g., 'suno-integration', 'user-authentication'):"
read -r FEATURE_NAME

echo "Enter feature type:"
echo "  1) API endpoint"
echo "  2) Service/Business logic"
echo "  3) Frontend component"
echo "  4) Database model"
echo "  5) Integration/External service"
read -r FEATURE_TYPE

echo "Enter brief description:"
read -r FEATURE_DESCRIPTION

# 2. Create feature branch
echo "🌿 Creating feature branch..."
git checkout develop
git pull origin develop
git checkout -b "feature/$FEATURE_NAME"

# 3. Create directory structure based on feature type
case $FEATURE_TYPE in
    1) # API endpoint
        echo "📡 Setting up API endpoint structure..."
        
        # Create API endpoint file
        mkdir -p "backend/app/api"
        cat > "backend/app/api/${FEATURE_NAME}.py" << EOF
"""
${FEATURE_DESCRIPTION} API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.utils.logging_config import get_logger

logger = get_logger("api.${FEATURE_NAME}")
router = APIRouter(prefix="/${FEATURE_NAME}", tags=["${FEATURE_NAME}"])


@router.get("/")
async def get_${FEATURE_NAME}(db: Session = Depends(get_db)):
    """Get ${FEATURE_NAME} items"""
    logger.info("Getting ${FEATURE_NAME} items")
    # TODO: Implement logic
    return {"message": "${FEATURE_NAME} endpoint"}


@router.post("/")
async def create_${FEATURE_NAME}(db: Session = Depends(get_db)):
    """Create new ${FEATURE_NAME}"""
    logger.info("Creating new ${FEATURE_NAME}")
    # TODO: Implement logic
    return {"message": "${FEATURE_NAME} created"}
EOF

        # Create schema file
        mkdir -p "backend/app/schemas"
        cat > "backend/app/schemas/${FEATURE_NAME}.py" << EOF
"""
${FEATURE_DESCRIPTION} Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ${FEATURE_NAME^}Base(BaseModel):
    """Base schema for ${FEATURE_NAME}"""
    # TODO: Add base fields
    pass


class ${FEATURE_NAME^}Create(${FEATURE_NAME^}Base):
    """Schema for creating ${FEATURE_NAME}"""
    # TODO: Add creation fields
    pass


class ${FEATURE_NAME^}Update(${FEATURE_NAME^}Base):
    """Schema for updating ${FEATURE_NAME}"""
    # TODO: Add update fields
    pass


class ${FEATURE_NAME^}Response(${FEATURE_NAME^}Base):
    """Schema for ${FEATURE_NAME} response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
EOF

        # Create test file
        mkdir -p "backend/tests/test_api"
        cat > "backend/tests/test_api/test_${FEATURE_NAME}.py" << EOF
"""
Tests for ${FEATURE_NAME} API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class Test${FEATURE_NAME^}API:
    """Test class for ${FEATURE_NAME} API"""
    
    def test_get_${FEATURE_NAME}(self, client: TestClient):
        """Test getting ${FEATURE_NAME} items"""
        response = client.get("/${FEATURE_NAME}/")
        assert response.status_code == 200
        # TODO: Add specific assertions
    
    def test_create_${FEATURE_NAME}(self, client: TestClient):
        """Test creating ${FEATURE_NAME}"""
        data = {
            # TODO: Add test data
        }
        response = client.post("/${FEATURE_NAME}/", json=data)
        assert response.status_code == 201
        # TODO: Add specific assertions
EOF
        ;;
        
    2) # Service/Business logic
        echo "⚙️ Setting up service structure..."
        
        # Create service file
        mkdir -p "backend/app/services"
        cat > "backend/app/services/${FEATURE_NAME}_service.py" << EOF
"""
${FEATURE_DESCRIPTION} service
"""

from sqlalchemy.orm import Session
from typing import Optional, List

from app.utils.logging_config import get_logger

logger = get_logger("services.${FEATURE_NAME}")


class ${FEATURE_NAME^}Service:
    """Service for ${FEATURE_NAME} business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process_${FEATURE_NAME}(self) -> dict:
        """Process ${FEATURE_NAME} logic"""
        logger.info("Processing ${FEATURE_NAME}")
        
        try:
            # TODO: Implement business logic
            result = {"status": "success", "message": "${FEATURE_NAME} processed"}
            logger.info(f"${FEATURE_NAME} processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing ${FEATURE_NAME}: {e}")
            raise
EOF

        # Create test file
        mkdir -p "backend/tests/test_services"
        cat > "backend/tests/test_services/test_${FEATURE_NAME}_service.py" << EOF
"""
Tests for ${FEATURE_NAME} service
"""

import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session

from app.services.${FEATURE_NAME}_service import ${FEATURE_NAME^}Service


class Test${FEATURE_NAME^}Service:
    """Test class for ${FEATURE_NAME} service"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_db = Mock(spec=Session)
        self.service = ${FEATURE_NAME^}Service(self.mock_db)
    
    @pytest.mark.asyncio
    async def test_process_${FEATURE_NAME}(self):
        """Test ${FEATURE_NAME} processing"""
        result = await self.service.process_${FEATURE_NAME}()
        
        assert result["status"] == "success"
        assert "${FEATURE_NAME} processed" in result["message"]
EOF
        ;;
        
    3) # Frontend component
        echo "🎨 Setting up frontend component structure..."
        
        # Create component file
        mkdir -p "frontend/src/components"
        cat > "frontend/src/components/${FEATURE_NAME^}.tsx" << EOF
import React, { useState, useEffect } from 'react';

interface ${FEATURE_NAME^}Props {
  // TODO: Define component props
}

const ${FEATURE_NAME^}: React.FC<${FEATURE_NAME^}Props> = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // TODO: Component initialization logic
  }, []);

  const handle${FEATURE_NAME^}Action = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // TODO: Implement action logic
      console.log('${FEATURE_NAME} action executed');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">${FEATURE_DESCRIPTION}</h2>
      
      {/* TODO: Implement component UI */}
      <button
        onClick={handle${FEATURE_NAME^}Action}
        disabled={loading}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
      >
        {loading ? 'Loading...' : '${FEATURE_NAME^} Action'}
      </button>
    </div>
  );
};

export default ${FEATURE_NAME^};
EOF

        # Create service file for API calls
        mkdir -p "frontend/src/services"
        cat > "frontend/src/services/${FEATURE_NAME}.ts" << EOF
import api from './api';

export interface ${FEATURE_NAME^}Data {
  // TODO: Define data interface
  id?: number;
  name: string;
  createdAt?: string;
}

export const ${FEATURE_NAME}Service = {
  async getAll(): Promise<${FEATURE_NAME^}Data[]> {
    const response = await api.get('/${FEATURE_NAME}');
    return response.data;
  },

  async create(data: Omit<${FEATURE_NAME^}Data, 'id' | 'createdAt'>): Promise<${FEATURE_NAME^}Data> {
    const response = await api.post('/${FEATURE_NAME}', data);
    return response.data;
  },

  async update(id: number, data: Partial<${FEATURE_NAME^}Data>): Promise<${FEATURE_NAME^}Data> {
    const response = await api.put(\`/${FEATURE_NAME}/\${id}\`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(\`/${FEATURE_NAME}/\${id}\`);
  },
};
EOF
        ;;
        
    4) # Database model
        echo "🗄️ Setting up database model structure..."
        
        # Create model file
        mkdir -p "backend/app/models"
        cat > "backend/app/models/${FEATURE_NAME}.py" << EOF
"""
${FEATURE_DESCRIPTION} database model
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class ${FEATURE_NAME^}(Base):
    """${FEATURE_DESCRIPTION} model"""
    
    __tablename__ = "${FEATURE_NAME}s"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<${FEATURE_NAME^}(id={self.id}, name='{self.name}')>"
EOF

        # Create migration
        echo "📝 Creating database migration..."
        cd backend
        uv run alembic revision --autogenerate -m "Add ${FEATURE_NAME} model"
        cd ..
        ;;
        
    5) # Integration/External service
        echo "🔌 Setting up integration structure..."
        
        # Create integration service
        mkdir -p "backend/app/services"
        cat > "backend/app/services/${FEATURE_NAME}_integration.py" << EOF
"""
${FEATURE_DESCRIPTION} integration service
"""

import httpx
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger("integrations.${FEATURE_NAME}")


class ${FEATURE_NAME^}Integration:
    """Integration service for ${FEATURE_NAME}"""
    
    def __init__(self):
        self.base_url = getattr(settings, '${FEATURE_NAME}_api_url', 'https://api.example.com')
        self.api_key = getattr(settings, '${FEATURE_NAME}_api_key', None)
        
        if not self.api_key:
            logger.warning("${FEATURE_NAME} API key not configured")
    
    async def call_api(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API call to ${FEATURE_NAME} service"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"${FEATURE_NAME} API call successful: {endpoint}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"${FEATURE_NAME} API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling ${FEATURE_NAME} API: {e}")
            raise
EOF
        ;;
esac

# 4. Create feature documentation
echo "📚 Creating feature documentation..."
mkdir -p "docs/features"
cat > "docs/features/${FEATURE_NAME}.md" << EOF
# ${FEATURE_NAME^} Feature

## Overview
${FEATURE_DESCRIPTION}

## Requirements
- [ ] TODO: List functional requirements
- [ ] TODO: List non-functional requirements

## Technical Design
- [ ] TODO: Architecture overview
- [ ] TODO: Database schema changes
- [ ] TODO: API endpoints
- [ ] TODO: External integrations

## Implementation Plan
- [ ] TODO: Phase 1 tasks
- [ ] TODO: Phase 2 tasks
- [ ] TODO: Testing strategy
- [ ] TODO: Deployment plan

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Performance tests

## Documentation
- [ ] API documentation
- [ ] User documentation
- [ ] Developer documentation

## Acceptance Criteria
- [ ] TODO: Define acceptance criteria
- [ ] TODO: Define success metrics

## Related Issues
<!-- Link to GitHub issues -->

## Notes
<!-- Additional implementation notes -->
EOF

# 5. Update main router if API endpoint
if [ "$FEATURE_TYPE" = "1" ]; then
    echo "🔗 Adding router to main application..."
    echo ""
    echo "⚠️  Manual step required:"
    echo "   Add the following to backend/app/main.py:"
    echo ""
    echo "   from app.api.${FEATURE_NAME} import router as ${FEATURE_NAME}_router"
    echo "   app.include_router(${FEATURE_NAME}_router, prefix='/api')"
    echo ""
fi

# 6. Create initial commit
echo "💾 Creating initial commit..."
git add .
git commit -m "feat: Initialize ${FEATURE_NAME} feature structure

- Add boilerplate code for ${FEATURE_NAME}
- Create test files and documentation
- Set up proper directory structure

Type: ${FEATURE_TYPE}
Description: ${FEATURE_DESCRIPTION}"

# 7. Push feature branch
git push -u origin "feature/$FEATURE_NAME"

# 8. Summary
echo ""
echo "✅ Feature setup complete!"
echo ""
echo "📁 Created files:"
find . -name "*${FEATURE_NAME}*" -type f | head -10
echo ""
echo "🚀 Next steps:"
echo "   1. Review generated boilerplate code"
echo "   2. Implement TODO items in the code"
echo "   3. Write comprehensive tests"
echo "   4. Update documentation"
echo "   5. Test the feature thoroughly"
echo "   6. Create PR when ready"
echo ""
echo "🌿 Feature branch: feature/$FEATURE_NAME"
echo "📚 Documentation: docs/features/${FEATURE_NAME}.md"
```

## Feature Types:
1. **API Endpoint** - REST API with routes, schemas, tests
2. **Service/Business Logic** - Core business logic services
3. **Frontend Component** - React components with TypeScript
4. **Database Model** - SQLAlchemy models with migrations
5. **Integration** - External service integrations

## Generated Structure:
- ✅ Boilerplate code with proper patterns
- ✅ Corresponding test files
- ✅ Documentation templates
- ✅ Type hints and error handling
- ✅ Logging integration
- ✅ Git branch and initial commit

## Best Practices Included:
- Proper error handling and logging
- Type hints throughout
- Comprehensive test structure
- Documentation templates
- Consistent naming conventions
- Security considerations
