# Gemini AI Insights - User Guide

**Last Updated**: October 13, 2025
**Status**: ✅ Fully Operational

---

## 🎉 Overview

The HAZOP Software now includes **Gemini AI integration** that provides intelligent suggestions for:
- **Causes** - What could trigger the deviation
- **Consequences** - What impacts could result from the deviation
- **Safeguards** - What controls can prevent or mitigate the deviation
- **Contextual Knowledge** - Industry standards, incidents, and best practices

---

## ✅ What Was Fixed

### Issue #1: Model Name Incompatibility
**Problem**: The old model name "gemini-pro" is no longer available
**Fix**: Updated to `models/gemini-2.5-flash` in [gemini_service.py:17](backend/app/services/gemini_service.py#L17)

### Issue #2: Safety Blocks
**Problem**: Gemini was blocking technical content about process hazards (finish_reason: 2)
**Fix**: Added safety_settings to allow technical/industrial content in [gemini_service.py:343-348](backend/app/services/gemini_service.py#L343-L348)

### Issue #3: Prompt Optimization
**Problem**: Complex prompts were triggering safety filters
**Fix**: Simplified prompts while maintaining technical accuracy

### Issue #4: "Add" Button Not Working (422 Error)
**Problem**: Clicking "Add" on AI suggestions returned 422 Unprocessable Entity error
**Root Cause**: Backend API endpoints expected parameters as function arguments instead of request body
**Fix**: Created Pydantic request models (`ApplyCauseSuggestionsRequest`, `ApplyConsequenceSuggestionsRequest`, `ApplySafeguardSuggestionsRequest`) in [gemini.py:200-212](backend/app/api/gemini.py#L200-L212)
**Status**: ✅ Fixed - All three endpoints now work correctly

---

## 📋 How to Use Gemini AI Insights

### Step 1: Access the HAZOP Analysis Page
1. Login to HAZOP Software at http://localhost:5173
2. Navigate to **Studies** page
3. Select or create a study
4. Click on a **Node** (e.g., "Centrifugal Pump P-101")
5. You'll see the **HAZOP Analysis** page

### Step 2: Create a Deviation
Click **"Add Deviation"** and fill in:
- **Parameter**: Flow, Pressure, Temperature, Level, etc.
- **Guide Word**: No, More, Less, As Well As, etc.
- **Description**: e.g., "No flow from pump P-101"

Click **Save**

### Step 3: Locate the Gemini AI Panel
Look for the **floating panel at the bottom-right** of the screen with:
- 🤖 Icon and "Gemini AI Insights" header
- Three tabs: **Causes**, **Consequences**, **Safeguards**
- 🔄 Refresh button
- ➕/➖ Expand/collapse button

### Step 4: Add Process Context (CRITICAL!)

**Why Context Matters**: The AI generates much better suggestions when it understands your specific process conditions.

1. Click **"+ Add Context"** button in the Gemini panel
2. Fill in the context form:

   ```
   Process Description: Centrifugal pump transferring process fluid
   Fluid Type: Crude oil
   Operating Conditions: 150°C, 5 bar
   Previous Incidents: Valve failed in 2018
   ```

3. Click **"Apply Context"** button

**Tips**:
- Be specific about operating conditions (temperature, pressure, flow rate)
- Mention the fluid properties (flammable, toxic, corrosive, etc.)
- Include any historical incidents or known issues
- Describe the process step (distillation, reaction, heat exchange, etc.)

### Step 5: Generate AI Suggestions

1. Select the appropriate tab:
   - **Causes Tab** - For root causes of the deviation
   - **Consequences Tab** - For impacts and outcomes
   - **Safeguards Tab** - For controls and mitigation measures

2. Click the **🔄 refresh button** in the panel header

3. Wait **3-5 seconds** for AI to process

4. Review the suggestions displayed

### Step 6: Review AI Suggestions

Each suggestion shows:
- **Text**: Detailed description of the cause/consequence/safeguard
- **Confidence**: 0-100% score indicating reliability
  - 90-100%: Very reliable, industry-standard
  - 70-89%: Likely, recommended
  - 50-69%: Possible, context-dependent
  - Below 50%: Additional consideration
- **Additional Metadata**:
  - For Consequences: Severity (Critical/High/Medium/Low), Category (Safety/Environmental/Operational/Economic)
  - For Safeguards: Type (Engineering/Detection/Administrative/Procedural), Effectiveness (High/Medium/Low)
  - For Causes: Reasoning explaining why this cause is relevant

### Step 7: Add Suggestions to Your Analysis

**⚠️ IMPORTANT - Hierarchical Workflow:**

The HAZOP structure is hierarchical:
```
Deviation → Causes → Consequences → Safeguards
```

**For Causes** (✅ Can add anytime):
- Click **"Add"** on any cause suggestion
- Or click **"Add All Suggestions"**
- Causes are added directly to the deviation

**For Consequences** (⚠️ Must select a Cause first):
1. **First**: Click on a **Cause** in the list above to select it (it will be highlighted in blue)
2. **Then**: Switch to **Consequences tab** in Gemini panel
3. Click **"Add"** on suggestions - they will link to the selected Cause
4. If you forget to select a cause, you'll see a warning message: ⚠️ "Select a Cause first..."

**For Safeguards** (⚠️ Must select a Consequence first):
1. **First**: Click on a **Cause** to expand it (▶ becomes ▼)
2. **Then**: Click on a **Consequence** to select it (it will be highlighted)
3. **Then**: Switch to **Safeguards tab** in Gemini panel
4. Click **"Add"** on suggestions - they will link to the selected Consequence
5. If you forget to select a consequence, you'll see a warning message: ⚠️ "Select a Consequence first..."

**Visual Indicators:**
- Selected items have a **blue background** highlight
- Warning messages appear if no parent is selected
- "Add All" button is **grayed out** when selection is required

### Step 8: Review and Edit

The AI suggestions are automatically added to your analysis, but you should:
- Review each suggestion for accuracy
- Edit descriptions to match your specific equipment/process
- Adjust confidence/severity/effectiveness ratings if needed
- Delete any suggestions that don't apply
- Verify the hierarchical structure is correct

---

## 📚 Contextual Knowledge (Auto-Generated)

The **Contextual Knowledge Panel** appears **below the deviation details** and provides:

### What It Includes:

1. **Regulations Tab**
   - ASME, API, OSHA, ISO standards
   - Relevant codes for your equipment type
   - Links to official documentation
   - Example: "ASME B31.3 Process Piping"

2. **Incident Reports Tab**
   - Historical incidents similar to your deviation
   - Date, facility, and description
   - Relevance explanation
   - Example: "Pump Seal Failure and Fire (2019-03-22)"

3. **Technical References Tab**
   - Engineering handbooks and guides
   - Design standards
   - Best practices
   - Example: "API 610: Centrifugal Pumps"

4. **Industry Benchmarks Tab**
   - Inspection frequencies
   - Testing intervals
   - Maintenance schedules
   - Example: "Pressure Vessel Inspection: External 5 years, Internal 10 years"

### How It Works:

The system automatically detects:
- **Equipment Types**: Pumps, vessels, piping, reactors, heat exchangers
- **Parameters**: Pressure, temperature, flow, level
- **Guide Words**: No, more, less, high, low

And provides relevant regulations, incidents, and references based on these detections.

---

## 🧪 Test Results

Here's what the AI generated for the test case:

### Test Scenario:
- **Deviation**: "No flow from pump P-101"
- **Equipment**: Centrifugal Pump
- **Process**: Crude oil transfer
- **Conditions**: 150°C, 5 bar
- **History**: Valve failed in 2018

### AI-Generated Results:

#### 5 Causes (95-80% confidence):
1. ✅ Suction/discharge valve closed or failed (95%)
2. ✅ Pump motor tripped (95%)
3. ✅ Suction strainer plugged with wax/coke (90%)
4. ✅ Insufficient NPSH causing vapor lock (85%)
5. ✅ Impeller damaged or blocked (80%)

#### 4 Consequences (95-85% confidence):
1. ✅ Hot crude oil release/fire (95%, High, Safety)
2. ✅ Production loss/shutdown (90%, High, Operational)
3. ✅ Pump mechanical damage (95%, Medium, Economic)
4. ✅ Upstream vessel overfill (85%, Medium, Operational)

#### 5 Safeguards (95-85% confidence):
1. ✅ Low flow alarm/trip (95%, High, Detection)
2. ✅ Low pressure alarm/trip (90%, High, Detection)
3. ✅ Valve position interlock (90%, High, Engineering)
4. ✅ Preventive maintenance program (90%, High, Administrative)
5. ✅ Motor current monitoring (85%, Medium, Detection)

---

## 🎯 Tips for Best Results

### 1. Provide Detailed Context
**Good**:
```
Process Description: Continuous distillation column separating crude oil
Fluid Type: Crude oil (heavy, contains H2S, corrosive)
Operating Conditions: 350°C, 15 bar, 100 m³/hr
Previous Incidents: Corrosion-induced leak in 2020, required 2-week shutdown
```

**Bad**:
```
Process Description: Column
Fluid Type: Oil
Operating Conditions: Hot
Previous Incidents: None
```

### 2. Use Descriptive Node Names
**Good**:
- "Centrifugal Pump P-101"
- "Distillation Column T-201"
- "Heat Exchanger E-301"
- "Pressure Relief Valve PSV-401"

**Bad**:
- "Node 1"
- "Equipment A"
- "Unit 5"

### 3. Be Specific in Deviation Descriptions
**Good**:
- "No flow from pump due to blocked suction strainer"
- "High pressure in vessel due to blocked outlet"
- "Low temperature in reactor due to cooling system failure"

**Bad**:
- "No flow"
- "High pressure"
- "Low temperature"

### 4. Review Confidence Scores
- **>90%**: Very reliable, industry-standard scenarios
- **70-89%**: Likely scenarios, recommended for consideration
- **50-69%**: Possible scenarios, depends on specific conditions
- **<50%**: Additional considerations, review carefully

### 5. Always Edit and Customize
AI suggestions are **starting points**, not final answers:
- ✅ Review for technical accuracy
- ✅ Adjust to match your specific equipment
- ✅ Add company-specific procedures/standards
- ✅ Consider your process-specific conditions
- ✅ Delete irrelevant suggestions

### 6. Use All Three Tabs
Don't just use one tab - get comprehensive coverage:
1. Start with **Causes** tab
2. Then **Consequences** tab
3. Finally **Safeguards** tab

This ensures you have a complete HAZOP analysis.

### 7. Iterate and Refine
- Add context → Generate suggestions → Review
- If suggestions aren't relevant, add more context
- If suggestions are too generic, be more specific
- Try different phrasings in context fields

---

## 🔧 How to Test Gemini AI

### Manual Testing via UI:
1. Start the application:
   ```bash
   # Terminal 1 - Backend
   cd /Users/nayyershahzad/HAZOP-Software/backend
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000

   # Terminal 2 - Frontend
   cd /Users/nayyershahzad/HAZOP-Software/frontend
   npm run dev
   ```

2. Navigate to http://localhost:5173
3. Follow Steps 1-7 above

### Automated Testing via Script:
```bash
cd /Users/nayyershahzad/HAZOP-Software
python3 test_gemini_insights.py
```

This script tests all three endpoints (causes, consequences, safeguards) plus contextual knowledge.

---

## 📊 API Endpoints

For developers or advanced users:

### Suggest Causes
```http
POST /api/gemini/suggest-causes
Content-Type: application/json
Authorization: Bearer <token>

{
  "deviation_id": "uuid-of-deviation",
  "context": {
    "process_description": "...",
    "fluid_type": "...",
    "operating_conditions": "...",
    "previous_incidents": "..."
  }
}
```

### Suggest Consequences
```http
POST /api/gemini/suggest-consequences
Content-Type: application/json
Authorization: Bearer <token>

{
  "deviation_id": "uuid-of-deviation",
  "cause_id": "uuid-of-cause",  // optional
  "context": { ... }
}
```

### Suggest Safeguards
```http
POST /api/gemini/suggest-safeguards
Content-Type: application/json
Authorization: Bearer <token>

{
  "deviation_id": "uuid-of-deviation",
  "cause_id": "uuid-of-cause",  // optional
  "consequence_id": "uuid-of-consequence",  // optional
  "context": { ... }
}
```

### Contextual Knowledge
```http
POST /api/gemini/contextual-knowledge
Content-Type: application/json
Authorization: Bearer <token>

{
  "node_id": "uuid-of-node",
  "deviation_id": "uuid-of-deviation",  // optional
  "context": { ... }
}
```

---

## ❓ Troubleshooting

### Problem: No suggestions appearing
**Solution**:
1. Check that backend is running: `curl http://localhost:8000/health`
2. Check backend logs: `tail -f /tmp/hazop-backend.log`
3. Verify API key in `backend/.env`: `GEMINI_API_KEY=...`
4. Try adding more context in the form

### Problem: "Invalid credentials" or "Unauthorized"
**Solution**:
1. Check that you're logged in
2. Verify token in browser localStorage
3. Try logging out and back in

### Problem: Suggestions are too generic
**Solution**:
1. Add more specific context
2. Use more descriptive deviation descriptions
3. Include operating conditions and fluid properties

### Problem: AI suggestions seem wrong
**Solution**:
1. AI is generating **starting points**, not final answers
2. Review and edit suggestions for your specific case
3. Delete irrelevant suggestions
4. Consider lower confidence suggestions with caution (<70%)

### Problem: Backend not starting
**Solution**:
```bash
cd /Users/nayyershahzad/HAZOP-Software/backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🔐 API Key Setup

If you need to set up a new Gemini API key:

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Edit `backend/.env`:
   ```
   GEMINI_API_KEY=your-new-api-key-here
   ```
5. Restart backend server

---

## 📈 Future Enhancements

Potential improvements for the AI system:

1. **Fine-tuning**: Train on historical HAZOP data from your facility
2. **Custom Prompts**: Allow users to customize AI prompts
3. **Batch Processing**: Generate suggestions for all deviations at once
4. **Export**: Export AI suggestions to Excel/Word reports
5. **Learning**: Learn from user edits to improve future suggestions
6. **Multi-language**: Support for non-English prompts and responses
7. **Integration**: Connect to external incident databases (CSB, ARIA)

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Review the backend logs: `/tmp/hazop-backend.log`
3. Check the [CLAUDE.md](CLAUDE.md) file for detailed technical information
4. Review the [QUICK_START.md](QUICK_START.md) for setup instructions

---

## ✅ Verification Checklist

Before starting a HAZOP session with AI:
- [ ] Backend running: `curl http://localhost:8000/health`
- [ ] Frontend running: http://localhost:5173
- [ ] Gemini API key configured in `backend/.env`
- [ ] Test user account created
- [ ] At least one study and node created
- [ ] Context form filled out with specific details
- [ ] All three tabs tested (Causes, Consequences, Safeguards)

---

**End of Guide** - Enjoy using AI-powered HAZOP analysis!
