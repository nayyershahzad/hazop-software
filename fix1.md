# Remaining Features to Implement

**Date**: October 13, 2025
**Priority**: High

---

## 📋 Outstanding Tasks

Based on user requirements, the following features need to be implemented:

---

## 1. Data Persistence & Save Confirmation ⚠️ **HIGH PRIORITY**

### Problem Statement
**User Feedback**: *"There is a bug in the program, after working on a specific deviation, I add another node and then go back to the previous, all the data is lost. Data needs to be saved using a push button. Before moving to next deviation, ask user consent to save it."*

### Current Behavior
- Data is auto-saved when forms are submitted
- No explicit "Save" button for the entire deviation analysis
- When switching nodes/deviations, no warning is shown
- User may lose track of what has been saved

### Required Implementation

#### A. Add "Unsaved Changes" Detection
```typescript
// Track if user has made changes since last save
const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

// Set to true whenever user edits any field
// Set to false after successful save
```

#### B. Add Confirmation Dialog Before Navigation
```typescript
// When user tries to switch deviations/nodes
const handleDeviationSwitch = (newDeviationId: string) => {
  if (hasUnsavedChanges) {
    const confirmSwitch = confirm(
      "You have unsaved changes. Are you sure you want to switch? Your changes will be lost."
    );
    if (!confirmSwitch) {
      return; // Stay on current deviation
    }
  }
  // Proceed with switch
  loadDeviation(newDeviationId);
};
```

#### C. Add "Save All" Button
```typescript
// Add a prominent "Save All" button in the HAZOP Analysis header
<button
  onClick={handleSaveAll}
  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
>
  💾 Save Analysis
</button>
```

### Files to Modify
- `/frontend/src/components/HAZOPAnalysis.tsx` - Add save logic
- `/frontend/src/pages/StudyDetail.tsx` - Add navigation guard

---

## 2. Collapsible Deviation Sections 🔽

### Problem Statement
**User Feedback**: *"Another issue is that closing the previous deviation should collapse it in the Hazop worksheet after analyzing finished."*

### Required Implementation

#### A. Add Collapse/Expand State
```typescript
const [expandedDeviations, setExpandedDeviations] = useState<Set<string>>(new Set());

// Toggle function
const toggleDeviation = (deviationId: string) => {
  setExpandedDeviations(prev => {
    const newSet = new Set(prev);
    if (newSet.has(deviationId)) {
      newSet.delete(deviationId);
    } else {
      newSet.add(deviationId);
    }
    return newSet;
  });
};
```

#### B. Update UI to Show Collapse/Expand
```typescript
// Add collapse button in deviation header
<div className="flex justify-between items-center">
  <h3>Deviation: {deviation.parameter} / {deviation.guide_word}</h3>
  <button onClick={() => toggleDeviation(deviation.id)}>
    {expandedDeviations.has(deviation.id) ? '▼ Collapse' : '▶ Expand'}
  </button>
</div>

// Conditionally render deviation content
{expandedDeviations.has(deviation.id) && (
  <div>
    {/* HAZOP worksheet content */}
  </div>
)}
```

#### C. Auto-Collapse When Switching
```typescript
// When user selects a new deviation
const handleSelectDeviation = (newDeviationId: string) => {
  // Collapse current deviation
  setExpandedDeviations(prev => {
    const newSet = new Set(prev);
    if (currentDeviationId) {
      newSet.delete(currentDeviationId);
    }
    newSet.add(newDeviationId);
    return newSet;
  });

  setCurrentDeviationId(newDeviationId);
};
```

### Files to Modify
- `/frontend/src/components/HAZOPAnalysis.tsx` - Add collapse state
- `/frontend/src/pages/StudyDetail.tsx` - Manage deviation list

---

## 3. AI Insights Context Reset 🔄

### Problem Statement
**User Feedback**: *"Clicking new deviation should open this specific deviation hazop sheet, with AI insight collapsed waiting for user to put the new context for this new deviation."*

### Current Behavior
- AI Insights panel retains context when switching deviations
- Panel remains in whatever state it was (expanded/collapsed)
- May show stale suggestions from previous deviation

### Required Implementation

#### A. Reset Context on Deviation Switch
```typescript
// In HAZOPAnalysis component
useEffect(() => {
  // When deviation changes, reset AI panel
  resetAIInsightsPanel();
}, [deviation.id]);
```

#### B. Update GeminiInsightsPanel Component
```typescript
// Add reset function in GeminiInsightsPanel
const resetPanel = () => {
  setProcessContext({
    process_description: '',
    fluid_type: '',
    operating_conditions: '',
    previous_incidents: ''
  });
  setSuggestedCauses([]);
  setSuggestedConsequences([]);
  setSuggestedRecommendations([]);
  setIsCollapsed(true); // Auto-collapse
};

// Expose reset via props
useImperativeHandle(ref, () => ({
  reset: resetPanel
}));
```

#### C. Auto-Collapse AI Panel
```typescript
// When switching deviations
const handleDeviationSwitch = (newDeviationId: string) => {
  // Collapse AI Insights panel
  aiInsightsPanelRef.current?.reset();

  // Load new deviation
  loadDeviation(newDeviationId);
};
```

### Files to Modify
- `/frontend/src/components/HAZOPAnalysis.tsx` - Add reset call
- `/frontend/src/components/GeminiInsightsPanel.tsx` - Add reset function

---

## 4. AI Response Caching 💰

### Problem Statement
**User Feedback**: *"Also ensure that we don't call Gemini again and again and some data could be in the cache to limit the cost."*

### Cost Analysis
- Gemini 2.5 Flash: $0.075 per 1M input tokens, $0.30 per 1M output tokens
- Average request: ~500 tokens input, ~1000 tokens output
- Cost per request: ~$0.0004
- **1000 calls = $0.40** (without caching)
- **With caching: 50-80% cost reduction**

### Required Implementation

#### A. Backend Caching Layer

Create new file: `/backend/app/services/gemini_cache.py`

```python
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import GeminiCache

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
            return json.loads(cached.response_data)
        return None

    def cache_response(self, deviation_id: str, context: Dict, suggestion_type: str, response: Dict[str, Any]):
        """Cache API response"""
        cache_key = self._generate_cache_key(deviation_id, context, suggestion_type)
        expires_at = datetime.utcnow() + self.cache_ttl

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
```

#### B. Database Migration for Cache Table

Create: `/backend/migrations/006_gemini_cache.sql`

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

#### C. Update Gemini Service to Use Cache

Update: `/backend/app/services/gemini_service.py`

```python
from app.services.gemini_cache import GeminiCacheService

class GeminiService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = GeminiCacheService(db)
        # ... existing init code

    async def suggest_causes(self, deviation_id: str, context: Dict):
        # Check cache first
        cached_response = self.cache.get_cached_response(
            deviation_id,
            context,
            'causes'
        )

        if cached_response:
            print(f"✅ Cache hit for causes (deviation: {deviation_id})")
            return cached_response

        # Cache miss - call Gemini API
        print(f"❌ Cache miss - calling Gemini API for causes")
        response = await self._call_gemini_api(deviation_id, context, 'causes')

        # Cache the response
        self.cache.cache_response(deviation_id, context, 'causes', response)

        return response
```

#### D. Frontend Indicator for Cached Responses

Update: `/frontend/src/components/GeminiInsightsPanel.tsx`

```typescript
// Show indicator when response is from cache
{suggestion.cached && (
  <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full ml-2">
    💾 Cached
  </span>
)}
```

### Files to Create/Modify
- **NEW**: `/backend/app/services/gemini_cache.py` - Cache service
- **NEW**: `/backend/app/models/gemini_cache.py` - Cache model
- **NEW**: `/backend/migrations/006_gemini_cache.sql` - Database table
- **MODIFY**: `/backend/app/services/gemini_service.py` - Add caching
- **MODIFY**: `/backend/app/api/gemini.py` - Return cache status
- **MODIFY**: `/frontend/src/components/GeminiInsightsPanel.tsx` - Show cache indicator

### Expected Cost Savings
- **Without cache**: 1000 calls = $0.40
- **With cache (70% hit rate)**: 300 calls = $0.12
- **Savings**: $0.28 (70%)

---

## Implementation Priority

### Immediate (Do First)
1. ✅ **JSX Syntax Fix** - COMPLETED
2. 🔥 **Data Persistence & Save Confirmation** - CRITICAL BUG FIX

### High Priority (Do Next)
3. 🔄 **AI Insights Context Reset** - User Experience Issue
4. 🔽 **Collapsible Deviation Sections** - User Experience Issue

### Medium Priority (Do After)
5. 💰 **AI Response Caching** - Cost Optimization

---

## Testing Checklist

### Data Persistence
- [ ] Warning appears when trying to switch deviations with unsaved changes
- [ ] "Save All" button saves all current deviation data
- [ ] No data loss when switching between nodes
- [ ] Confirmation dialog works correctly

### Collapsible Sections
- [ ] Deviations can be collapsed/expanded
- [ ] Current deviation auto-expands when selected
- [ ] Previous deviation auto-collapses when switching
- [ ] Collapse state persists during session

### AI Context Reset
- [ ] AI Insights panel collapses when switching deviations
- [ ] Context form clears when switching deviations
- [ ] Previous suggestions clear when switching deviations
- [ ] User can enter new context for new deviation

### Caching
- [ ] Cache hit indicator appears for cached responses
- [ ] Cache misses trigger new API calls
- [ ] Cached responses are identical to fresh responses
- [ ] Cache expires after 7 days
- [ ] Cache invalidates when deviation is updated

---

## Estimated Implementation Time

- **Data Persistence**: 2-3 hours
- **Collapsible Sections**: 1-2 hours
- **AI Context Reset**: 1 hour
- **AI Response Caching**: 3-4 hours

**Total**: 7-10 hours

---

## Next Steps

1. Fix JSX syntax errors (DONE ✅)
2. Implement data persistence & save confirmation
3. Add collapsible deviation sections
4. Implement AI context reset
5. Add AI response caching layer

---

**Ready to proceed with implementation!**
