# Quick Start Guide - HAZOP with Gemini AI

## ✅ Status: Both Servers Running!

- **Backend**: http://localhost:8000 ✅
- **Frontend**: http://localhost:5173 ✅

---

## 🚀 Access Your Application

**Open in browser**: http://localhost:5173

---

## 📝 What You Need to Do

### 1. Create Your First Study (Data was reset)

Since the database was reset during troubleshooting, you need to:

1. **Register/Login** at http://localhost:5173
2. **Create a HAZOP Study**:
   - Click "New Study"
   - Enter study name and description
3. **Add Nodes** to your study
4. **Add Deviations** to each node
5. **Add Causes, Consequences, Safeguards**

### 2. Test Gemini AI Features

Once you have a deviation:

**Gemini Insights Panel** (bottom-right):
- Click "+ Add Context" to provide process details
- Fill in:
  - Process description: e.g., "Crude oil distillation"
  - Fluid type: e.g., "Crude oil"
  - Operating conditions: e.g., "150°C, 5 bar"
- Click "Apply Context"
- Switch between Causes/Consequences/Safeguards tabs
- Review AI suggestions and click "Add" to apply them

**Contextual Knowledge Panel** (below deviation):
- Automatically appears when you view a deviation
- Click to expand
- Browse regulations, incidents, technical refs, and benchmarks

---

## 🔧 If You Need to Restart Servers

### Stop Everything:
```bash
pkill -f uvicorn
pkill -f vite
```

### Start Backend:
```bash
cd /Users/nayyershahzad/HAZOP-Software/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend:
```bash
cd /Users/nayyershahzad/HAZOP-Software/frontend
npm run dev
```

---

## ⚠️ Important Notes

### Gemini API Key
If AI suggestions return empty results:
1. Check if your API key is valid
2. Update model name in `backend/app/services/gemini_service.py` line 17:
   ```python
   MODEL_NAME = "gemini-pro"  # Try: "models/gemini-1.5-pro"
   ```
3. Restart backend

### Database Backup
If you have a previous database backup:
```bash
psql -h localhost -U hazop_user -d hazop_db < your_backup.sql
```

---

## 📚 Documentation

- **Full Documentation**: [RESTORATION_COMPLETE.md](RESTORATION_COMPLETE.md)
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🎯 Your Next Steps

1. ✅ **Servers are running**
2. **Go to**: http://localhost:5173
3. **Login/Register**
4. **Create your first study**
5. **Test Gemini AI features**

Everything is ready! Start building your HAZOP analysis with AI assistance.
