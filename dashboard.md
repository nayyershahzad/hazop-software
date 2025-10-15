# HAZOP Study Dashboard - Implementation Plan

**Created**: October 14, 2025
**Purpose**: Study-specific dashboard with visual analytics and Excel export
**Status**: Planning Phase

---

## 📊 Dashboard Overview

A comprehensive, interactive dashboard for each HAZOP study showing:
- Visual analytics with charts (donut, bar, progress)
- Study progress and completion metrics
- Risk distribution and severity analysis
- Quick navigation to specific nodes/deviations
- Excel export functionality for complete HAZOP worksheets

---

## 🎯 Key Features

### 1. Visual Analytics

**Completion Metrics**
- Total nodes, deviations, causes, consequences, safeguards, recommendations
- Progress indicators (% complete)
- Status badges (In Progress, Completed, Pending Review)

**Risk Analysis Charts**
- **Donut Chart**: Risk Level Distribution (Low/Medium/High/Critical)
- **Bar Chart**: Deviations by Node
- **Horizontal Bar**: Top 5 Most Critical Deviations
- **Gauge Chart**: Overall Study Risk Score

**Category Breakdown**
- **Pie Chart**: Consequences by Category (Safety/Environmental/Operational/Economic)
- **Stacked Bar**: Safeguards by Type (Engineering/Detection/Administrative/Procedural)
- **Timeline**: Study progress over time

### 2. Interactive Navigation

**Nodes Grid View**
- Card-based layout with node summaries
- Click to navigate directly to node detail
- Visual indicators: risk level color coding
- Quick stats: # deviations, # causes, completion %

**Deviations List View**
- Sortable table with key information
- Filters: by node, by risk level, by parameter
- Click to navigate directly to deviation analysis
- Search functionality

**Recent Activity Feed**
- Last 10 modifications
- User attribution
- Quick links to modified items

### 3. Excel Export

**Single Sheet Export** (Simple)
- All deviations with causes/consequences/safeguards in flat table
- One row per cause-consequence-safeguard combination
- Columns: Node, Deviation, Parameter, Guide Word, Cause, Consequence, Safeguard, Recommendation, Risk

**Multi-Sheet Workbook** (Detailed)
- Sheet 1: Study Summary
- Sheet 2: Nodes
- Sheet 3: Deviations
- Sheet 4: Causes
- Sheet 5: Consequences
- Sheet 6: Safeguards
- Sheet 7: Recommendations
- Sheet 8: Risk Assessments

**Formatted Export** (Professional)
- Styled headers (bold, colored)
- Auto-width columns
- Conditional formatting for risk levels
- Frozen header rows
- Filter dropdown on headers

---

## 🎨 Design Specifications

### Layout

```
┌─────────────────────────────────────────────────────┐
│  Study Header                                       │
│  [Study Name] - [Facility]                         │
│  [Export to Excel] [Print] [Share]                 │
├─────────────────────────────────────────────────────┤
│  Key Metrics (4 Cards)                              │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐              │
│  │Nodes │ │Devs. │ │Causes│ │Risks │              │
│  │  12  │ │  45  │ │ 120  │ │ 🔴15 │              │
│  └──────┘ └──────┘ └──────┘ └──────┘              │
├─────────────────────────────────────────────────────┤
│  Charts Row 1                                       │
│  ┌──────────────────┐  ┌──────────────────────┐   │
│  │ Risk Distribution│  │ Deviations by Node   │   │
│  │  (Donut Chart)   │  │   (Bar Chart)        │   │
│  └──────────────────┘  └──────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  Charts Row 2                                       │
│  ┌──────────────────┐  ┌──────────────────────┐   │
│  │ Consequence Cat. │  │ Top Critical Devs.   │   │
│  │   (Pie Chart)    │  │ (Horizontal Bar)     │   │
│  └──────────────────┘  └──────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  Nodes Overview (Grid)                              │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                      │
│  │N-01│ │N-02│ │N-03│ │N-04│  → Click to navigate │
│  └────┘ └────┘ └────┘ └────┘                      │
├─────────────────────────────────────────────────────┤
│  Deviations Table (Interactive)                     │
│  [Search] [Filter by: All Nodes ▼] [Risk: All ▼]  │
│  ┌──────┬─────────┬──────────┬──────┬──────────┐  │
│  │ Node │ Param   │ GuideWord│ Risk │ Actions  │  │
│  ├──────┼─────────┼──────────┼──────┼──────────┤  │
│  │ P-101│ Flow    │ No       │ 🔴   │ [View]   │  │
│  └──────┴─────────┴──────────┴──────┴──────────┘  │
└─────────────────────────────────────────────────────┘
```

### Color Scheme

**Risk Levels**
- 🔴 Critical: `bg-red-600`, `text-red-100`
- 🟠 High: `bg-orange-500`, `text-orange-100`
- 🟡 Medium: `bg-yellow-500`, `text-yellow-100`
- 🟢 Low: `bg-green-500`, `text-green-100`

**Charts**
- Primary: Blue (`#3B82F6`)
- Secondary: Purple (`#8B5CF6`)
- Accent: Teal (`#14B8A6`)
- Danger: Red (`#EF4444`)
- Warning: Orange (`#F59E0B`)
- Success: Green (`#10B981`)

### Typography
- Header: `text-3xl font-bold`
- Subheader: `text-xl font-semibold`
- Body: `text-base`
- Small: `text-sm`
- Tiny: `text-xs`

---

## 🛠️ Technical Implementation

### Frontend Components

**1. StudyDashboard.tsx** (Main Component)
- Location: `frontend/src/pages/StudyDashboard.tsx`
- Route: `/studies/:studyId/dashboard`
- Fetches all study data on mount
- Renders metrics, charts, and navigation elements

**2. DashboardMetricCard.tsx** (Reusable)
- Displays single metric with icon and count
- Props: title, value, icon, color, trend (optional)
- Example: Nodes card, Deviations card

**3. RiskDistributionChart.tsx** (Chart Component)
- Donut chart using recharts library
- Data: count of deviations by risk level
- Interactive: hover for details, click for drill-down

**4. DeviationsByNodeChart.tsx** (Chart Component)
- Bar chart using recharts
- X-axis: Node names
- Y-axis: Number of deviations
- Click bar to navigate to node

**5. ConsequenceCategoryChart.tsx** (Chart Component)
- Pie chart using recharts
- Data: count of consequences by category
- Color-coded by category type

**6. NodesGridView.tsx** (Grid Component)
- Responsive grid of node cards
- Each card shows: node name, deviation count, risk indicator
- Click to navigate to node detail

**7. DeviationsTableView.tsx** (Table Component)
- Sortable, filterable table
- Columns: Node, Parameter, Guide Word, Description, Risk, Actions
- Search bar and filter dropdowns
- Pagination (20 per page)

**8. ExcelExportButton.tsx** (Export Component)
- Dropdown with export options: Simple, Detailed, Formatted
- Uses `xlsx` library for Excel generation
- Downloads file: `{study_name}_HAZOP_{date}.xlsx`

### Backend Endpoints

**Dashboard Data Endpoint**
```
GET /api/studies/{study_id}/dashboard
Response:
{
  "study": { ... },
  "metrics": {
    "total_nodes": 12,
    "total_deviations": 45,
    "total_causes": 120,
    "total_consequences": 180,
    "total_safeguards": 150,
    "total_recommendations": 90,
    "risk_distribution": {
      "critical": 15,
      "high": 20,
      "medium": 8,
      "low": 2
    },
    "deviations_by_node": [
      { "node_id": "...", "node_name": "P-101", "count": 5 },
      ...
    ],
    "consequences_by_category": {
      "safety": 60,
      "environmental": 40,
      "operational": 50,
      "economic": 30
    },
    "completion_percentage": 75,
    "critical_deviations": [
      { "id": "...", "node_name": "P-101", "parameter": "Flow", ... },
      ...
    ]
  }
}
```

**Excel Export Endpoint**
```
GET /api/studies/{study_id}/export/excel?format=simple|detailed|formatted
Response: Binary Excel file
Headers:
  Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  Content-Disposition: attachment; filename="Study_Name_HAZOP_20251014.xlsx"
```

### Libraries to Install

**Frontend**
```bash
npm install recharts xlsx file-saver
npm install @types/file-saver --save-dev
```

**Backend**
```bash
pip install openpyxl xlsxwriter
```

---

## 📋 Implementation Steps

### Phase 1: Dashboard Page Setup (2 hours)

1. Create route and navigation
2. Create StudyDashboard.tsx skeleton
3. Fetch basic study data
4. Display study header

### Phase 2: Metrics Cards (1 hour)

1. Create DashboardMetricCard component
2. Fetch metrics from backend
3. Display 4-6 key metrics

### Phase 3: Charts Implementation (3 hours)

1. Install recharts library
2. Create RiskDistributionChart (donut)
3. Create DeviationsByNodeChart (bar)
4. Create ConsequenceCategoryChart (pie)
5. Add chart interactions (hover, click)

### Phase 4: Navigation Components (2 hours)

1. Create NodesGridView component
2. Create DeviationsTableView component
3. Implement click-to-navigate functionality
4. Add search and filters

### Phase 5: Backend Dashboard Endpoint (2 hours)

1. Create `/api/studies/{study_id}/dashboard` endpoint
2. Aggregate data from database
3. Calculate metrics and distributions
4. Return structured JSON response

### Phase 6: Excel Export (3 hours)

1. Create ExcelExportButton component
2. Implement backend export endpoint
3. Generate simple Excel format
4. Generate detailed multi-sheet format
5. Add styling and formatting
6. Handle download on frontend

### Phase 7: Polish and Testing (1 hour)

1. Add loading states
2. Add error handling
3. Responsive design tweaks
4. Test navigation
5. Test Excel export
6. Performance optimization

**Total Estimated Time: 14 hours**

---

## 🎯 Success Criteria

✅ Dashboard loads within 2 seconds
✅ All charts render correctly with real data
✅ Clicking charts/cards navigates to correct page
✅ Excel export generates valid files
✅ Excel export includes all HAZOP data
✅ Dashboard is responsive (mobile, tablet, desktop)
✅ Visual design is professional and consistent

---

## 📐 Database Queries

### Risk Distribution
```sql
SELECT
  ia.risk_level,
  COUNT(*) as count
FROM impact_assessments ia
JOIN consequences c ON ia.consequence_id = c.id
JOIN deviations d ON c.deviation_id = d.id
JOIN hazop_nodes n ON d.node_id = n.id
WHERE n.study_id = :study_id
GROUP BY ia.risk_level
```

### Deviations by Node
```sql
SELECT
  n.id,
  n.node_name,
  COUNT(d.id) as deviation_count
FROM hazop_nodes n
LEFT JOIN deviations d ON n.id = d.node_id
WHERE n.study_id = :study_id
GROUP BY n.id, n.node_name
ORDER BY deviation_count DESC
```

### Consequences by Category
```sql
SELECT
  UNNEST(STRING_TO_ARRAY(c.category, ',')) as category,
  COUNT(*) as count
FROM consequences c
JOIN deviations d ON c.deviation_id = d.id
JOIN hazop_nodes n ON d.node_id = n.id
WHERE n.study_id = :study_id AND c.category IS NOT NULL
GROUP BY category
```

---

## 🚀 Future Enhancements

1. **Real-time Updates**: WebSocket for live dashboard updates
2. **Comparison**: Compare multiple studies side-by-side
3. **Trends**: Historical trend charts (risk over time)
4. **Heatmap**: Node-deviation risk heatmap
5. **PDF Export**: Generate PDF report with charts
6. **Custom Reports**: User-defined report templates
7. **Scheduling**: Schedule automated report generation
8. **Email**: Email dashboard summary to stakeholders
9. **Mobile App**: Native mobile dashboard
10. **AI Insights**: AI-generated observations and recommendations

---

## 📚 File Structure

```
frontend/src/
├── pages/
│   └── StudyDashboard.tsx          # Main dashboard page
├── components/
│   ├── dashboard/
│   │   ├── DashboardMetricCard.tsx
│   │   ├── RiskDistributionChart.tsx
│   │   ├── DeviationsByNodeChart.tsx
│   │   ├── ConsequenceCategoryChart.tsx
│   │   ├── NodesGridView.tsx
│   │   ├── DeviationsTableView.tsx
│   │   └── ExcelExportButton.tsx
│   └── ...

backend/app/
├── api/
│   ├── studies.py                  # Add dashboard endpoint
│   └── export.py                   # New: Excel export endpoints
├── services/
│   └── export_service.py           # New: Excel generation logic
└── ...
```

---

## ✅ Acceptance Testing

**Test Case 1: Dashboard Loads**
- Navigate to `/studies/:studyId/dashboard`
- Verify all metrics display correct numbers
- Verify all charts render

**Test Case 2: Navigation from Charts**
- Click on donut chart slice → Filter to that risk level
- Click on bar chart bar → Navigate to that node
- Click on node card → Navigate to node detail

**Test Case 3: Deviations Table**
- Search for deviation → Shows filtered results
- Filter by node → Shows only that node's deviations
- Filter by risk → Shows only that risk level
- Click "View" → Navigate to deviation detail

**Test Case 4: Excel Export**
- Click "Export to Excel" → Dropdown shows 3 options
- Click "Simple" → Downloads Excel file
- Open Excel → Verify data is correct
- Click "Formatted" → Downloads styled Excel
- Open Excel → Verify styling applied

---

## 🐛 Known Issues / Edge Cases

1. **Large Studies**: Studies with 1000+ deviations may take time to load
   - Solution: Add pagination, lazy loading

2. **Empty Study**: Study with no data shows empty charts
   - Solution: Show placeholder message "No data yet"

3. **Excel Size**: Very large studies may generate huge Excel files
   - Solution: Add file size warning, compress, or paginate export

4. **Browser Compatibility**: Charts may not render in old browsers
   - Solution: Add fallback table view

---

## 📝 Notes

- Use recharts for charts (lightweight, React-friendly)
- Use xlsx library for Excel generation (widely used, well-maintained)
- Dashboard should be read-only (no editing from dashboard)
- Cache dashboard data for 5 minutes to improve performance
- Add "Refresh" button to manually reload data

---

**Ready for Implementation**: ✅ YES
**Approved by**: [Pending]
**Start Date**: October 14, 2025
