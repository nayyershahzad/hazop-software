# HAZOP Software Performance Optimization Plan

**Date:** October 16, 2025
**Purpose:** Improve performance of HAZOP Software on Render.com Professional Plan
**Author:** Claude

## Overview

This document outlines a comprehensive plan to optimize the HAZOP Software application deployed on Render.com. After upgrading to the Professional plan, these optimizations will ensure maximum performance and responsiveness for users. The plan is organized into phases with specific tasks, code changes, and expected outcomes.

## Phase 1: Critical Performance Improvements

These high-impact changes should be implemented immediately to address the most significant performance bottlenecks.

### 1.1 Database Connection Pooling

**Files to Modify:**
- `/backend/app/database.py`

**Implementation:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Add connection pooling parameters
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,               # Maintain 10 connections
    max_overflow=20,            # Allow up to 20 more under heavy load
    pool_timeout=30,            # Wait up to 30 seconds for a connection
    pool_recycle=1800,          # Recycle connections after 30 minutes
    pool_pre_ping=True          # Verify connections before use
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    # Import all models so they are registered with Base.metadata
    from app.models import (
        Organization, User, HazopStudy, HazopNode, Deviation,
        Cause, Consequence, Safeguard, RiskAssessment, Recommendation,
        PIDDocument, NodePIDLocation, ImpactAssessment
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
```

**Expected Outcome:**
- Reduced database connection overhead
- Improved handling of concurrent requests
- Better stability under load

### 1.2 Implement Gemini API Response Caching

**Files to Create:**
- `/backend/app/services/gemini_cache.py`
- `/backend/app/models/gemini_cache.py`
- `/backend/migrations/006_gemini_cache.sql`

**Files to Modify:**
- `/backend/app/services/gemini_service.py`
- `/backend/app/api/gemini.py`

**Implementation:**

1. First, create the database model in `/backend/app/models/gemini_cache.py`:
```python
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
import uuid
from app.database import Base

class GeminiCache(Base):
    __tablename__ = "gemini_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(64), unique=True, nullable=False, index=True)
    deviation_id = Column(UUID(as_uuid=True), ForeignKey("deviations.id", ondelete="CASCADE"), nullable=False)
    suggestion_type = Column(String(50), nullable=False)  # 'causes', 'consequences', 'safeguards', etc.
    context_hash = Column(String(32), nullable=False)
    response_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
```

2. Create the database migration in `/backend/migrations/006_gemini_cache.sql`:
```sql
-- Create table for caching Gemini AI responses
CREATE TABLE IF NOT EXISTS gemini_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(64) NOT NULL UNIQUE,
    deviation_id UUID NOT NULL,
    suggestion_type VARCHAR(50) NOT NULL,
    context_hash VARCHAR(32) NOT NULL,
    response_data TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_deviation
        FOREIGN KEY (deviation_id)
        REFERENCES deviations(id)
        ON DELETE CASCADE
);

-- Index for fast lookups
CREATE INDEX idx_gemini_cache_key ON gemini_cache(cache_key);
CREATE INDEX idx_gemini_cache_deviation ON gemini_cache(deviation_id);
CREATE INDEX idx_gemini_cache_expires ON gemini_cache(expires_at);

-- Comments
COMMENT ON TABLE gemini_cache IS 'Caches Gemini AI API responses to reduce costs';
COMMENT ON COLUMN gemini_cache.cache_key IS 'SHA256 hash of deviation_id + context + type';
COMMENT ON COLUMN gemini_cache.context_hash IS 'MD5 hash of context for quick comparison';
COMMENT ON COLUMN gemini_cache.expires_at IS 'Cache expiration timestamp (TTL: 7 days)';
```

3. Create the cache service in `/backend/app/services/gemini_cache.py`:
```python
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.gemini_cache import GeminiCache

class GeminiCacheService:
    def __init__(self, db: Session):
        self.db = db
        self.cache_ttl = timedelta(days=7)  # Cache for 7 days

    def _generate_cache_key(self, deviation_id: str, context: Dict, suggestion_type: str) -> str:
        """Generate unique cache key from deviation + context + type"""
        cache_data = {
            'deviation_id': deviation_id,
            'context': context,
            'type': suggestion_type
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def get_cached_response(self, deviation_id: str, context: Dict, suggestion_type: str) -> Optional[Dict[str, Any]]:
        """Get cached response if exists and not expired"""
        cache_key = self._generate_cache_key(deviation_id, context, suggestion_type)

        cached = self.db.query(GeminiCache).filter(
            GeminiCache.cache_key == cache_key,
            GeminiCache.expires_at > datetime.utcnow()
        ).first()

        if cached:
            print(f"✅ Cache hit for {suggestion_type} (deviation: {deviation_id})")
            return json.loads(cached.response_data)

        print(f"❌ Cache miss for {suggestion_type} (deviation: {deviation_id})")
        return None

    def cache_response(self, deviation_id: str, context: Dict, suggestion_type: str, response: Dict[str, Any]):
        """Cache API response"""
        cache_key = self._generate_cache_key(deviation_id, context, suggestion_type)
        expires_at = datetime.utcnow() + self.cache_ttl

        # Check for existing cache entry and update if exists
        existing = self.db.query(GeminiCache).filter(
            GeminiCache.cache_key == cache_key
        ).first()

        if existing:
            existing.response_data = json.dumps(response)
            existing.expires_at = expires_at
            self.db.commit()
            return

        # Create new cache entry
        cached = GeminiCache(
            cache_key=cache_key,
            deviation_id=deviation_id,
            suggestion_type=suggestion_type,
            context_hash=self._hash_context(context),
            response_data=json.dumps(response),
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )

        self.db.add(cached)
        self.db.commit()

    def _hash_context(self, context: Dict) -> str:
        """Generate hash of context for quick lookup"""
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def cleanup_expired(self):
        """Remove expired cache entries"""
        expired = self.db.query(GeminiCache).filter(
            GeminiCache.expires_at < datetime.utcnow()
        ).delete()
        self.db.commit()
        return expired
```

4. Update the gemini_service.py to use caching:
```python
# Add to imports
from app.services.gemini_cache import GeminiCacheService

# Modify the suggest_causes method to use cache
async def suggest_causes(
    self,
    db: Session,
    node: Node,
    deviation: "Deviation",
    context: Optional[Dict] = None
) -> List[Dict[str, any]]:
    """Generate AI suggestions for causes of a deviation."""
    if not self.api_key_configured:
        print("[Gemini] API key not configured, returning empty suggestions")
        return []

    # Initialize cache service
    cache_service = GeminiCacheService(db)

    # Try to get from cache first
    context_dict = context or {}
    cached_response = cache_service.get_cached_response(
        deviation_id=str(deviation.id),
        context=context_dict,
        suggestion_type='causes'
    )

    if cached_response:
        # Add flag to indicate this came from cache
        for suggestion in cached_response:
            suggestion['cached'] = True
        return cached_response

    # Cache miss - call API
    prompt = self._build_causes_prompt(node, deviation, context)

    print(f"[Gemini] Generating cause suggestions for deviation: {deviation.parameter}/{deviation.guide_word}")
    print(f"[Gemini] Context provided: {context}")

    try:
        response = await self._generate_response(prompt)
        print(f"[Gemini] Raw response received: {response[:200]}...")
        suggestions = self._parse_suggestions(response)
        print(f"[Gemini] Parsed {len(suggestions)} suggestions")

        # Cache the successful response
        cache_service.cache_response(
            deviation_id=str(deviation.id),
            context=context_dict,
            suggestion_type='causes',
            response=suggestions
        )

        return suggestions
    except Exception as e:
        print(f"[Gemini] Error generating cause suggestions: {e}")
        import traceback
        traceback.print_exc()
        return []
```

5. Apply the same caching pattern to the other suggestion methods.

**Expected Outcome:**
- 70% reduction in Gemini API costs
- Faster response times for AI suggestions
- Reduced load on backend services

### 1.3 Add Database Indexes

**Files to Create:**
- `/backend/migrations/007_performance_indexes.sql`

**Implementation:**
```sql
-- Create indexes for most frequently queried columns

-- Causes table
CREATE INDEX IF NOT EXISTS idx_causes_deviation_id ON causes(deviation_id);
CREATE INDEX IF NOT EXISTS idx_causes_created_by ON causes(created_by);

-- Consequences table
CREATE INDEX IF NOT EXISTS idx_consequences_deviation_id ON consequences(deviation_id);
CREATE INDEX IF NOT EXISTS idx_consequences_cause_id ON consequences(cause_id);
CREATE INDEX IF NOT EXISTS idx_consequences_created_by ON consequences(created_by);

-- Safeguards table
CREATE INDEX IF NOT EXISTS idx_safeguards_deviation_id ON safeguards(deviation_id);
CREATE INDEX IF NOT EXISTS idx_safeguards_consequence_id ON safeguards(consequence_id);
CREATE INDEX IF NOT EXISTS idx_safeguards_created_by ON safeguards(created_by);

-- Recommendations table
CREATE INDEX IF NOT EXISTS idx_recommendations_deviation_id ON recommendations(deviation_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_consequence_id ON recommendations(consequence_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_by ON recommendations(created_by);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);

-- Node and Deviation tables
CREATE INDEX IF NOT EXISTS idx_nodes_study_id ON hazop_nodes(study_id);
CREATE INDEX IF NOT EXISTS idx_deviations_node_id ON deviations(node_id);
CREATE INDEX IF NOT EXISTS idx_deviations_parameter ON deviations(parameter);
CREATE INDEX IF NOT EXISTS idx_deviations_guide_word ON deviations(guide_word);

-- Impact assessment
CREATE INDEX IF NOT EXISTS idx_impact_assessment_consequence_id ON impact_assessments(consequence_id);
CREATE INDEX IF NOT EXISTS idx_impact_assessment_risk_level ON impact_assessments(risk_level);

-- Organization-based queries
CREATE INDEX IF NOT EXISTS idx_studies_organization_id ON hazop_studies(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id);
```

**Expected Outcome:**
- Faster query performance for all HAZOP entity operations
- Reduced database load, especially for list operations
- Improved performance when filtering by organization

## Phase 2: Frontend Optimizations

These changes focus on improving the frontend performance and user experience.

### 2.1 Code Splitting & Bundle Optimization

**Files to Modify:**
- `/frontend/vite.config.ts`
- `/frontend/src/App.tsx`
- `/frontend/src/pages/StudyDetail.tsx`
- `/frontend/src/components/HAZOPAnalysis.tsx`
- `/frontend/src/components/PIDViewer.tsx`

**Implementation:**

1. Update Vite configuration for build optimization:
```typescript
// vite.config.ts
import { defineConfig, splitVendorChunkPlugin } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    splitVendorChunkPlugin(), // Split vendor chunks
  ],
  build: {
    target: 'es2018',
    minify: 'terser', // Use terser for better minification
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          // Split large dependencies into separate chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'pdf-viewer': ['react-pdf', 'pdfjs-dist'],
          'data-viz': ['recharts'],
          'utils': ['axios', 'zustand']
        },
      },
    },
    chunkSizeWarningLimit: 1000, // Increase the warning limit
  },
  css: {
    // CSS modules configuration
    modules: {
      localsConvention: 'camelCase',
    }
  },
  resolve: {
    alias: {
      // Add an alias for source directory
      '@': resolve(__dirname, 'src'),
      // Keep the PDF styles alias
      '@pdf-styles': resolve(__dirname, 'src/pdf-styles.css')
    }
  }
})
```

2. Implement lazy loading for major components in App.tsx:
```tsx
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Loading from './components/Loading';

// Lazy load pages for better code splitting
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Studies = lazy(() => import('./pages/Studies'));
const StudyDetail = lazy(() => import('./pages/StudyDetail'));
const UserProfile = lazy(() => import('./pages/UserProfile'));
const NotFound = lazy(() => import('./pages/NotFound'));

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Suspense fallback={<Loading />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/studies" element={<Studies />} />
          <Route path="/studies/:studyId" element={<StudyDetail />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="/" element={<Studies />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
```

3. Create a basic Loading component:
```tsx
// src/components/Loading.tsx
function Loading() {
  return (
    <div className="flex justify-center items-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
      <p className="ml-2">Loading...</p>
    </div>
  );
}

export default Loading;
```

4. Dynamically import heavy components like PIDViewer:
```tsx
// In StudyDetail.tsx, replace the direct import
import { lazy, Suspense } from 'react';
// Remove: import { PIDViewer } from '../components/PIDViewer';

// Add lazy loading
const PIDViewer = lazy(() => import('../components/PIDViewer'));

// Then in the render section
{studyId && (
  <Suspense fallback={<div className="h-20 bg-gray-100 animate-pulse rounded-lg"></div>}>
    <PIDViewer
      studyId={studyId}
      selectedNodeId={selectedNode?.id}
      onNodeMarked={loadNodes}
    />
  </Suspense>
)}
```

**Expected Outcome:**
- Reduced initial load time
- Smaller bundle sizes
- Better code splitting for large dependencies

### 2.2 Implement Memoization for Complex Components

**Files to Modify:**
- `/frontend/src/components/HAZOPAnalysis.tsx`
- `/frontend/src/components/GeminiInsightsPanel.tsx`

**Implementation:**

1. Memoize the HAZOPAnalysis component:
```tsx
import React, { useState, useEffect, useMemo, useCallback, memo } from 'react';

// ... existing code ...

// Wrap the export with React.memo
export const HAZOPAnalysis = memo(function HAZOPAnalysis({
  deviation,
  onUnsavedChanges
}: HAZOPAnalysisProps) {
  // ... component implementation ...

  // Memoize complex calculations
  const hasActiveItems = useMemo(() => {
    return causes.length > 0 || consequences.length > 0 || safeguards.length > 0 || recommendations.length > 0;
  }, [causes.length, consequences.length, safeguards.length, recommendations.length]);

  // Memoize handlers
  const handleSave = useCallback(() => {
    markAsSaved();
    alert('Analysis state saved! ✓');
  }, [markAsSaved]);

  // ... rest of component ...
});
```

2. Memoize the GeminiInsightsPanel:
```tsx
import React, { useState, useEffect, useMemo, useCallback, memo } from 'react';

// ... existing code ...

// Wrap the export with React.memo and specify comparison function
export const GeminiInsightsPanel = memo(function GeminiInsightsPanel({
  deviation,
  selectedCauseId,
  selectedConsequenceId,
  onAddCause,
  onAddConsequence,
  onAddRecommendation,
}: GeminiInsightsPanelProps) {
  // ... component implementation ...

  // Memoize context processing
  const processedContext = useMemo(() => {
    // Construct context object from form inputs
    return Object.entries(processContext).reduce((acc, [key, value]) => {
      if (value) acc[key as keyof typeof processContext] = value;
      return acc;
    }, {} as Partial<typeof processContext>);
  }, [processContext]);

  // Memoize handlers
  const loadSuggestions = useCallback(async () => {
    // ... existing implementation ...
  }, [deviation.id, selectedCauseId, selectedConsequenceId, insightType, processedContext]);

  // ... rest of component ...
}, (prevProps, nextProps) => {
  // Custom comparison to prevent unnecessary re-renders
  return (
    prevProps.deviation.id === nextProps.deviation.id &&
    prevProps.selectedCauseId === nextProps.selectedCauseId &&
    prevProps.selectedConsequenceId === nextProps.selectedConsequenceId
  );
});
```

**Expected Outcome:**
- Reduced unnecessary re-renders
- Improved component performance
- Smoother user interface

## Phase 3: API and Backend Optimizations

These changes focus on improving API performance and backend service configurations.

### 3.1 Optimize API Request/Response Handling

**Files to Modify:**
- `/backend/app/main.py`
- `/backend/app/api/deps.py`
- `/backend/app/api/studies.py`

**Implementation:**

1. Add response compression to main.py:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware  # Add this import
from app.database import init_db
from app.api import auth, studies, hazop, pid, impact_assessment, gemini
import os

app = FastAPI(
    title="HAZOP Management System",
    description="AI-powered HAZOP study management system with multi-tenant support",
    version="2.0.0-mvp"
)

# Add Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB

# CORS middleware with environment-aware origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]

# Add wildcard for development (will be restricted in production)
if os.getenv("ENVIRONMENT") == "development":
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of the file ...
```

2. Optimize authentication in deps.py with caching:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.security import decode_token
from uuid import UUID
from functools import lru_cache
from typing import Dict, Any, Optional

security = HTTPBearer()

# Simple in-memory token cache (will reset on service restart)
# For a more persistent solution, use Redis
token_cache: Dict[str, Dict[str, Any]] = {}

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Returns full User object with organization relationship loaded.

    This is the main dependency for protecting endpoints and enforcing
    organization-level data isolation.
    """
    try:
        token = credentials.credentials

        # Check if token is in cache
        cached_data = token_cache.get(token)
        if cached_data:
            # Validate expiry
            if cached_data.get("exp", 0) > datetime.utcnow().timestamp():
                user_id = cached_data.get("user_id")
                # Get user from database (still needed for latest data)
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return user

        # Not in cache or expired, decode token
        payload = decode_token(token)
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        organization_id: str = payload.get("organization_id")

        if email is None or user_id is None or organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Cache token data
        token_cache[token] = {
            "user_id": user_id,
            "email": email,
            "organization_id": organization_id,
            "exp": payload.get("exp", 0)
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Query user and verify they belong to the organization in the token
    user = db.query(User).filter(
        User.id == user_id,
        User.email == email,
        User.organization_id == organization_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or organization mismatch"
        )

    # Verify organization is active
    organization = db.query(Organization).filter(Organization.id == user.organization_id).first()
    if not organization or not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization account is suspended"
        )

    return user
```

3. Optimize the dashboard endpoint in studies.py with JOIN operations:
```python
@router.get("/{study_id}/dashboard")
def get_study_dashboard(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard data for a study"""
    study = db.query(HazopStudy).filter(HazopStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Use a single query with JOIN to get counts
    query = db.query(
        HazopNode.id.label('node_id'),
        HazopNode.node_name.label('node_name'),
        func.count(distinct(Deviation.id)).label('deviation_count')
    ).join(
        Deviation, Deviation.node_id == HazopNode.id, isouter=True
    ).filter(
        HazopNode.study_id == study_id
    ).group_by(
        HazopNode.id, HazopNode.node_name
    )

    deviations_by_node = [
        {
            "node_id": str(row.node_id),
            "node_name": row.node_name,
            "count": row.deviation_count
        }
        for row in query.all()
    ]

    # Get total counts efficiently with subqueries
    total_nodes = db.query(func.count(HazopNode.id)).filter(
        HazopNode.study_id == study_id
    ).scalar()

    # Create efficient subquery for nodes in this study
    nodes_subq = db.query(HazopNode.id).filter(
        HazopNode.study_id == study_id
    ).subquery()

    # Count deviations using the subquery
    total_deviations = db.query(func.count(Deviation.id)).filter(
        Deviation.node_id.in_(nodes_subq)
    ).scalar()

    # Get risk distribution with a JOIN query
    risk_distribution = {
        "critical": 0, "high": 0, "medium": 0, "low": 0
    }

    risk_query = db.query(
        ImpactAssessment.risk_level,
        func.count(ImpactAssessment.id).label('count')
    ).join(
        Consequence, Consequence.id == ImpactAssessment.consequence_id
    ).join(
        Deviation, Deviation.id == Consequence.deviation_id
    ).join(
        HazopNode, HazopNode.id == Deviation.node_id
    ).filter(
        HazopNode.study_id == study_id,
        ImpactAssessment.risk_level.isnot(None)
    ).group_by(
        ImpactAssessment.risk_level
    )

    for row in risk_query.all():
        risk_level = row.risk_level.lower()
        if risk_level in risk_distribution:
            risk_distribution[risk_level] = row.count

    # Sort by count descending
    deviations_by_node.sort(key=lambda x: x["count"], reverse=True)

    return {
        "study": {
            "id": str(study.id),
            "title": study.title,
            "facility_name": study.facility_name
        },
        "metrics": {
            "total_nodes": total_nodes,
            "total_deviations": total_deviations,
            "risk_distribution": risk_distribution,
            "deviations_by_node": deviations_by_node
        }
    }
```

**Expected Outcome:**
- Reduced API response times
- Lower bandwidth usage
- Improved authentication performance

### 3.2 Configure Render.com Service Settings

**Settings to Update in Render Dashboard:**

1. **Web Service Settings (Backend):**
   - Increase instance size to at least 1GB RAM
   - Enable auto-scaling with:
     - Min: 1 instance
     - Max: 3 instances
     - Target CPU usage: 70%
   - Set health check path: `/health`
   - Configure environment variables:
     ```
     PYTHON_VERSION=3.11.9
     JWT_ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=1440
     ENVIRONMENT=production
     ```

2. **Database Settings:**
   - Enable autoscaling
   - Set connection limit to match your max expected concurrent users
   - Enable query performance insights
   - Schedule weekly maintenance during off-hours

3. **Frontend Static Site:**
   - Enable global CDN for better asset delivery
   - Set cache headers:
     - Cache-Control: max-age=31536000 (for assets with hashed filenames)
     - Cache-Control: max-age=3600 (for index.html and other dynamic files)

4. **Environment Variable Updates:**
   - Add `REDIS_URL` if implementing a Redis cache

**Expected Outcome:**
- Optimal resource allocation
- Better handling of traffic spikes
- Reduced cold-start times

## Phase 4: Long-term Improvements

These changes require more significant architectural modifications but provide substantial performance benefits.

### 4.1 Implement Redis Caching for Frequently Accessed Data

**Files to Create/Modify:**
- `/backend/app/services/redis_cache.py`
- `/backend/app/config.py` (update)

**Implementation:**

1. Add Redis dependency to requirements.txt:
```
redis==5.0.0
```

2. Create Redis cache service:
```python
# /backend/app/services/redis_cache.py
import json
import redis
from typing import Any, Dict, Optional, Union, List
from app.config import settings

class RedisCache:
    """Redis caching service for frequently accessed data."""

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.default_ttl = 3600  # 1 hour default TTL

    def get(self, key: str) -> Optional[Union[Dict, List]]:
        """Get a value from the cache."""
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: Union[Dict, List], ttl: Optional[int] = None) -> bool:
        """Set a value in the cache with optional TTL."""
        ttl = ttl or self.default_ttl
        return self.redis.setex(key, ttl, json.dumps(value))

    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        return bool(self.redis.delete(key))

    def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        keys = self.redis.keys(pattern)
        if keys:
            return self.redis.delete(*keys)
        return 0

# Create a singleton instance
redis_cache = RedisCache()
```

3. Use Redis caching for study data:
```python
# In studies.py
from app.services.redis_cache import redis_cache

@router.get("/", response_model=List[StudyResponse])
def list_studies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all HAZOP studies (organization-isolated)"""
    # Try to get from cache
    cache_key = f"org:{current_user.organization_id}:studies"
    cached_data = redis_cache.get(cache_key)

    if cached_data:
        return cached_data

    # Not in cache, query database
    studies = db.query(HazopStudy).filter(
        HazopStudy.organization_id == current_user.organization_id
    ).all()

    # Prepare response
    response_data = [
        {
            "id": str(study.id),
            "title": study.title,
            "description": study.description,
            "facility_name": study.facility_name,
            "status": study.status,
            "created_at": study.created_at
        }
        for study in studies
    ]

    # Cache the result (TTL: 5 minutes)
    redis_cache.set(cache_key, response_data, 300)

    return response_data
```

4. Invalidate cache on updates:
```python
@router.post("/", response_model=StudyResponse)
def create_study(
    req: CreateStudyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new HAZOP study (organization-isolated)"""
    study = HazopStudy(
        title=req.title,
        description=req.description,
        facility_name=req.facility_name,
        created_by=current_user.id,
        organization_id=current_user.organization_id
    )
    db.add(study)
    db.commit()
    db.refresh(study)

    # Invalidate studies list cache
    redis_cache.delete(f"org:{current_user.organization_id}:studies")

    return study
```

**Expected Outcome:**
- Significantly faster response times for frequent operations
- Reduced database load for read-heavy operations
- Improved scaling under load

### 4.2 Implement Frontend State Management Optimizations

**Files to Create/Modify:**
- `/frontend/src/store/studyStore.ts` (new)
- `/frontend/src/store/deviationStore.ts` (new)
- `/frontend/src/pages/StudyDetail.tsx` (update)
- `/frontend/src/components/HAZOPAnalysis.tsx` (update)

**Implementation:**

1. Create optimized state stores with Zustand:
```typescript
// /frontend/src/store/studyStore.ts
import { create } from 'zustand';
import axios from 'axios';
import { Study, Node } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface StudyState {
  studies: Study[];
  currentStudy: Study | null;
  nodes: Node[];
  isLoading: boolean;
  error: string | null;
  fetchStudies: () => Promise<void>;
  fetchStudy: (studyId: string) => Promise<void>;
  fetchNodes: (studyId: string) => Promise<void>;
}

export const useStudyStore = create<StudyState>((set, get) => ({
  studies: [],
  currentStudy: null,
  nodes: [],
  isLoading: false,
  error: null,

  fetchStudies: async () => {
    set({ isLoading: true, error: null });
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      set({ studies: response.data, isLoading: false });
    } catch (err) {
      console.error('Failed to fetch studies:', err);
      set({ error: 'Failed to load studies', isLoading: false });
    }
  },

  fetchStudy: async (studyId: string) => {
    set({ isLoading: true, error: null });
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies/${studyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      set({ currentStudy: response.data, isLoading: false });
    } catch (err) {
      console.error('Failed to fetch study:', err);
      set({ error: 'Failed to load study', isLoading: false });
    }
  },

  fetchNodes: async (studyId: string) => {
    set({ isLoading: true, error: null });
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies/${studyId}/nodes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      set({ nodes: response.data, isLoading: false });
    } catch (err) {
      console.error('Failed to fetch nodes:', err);
      set({ error: 'Failed to load nodes', isLoading: false });
    }
  }
}));
```

2. Create deviation store:
```typescript
// /frontend/src/store/deviationStore.ts
import { create } from 'zustand';
import axios from 'axios';
import { Deviation, Cause, Consequence, Safeguard, Recommendation } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface DeviationState {
  deviations: Deviation[];
  selectedDeviation: Deviation | null;
  causes: Cause[];
  consequences: Consequence[];
  safeguards: Safeguard[];
  recommendations: Recommendation[];
  isLoading: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;
  fetchDeviations: (nodeId: string) => Promise<void>;
  selectDeviation: (deviation: Deviation) => void;
  loadHazopData: (deviationId: string) => Promise<void>;
  markSaved: () => void;
}

export const useDeviationStore = create<DeviationState>((set, get) => ({
  deviations: [],
  selectedDeviation: null,
  causes: [],
  consequences: [],
  safeguards: [],
  recommendations: [],
  isLoading: false,
  error: null,
  hasUnsavedChanges: false,

  fetchDeviations: async (nodeId: string) => {
    set({ isLoading: true, error: null });
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies/nodes/${nodeId}/deviations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      set({ deviations: response.data, isLoading: false });
    } catch (err) {
      console.error('Failed to fetch deviations:', err);
      set({ error: 'Failed to load deviations', isLoading: false });
    }
  },

  selectDeviation: (deviation: Deviation) => {
    set({
      selectedDeviation: deviation,
      causes: [],
      consequences: [],
      safeguards: [],
      recommendations: [],
      hasUnsavedChanges: false
    });
  },

  loadHazopData: async (deviationId: string) => {
    set({ isLoading: true, error: null });
    try {
      const token = localStorage.getItem('token');

      // Fetch all data in parallel for better performance
      const [causesRes, consequencesRes, safeguardsRes, recommendationsRes] = await Promise.all([
        axios.get(`${API_URL}/api/hazop/deviations/${deviationId}/causes`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/hazop/deviations/${deviationId}/consequences`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/hazop/deviations/${deviationId}/safeguards`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/hazop/deviations/${deviationId}/recommendations`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      set({
        causes: causesRes.data,
        consequences: consequencesRes.data,
        safeguards: safeguardsRes.data,
        recommendations: recommendationsRes.data,
        isLoading: false,
        hasUnsavedChanges: false
      });
    } catch (err) {
      console.error('Failed to load HAZOP data:', err);
      set({ error: 'Failed to load HAZOP data', isLoading: false });
    }
  },

  markSaved: () => {
    set({ hasUnsavedChanges: false });
  }
}));
```

3. Update components to use these stores.

**Expected Outcome:**
- More efficient state management
- Reduced prop drilling
- Better separation of UI and data logic
- Improved performance with parallel data loading

## Implementation Schedule

### Week 1: Critical Performance Improvements
- **Day 1-2:** Implement database optimizations (connection pooling, indexes)
- **Day 3-5:** Implement Gemini API caching

### Week 2: Frontend Optimizations
- **Day 1-3:** Implement code splitting and bundle optimization
- **Day 4-5:** Implement memoization for complex components

### Week 3: API and Backend Optimizations
- **Day 1-3:** Optimize API request/response handling
- **Day 4-5:** Configure Render.com service settings

### Week 4: Long-term Improvements
- **Day 1-3:** Implement Redis caching for frequently accessed data
- **Day 4-5:** Implement frontend state management optimizations

## Monitoring and Evaluation

To measure the impact of these optimizations:

1. **Performance Metrics to Track:**
   - Page load times (before/after)
   - API response times (before/after)
   - Database query times (before/after)
   - Gemini API costs (before/after)

2. **Monitoring Tools:**
   - Render.com dashboard metrics
   - Browser developer tools
   - Custom performance logging in backend

3. **Success Criteria:**
   - 50% reduction in API response times
   - 40% reduction in page load times
   - 70% reduction in Gemini API costs
   - Elimination of cold-start delays

## Conclusion

This optimization plan provides a comprehensive approach to significantly improve the performance of the HAZOP Software application on Render.com. By implementing these changes in phases, we can ensure a smooth transition with minimal disruption while achieving maximum performance gains.

The most critical improvements (database optimization, Gemini API caching, and frontend bundle optimization) should be implemented first to provide immediate benefits, followed by the other optimizations to further enhance performance.