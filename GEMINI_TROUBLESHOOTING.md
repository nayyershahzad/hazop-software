# Gemini AI Integration Troubleshooting Guide

**Created**: October 14, 2025
**Issue**: "No cause suggestions available. Click refresh to generate."
**Status**: ✅ Backend working, investigating frontend

---

## 🔍 Problem Description

You're seeing empty Gemini suggestions in the frontend with the message:
- "No cause suggestions available. Click refresh to generate."
- "No consequence suggestions available."
- "No recommendation suggestions available."

Even after:
- Filling in the context form with:
  - Process Description: Centrifugal pump transferring process fluid
  - Fluid Type: Crude oil
  - Operating Conditions: 150°C, 5 bar
  - Previous Incidents: Valve failed in 2018
- Clicking the refresh button (🔄)
- Waiting several seconds

---

## ✅ What We've Verified

### Backend is Working ✅
- Backend API is running on port 8000
- Gemini API key is configured correctly
- Direct API tests show Gemini is responding with suggestions
- Test results:
  ```
  ✅ Received 5 cause suggestions (95-85% confidence)
  ✅ Received 5 consequence suggestions
  ✅ Received 4 safeguard suggestions
  ```

### Frontend is Running ✅
- Frontend is running on port 5173
- Vite dev server is active
- UI is accessible

---

## 🎯 Diagnostic Tool

We've created a comprehensive diagnostic tool to help identify the issue:

### Run the Diagnostic Tool

```bash
cd /Users/nayyershahzad/HAZOP-Software
python3 test_gemini_frontend.py
```

This tool will:
1. ✅ Test backend health
2. ✅ Test authentication
3. ✅ Check data availability (studies/nodes/deviations)
4. ✅ Test Gemini API integration
5. ✅ Verify API key configuration

---

## 🔧 Common Issues & Solutions

### Issue 1: Context Not Being Sent

**Symptom**: Suggestions are empty or generic

**Solution**:
1. Make sure you click **"Apply Context"** after filling the form
2. Wait for a confirmation (the form should stay visible)
3. Then click the **refresh button (🔄)**
4. The context should be included in the API request

**How to verify**:
- Open browser DevTools (F12)
- Go to Network tab
- Click refresh in AI panel
- Look for request to `/api/gemini/suggest-causes`
- Check the payload - it should include a `context` object

### Issue 2: Authentication Token Expired

**Symptom**: Network error or 401 Unauthorized

**Solution**:
1. Logout from the app
2. Clear browser localStorage:
   ```javascript
   // In browser console (F12)
   localStorage.clear()
   ```
3. Login again
4. Try Gemini suggestions again

### Issue 3: Incorrect Deviation ID

**Symptom**: 404 Not Found error

**Solution**:
1. Make sure you're viewing a valid deviation
2. The deviation must be selected (expanded)
3. The AI Insights panel should show at the bottom-left
4. Try refreshing the entire page (Cmd+R / Ctrl+R)

### Issue 4: CORS or Network Issues

**Symptom**: Network request fails immediately

**Solution**:
1. Check that backend is running:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

2. Check that frontend API URL is correct:
   - Open `frontend/.env` or `frontend/.env.development`
   - Should have: `VITE_API_URL=http://localhost:8000`

3. Restart both servers:
   ```bash
   # Kill existing processes
   pkill -f uvicorn
   pkill -f vite

   # Start backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

   # Start frontend
   cd ../frontend
   npm run dev &
   ```

### Issue 5: Gemini API Rate Limiting

**Symptom**: First request works, subsequent requests return empty

**Solution**:
- Gemini has rate limits (15 requests per minute for free tier)
- Wait 1 minute between requests
- Or upgrade to paid tier for higher limits

### Issue 6: Safety Filters Blocking Content

**Symptom**: Gemini returns empty array or blocks the response

**Solution**:
- Try rephrasing your context to be less specific about hazardous scenarios
- Instead of: "Potential explosion and fire"
- Use: "Process upset and equipment damage"

**Note**: The backend already has safety settings configured to allow technical content, but some phrases may still trigger filters.

---

## 🧪 Manual Testing Steps

### Step 1: Test Backend API Directly

```bash
# Get a valid token first (replace email/password)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}'

# Copy the access_token from response

# Test suggest-causes endpoint
curl -X POST http://localhost:8000/api/gemini/suggest-causes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "deviation_id": "YOUR_DEVIATION_ID",
    "context": {
      "process_description": "Centrifugal pump transferring process fluid",
      "fluid_type": "Crude oil",
      "operating_conditions": "150°C, 5 bar",
      "previous_incidents": "Valve failed in 2018"
    }
  }'
```

**Expected Response**: JSON array with 3-5 cause suggestions

### Step 2: Check Browser Console

1. Open the HAZOP app in browser
2. Press F12 to open DevTools
3. Go to **Console** tab
4. Look for any errors in red
5. Common errors:
   - `CORS error` → Backend not running or wrong URL
   - `401 Unauthorized` → Token expired, login again
   - `404 Not Found` → Invalid deviation ID
   - `Network error` → Backend not accessible

### Step 3: Check Network Requests

1. Open DevTools (F12)
2. Go to **Network** tab
3. Click refresh button (🔄) in AI Insights panel
4. Look for request to `/api/gemini/suggest-causes`
5. Click on the request to see:
   - **Request Headers**: Should have `Authorization: Bearer ...`
   - **Request Payload**: Should have `deviation_id` and `context`
   - **Response**: Should have array of suggestions or error message
6. If response is empty array `[]`:
   - Check backend logs for errors
   - Try with different context
   - Wait 1 minute (rate limiting)

---

## 📋 Checklist for Troubleshooting

Before asking for help, verify:

- [ ] Backend is running: `curl http://localhost:8000/health`
- [ ] Frontend is running: Can access http://localhost:5173
- [ ] You're logged in (check localStorage for 'token')
- [ ] You have created: Study → Node → Deviation
- [ ] The deviation is expanded (selected)
- [ ] AI Insights panel is visible (bottom-left)
- [ ] AI Insights panel is expanded (not collapsed)
- [ ] You clicked "+ Add Context" button
- [ ] You filled in the context form
- [ ] You clicked "Apply Context" button
- [ ] You clicked the refresh button (🔄)
- [ ] You waited at least 5-10 seconds
- [ ] No errors in browser console (F12)
- [ ] Network request was sent (check Network tab)
- [ ] Network request returned 200 OK (not 401/404/500)

---

## 🔍 Debugging Frontend Code

If the issue persists, check these frontend files:

### 1. GeminiInsightsPanel.tsx

Location: `frontend/src/components/GeminiInsightsPanel.tsx`

Key function: `loadSuggestions()` (line 79)

This function:
- Constructs the API request
- Sends POST to `/api/gemini/suggest-causes` (or consequences/safeguards)
- Updates state with suggestions

**Check**:
- Is the function being called? (Add `console.log` at line 80)
- Is context being included? (Add `console.log(context)` at line 88)
- Is response.data an array? (Add `console.log(response.data)` at line 127)

### 2. API_URL Configuration

Location: `frontend/src/components/GeminiInsightsPanel.tsx` line 5

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

**Check**:
- Add `console.log('API_URL:', API_URL)` to see what URL is being used
- Should be: `http://localhost:8000`

### 3. useEffect Dependency Array

Location: `frontend/src/components/GeminiInsightsPanel.tsx` line 77

```typescript
useEffect(() => {
  if (deviation && !isCollapsed) {
    loadSuggestions();
  }
}, [deviation.id, selectedCauseId, selectedConsequenceId, insightType]);
```

This auto-loads suggestions when:
- Deviation changes
- Selected cause/consequence changes
- Tab changes (causes/consequences/recommendations)
- Panel is expanded

**Issue**: If panel is collapsed (`isCollapsed = true`), suggestions won't auto-load

**Solution**: Expand the panel first, then suggestions should load

---

## 🐛 Known Issues

### Issue: Auto-collapse on Deviation Switch

**Description**: When switching between deviations, the AI Insights panel auto-collapses and clears context.

**This is intentional** (as per line 69 in GeminiInsightsPanel.tsx):
```typescript
setIsCollapsed(true); // Auto-collapse when switching deviations
```

**Reason**: Prevents confusion by showing old suggestions for a different deviation.

**Workaround**: After switching deviations:
1. Expand AI panel manually
2. Add context again
3. Click refresh

---

## 💡 Quick Fix Attempts

### Fix 1: Hard Refresh the Browser

Sometimes the React state gets stale:

```
Cmd + Shift + R (Mac)
Ctrl + Shift + R (Windows/Linux)
```

This clears the cache and reloads everything.

### Fix 2: Clear React State

In browser console (F12):

```javascript
// Clear localStorage
localStorage.clear();

// Reload page
window.location.reload();
```

Then login and try again.

### Fix 3: Restart Everything

```bash
cd /Users/nayyershahzad/HAZOP-Software

# Kill all processes
pkill -f uvicorn
pkill -f vite
sleep 2

# Start backend
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/hazop-backend.log 2>&1 &

# Start frontend
cd ../frontend
nohup npm run dev > /tmp/hazop-frontend.log 2>&1 &

# Wait for startup
sleep 5

# Check logs
echo "Backend log:"
tail -20 /tmp/hazop-backend.log

echo "Frontend log:"
tail -20 /tmp/hazop-frontend.log
```

### Fix 4: Check Gemini API Key

```bash
cd /Users/nayyershahzad/HAZOP-Software/backend
cat .env | grep GEMINI_API_KEY
```

Should show:
```
GEMINI_API_KEY=AIzaSyDA9m4mrCyb_wppn9hKQCLIyVMj_d2ldI0
```

If missing or wrong, update `.env` and restart backend.

---

## 📞 Getting More Help

### Check Backend Logs

```bash
tail -f /tmp/hazop-backend.log | grep -E "(gemini|suggest|error|Error|ERROR)"
```

Look for:
- Gemini API errors
- Authentication errors
- Python exceptions
- HTTP status codes

### Check Frontend Logs

```bash
tail -f /tmp/hazop-frontend.log
```

Look for:
- Compilation errors
- Build warnings
- Vite errors

### Enable Debug Mode

Add debug logging to the frontend:

Edit `frontend/src/components/GeminiInsightsPanel.tsx`:

```typescript
// Add at the top of loadSuggestions() function (line 80)
console.log('🔍 Loading suggestions...', {
  insightType,
  deviationId: deviation.id,
  context: processContext,
  isCollapsed,
  selectedCauseId,
  selectedConsequenceId
});

// Add after response (line 136)
console.log('✅ Received response:', response.data);
```

Then check browser console for detailed logs.

---

## 📊 Test Results Summary

### Backend API Tests: ✅ PASSING

```
✅ Gemini service initialized
✅ Received 5 cause suggestions (95-85% confidence)
✅ Received 5 consequence suggestions
✅ Received 4 safeguard suggestions
```

Sample causes generated:
1. "Suction or discharge isolation valve is inadvertently or incorrectly closed" (95%)
2. "Loss of pump prime due to air ingress, low suction level, or..." (85%)
3. "Suction strainer or inlet line is blocked by debris, scale..." (90%)

### Conclusion

The **backend Gemini integration is working perfectly**. The issue is in the **frontend-to-backend communication** or **frontend state management**.

Most likely causes:
1. **Context not being sent** - User didn't click "Apply Context"
2. **Panel is collapsed** - Auto-collapses on deviation switch
3. **Token expired** - Need to re-login
4. **Network error** - CORS or connectivity issue
5. **React state issue** - Need hard refresh

---

## 🎯 Recommended Next Steps

1. **Run the diagnostic tool**:
   ```bash
   python3 test_gemini_frontend.py
   ```

2. **Check browser console** for errors (F12)

3. **Try the manual test**:
   - Open http://localhost:5173
   - Login
   - Go to a deviation
   - Open browser DevTools (F12)
   - Expand AI Insights panel
   - Click "+ Add Context"
   - Fill form and click "Apply Context"
   - Click refresh button (🔄)
   - Watch Network tab for request
   - Check Console tab for logs

4. **If still not working**, provide:
   - Browser console errors (screenshot)
   - Network tab request/response (screenshot)
   - Backend logs: `tail -50 /tmp/hazop-backend.log`

---

## ✅ Success Criteria

You'll know it's working when:

1. Click refresh button (🔄)
2. Panel shows "Loading..." spinner
3. After 5-10 seconds, suggestions appear
4. Each suggestion shows:
   - Description text
   - Confidence percentage
   - "Add" button (➕)
5. Clicking "Add" adds the item to your worksheet

---

**Last Updated**: October 14, 2025
**Tool Version**: 1.0
**Author**: Claude AI Assistant
