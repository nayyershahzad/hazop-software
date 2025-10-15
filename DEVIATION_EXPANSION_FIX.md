# Deviation Expansion/Collapse Fix

**Date**: October 14, 2025
**Issue**: Deviations not opening when clicked after being collapsed
**Status**: ✅ **FIXED**

---

## Problem Identified

When trying to re-expand a previously collapsed deviation, it wouldn't show the HAZOP Analysis panel. This was due to inconsistent state management between `expandedDeviations` and `selectedDeviation`.

### Root Cause

The deviation render logic had two conflicting conditions:

**Line 504** (original):
```typescript
{expandedDeviations.has(dev.id) && selectedDeviation?.id === dev.id && (
  <HAZOPAnalysis ... />
)}
```

The HAZOP Analysis panel only shows when BOTH:
1. Deviation is in `expandedDeviations` set
2. Deviation is the `selectedDeviation`

**But the click handler had a bug** (lines 449-455):

```typescript
onClick={() => {
  if (!expandedDeviations.has(dev.id)) {
    handleDeviationClick(dev);  // ✅ Sets BOTH expandedDeviations AND selectedDeviation
  } else {
    toggleDeviationExpansion(dev.id);  // ❌ Only toggles expandedDeviations
  }
}}
```

### The Problem Flow

1. User clicks collapsed deviation → `handleDeviationClick()` → Sets both states ✅
2. User clicks ▼ to collapse → `toggleDeviationExpansion()` → Removes from expandedDeviations ✅
3. User clicks collapsed deviation again → `toggleDeviationExpansion()` → Adds to expandedDeviations ❌
   - **BUG**: `selectedDeviation` is NOT updated
   - Result: Condition fails, HAZOP panel doesn't show

---

## Solution Applied

### Fix 1: Unified Click Handler

**File**: `frontend/src/pages/StudyDetail.tsx`

Changed the main deviation header click to always use `handleDeviationClick()`:

**Before**:
```typescript
onClick={() => {
  if (!expandedDeviations.has(dev.id)) {
    handleDeviationClick(dev);
  } else {
    toggleDeviationExpansion(dev.id);
  }
}}
```

**After**:
```typescript
onClick={() => {
  // Always handle deviation click for proper state management
  handleDeviationClick(dev);
}}
```

### Fix 2: Enhanced handleDeviationClick Logic

Added logic to handle clicking an already-expanded deviation (to collapse it):

**Before**:
```typescript
const handleDeviationClick = (deviation: Deviation) => {
  if (hasUnsavedChanges && selectedDeviation && selectedDeviation.id !== deviation.id) {
    // Show confirmation dialog
    setPendingDeviation(deviation);
    setShowUnsavedWarning(true);
  } else {
    setSelectedDeviation(deviation);
    setHasUnsavedChanges(false);
    setExpandedDeviations(new Set([deviation.id]));
  }
};
```

**After**:
```typescript
const handleDeviationClick = (deviation: Deviation) => {
  // If clicking the same deviation that's already selected and expanded, collapse it
  if (selectedDeviation?.id === deviation.id && expandedDeviations.has(deviation.id)) {
    toggleDeviationExpansion(deviation.id);
    return;
  }

  // If there are unsaved changes and switching to a different deviation, show warning
  if (hasUnsavedChanges && selectedDeviation && selectedDeviation.id !== deviation.id) {
    setPendingDeviation(deviation);
    setShowUnsavedWarning(true);
  } else {
    setSelectedDeviation(deviation);
    setHasUnsavedChanges(false);
    setExpandedDeviations(new Set([deviation.id]));
  }
};
```

### Fix 3: Consistent Button Behavior

Changed the expand/collapse button (▶/▼) to also use `handleDeviationClick()`:

**Before**:
```typescript
<button
  onClick={(e) => {
    e.stopPropagation();
    toggleDeviationExpansion(dev.id);
  }}
>
  {expandedDeviations.has(dev.id) ? '▼' : '▶'}
</button>
```

**After**:
```typescript
<button
  onClick={(e) => {
    e.stopPropagation();
    handleDeviationClick(dev);
  }}
  title={expandedDeviations.has(dev.id) ? 'Collapse deviation' : 'Expand deviation'}
>
  {expandedDeviations.has(dev.id) ? '▼' : '▶'}
</button>
```

---

## What This Fixes

✅ **Deviations now open reliably** - Can expand/collapse any deviation multiple times
✅ **Consistent state management** - `selectedDeviation` and `expandedDeviations` always in sync
✅ **Better UX** - All click areas (header, button) behave the same way
✅ **Maintained safety** - Unsaved changes warning still works correctly

---

## New Behavior

### Scenario 1: Click Collapsed Deviation
- **Action**: Click on a collapsed deviation (▶)
- **Result**:
  - Deviation expands (▼)
  - HAZOP Analysis panel appears
  - Other deviations collapse
  - Sets both `selectedDeviation` and `expandedDeviations`

### Scenario 2: Click Expanded Deviation
- **Action**: Click on an already expanded deviation (▼)
- **Result**:
  - Deviation collapses (▶)
  - HAZOP Analysis panel hides
  - Clears from `expandedDeviations`

### Scenario 3: Re-expand Previously Collapsed
- **Action**: Click a deviation that was previously expanded and collapsed
- **Result**: ✅ **NOW WORKS!**
  - Deviation expands (▼)
  - HAZOP Analysis panel appears
  - Sets both states correctly

### Scenario 4: Click with Unsaved Changes
- **Action**: Click different deviation when current has unsaved changes
- **Result**:
  - Warning dialog appears
  - Must choose: Cancel or Switch Anyway
  - If switch, new deviation expands with correct state

---

## Testing Checklist

Test these scenarios:

- [ ] Click collapsed deviation → Opens with HAZOP panel ✅
- [ ] Click expanded deviation → Collapses and hides panel ✅
- [ ] Click ▶ button → Expands deviation ✅
- [ ] Click ▼ button → Collapses deviation ✅
- [ ] Expand, collapse, re-expand same deviation → Works ✅
- [ ] Switch between multiple deviations → Only one expanded ✅
- [ ] Make changes, try to switch → Warning appears ✅
- [ ] After warning, switch works correctly ✅

---

## Technical Details

### State Management

Two pieces of state control deviation expansion:

1. **`expandedDeviations: Set<string>`** - Tracks which deviations are visually expanded
   - Used for UI styling (blue border, blue background)
   - Controls collapse/expand animation

2. **`selectedDeviation: Deviation | null`** - The deviation being analyzed
   - Used to load HAZOP Analysis component
   - Passed to HAZOPAnalysis component

**Both must be synchronized** for the UI to work correctly.

### Single Source of Truth

By routing all clicks through `handleDeviationClick()`, we ensure:
- ✅ State changes happen in one place
- ✅ Unsaved changes check happens consistently
- ✅ Both state variables updated together
- ✅ Easy to debug and maintain

---

## Code Changed

**File**: `frontend/src/pages/StudyDetail.tsx`

**Lines modified**:
- Line 210-230: Enhanced `handleDeviationClick()` function
- Line 449-452: Simplified main click handler
- Line 464-473: Updated expand/collapse button

**Total changes**: ~15 lines modified

---

## Rollback Instructions

If you need to revert:

```bash
cd /Users/nayyershahzad/HAZOP-Software
git diff frontend/src/pages/StudyDetail.tsx
git checkout frontend/src/pages/StudyDetail.tsx
```

---

## Related Issues Fixed

This also improves:
- ✅ More intuitive clicking behavior
- ✅ Consistent expand/collapse experience
- ✅ Better tooltip on button ("Collapse deviation" / "Expand deviation")
- ✅ All click areas work identically

---

**Status**: ✅ Fix applied
**Testing**: Ready for user verification
**Hot Reload**: Changes will apply automatically in browser
