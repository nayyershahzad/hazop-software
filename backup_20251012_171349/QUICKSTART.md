# 🚀 HAZOP System - Quick Start Guide

## 1️⃣ Start the System (30 seconds)

### Using the start script:
```bash
./start.sh
```

### Or manually with Docker:
```bash
docker-compose up
```

### Or manually without Docker:
**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Make sure PostgreSQL is running!**

---

## 2️⃣ Access the Application

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 3️⃣ First Steps

1. **Register** a new account at http://localhost:5173/login
2. **Click "Don't have an account? Sign Up"**
3. **Fill in your details** and submit
4. **You'll be automatically logged in**

---

## 4️⃣ Create Your First HAZOP Study

1. **Click "+ New Study"**
2. **Fill in**:
   - Study Title: "Reactor Temperature Control"
   - Facility Name: "Plant A - Reactor Section"
   - Description: "HAZOP study for reactor temperature control system"
3. **Click "Create Study"**

---

## 5️⃣ Add Nodes to Your Study

1. **Click on your study card**
2. **Click "+ Add Node"**
3. **Fill in**:
   - Node Number: "N-001"
   - Node Name: "Reactor Feed System"
   - Description: "Feed line from storage to reactor"
   - Design Intent: "Deliver raw material at 50 L/min, 25°C"
4. **Click "Create Node"**

---

## 6️⃣ Add Deviations

1. **Click on a node** (left sidebar)
2. **Click "+ Add Deviation"**
3. **Select**:
   - Parameter: "Flow"
   - Guide Word: "No"
   - Deviation Description: "No flow to reactor due to pump failure"
4. **Click "Create Deviation"**

**Try more deviations:**
- Flow / More / "Excessive flow exceeding design capacity"
- Temperature / High / "Feed temperature exceeds design limit"
- Pressure / More / "High pressure in feed line"

---

## 7️⃣ Common Docker Commands

```bash
# Start everything
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop everything
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Rebuild containers
docker-compose up --build
```

---

## 8️⃣ Troubleshooting

### ❌ "Port 8000 already in use"
```bash
# Find what's using port 8000
lsof -i :8000
# Kill it or stop docker-compose
docker-compose down
```

### ❌ "Can't connect to database"
```bash
# Reset database
docker-compose down -v
docker-compose up
```

### ❌ "Frontend not loading"
```bash
# Check if services are running
docker-compose ps

# Restart frontend
docker-compose restart frontend
```

### ❌ "Login not working"
- Check browser console (F12)
- Verify backend is running: http://localhost:8000/health
- Check JWT_SECRET is set in .env

---

## 9️⃣ Test the API Directly

Visit http://localhost:8000/docs to see interactive API documentation.

**Try it out:**
1. **Register a user** via POST /api/auth/register
2. **Copy the access_token** from response
3. **Click "Authorize"** button (top right)
4. **Paste token** as: `Bearer YOUR_TOKEN`
5. **Now try** any endpoint (GET /api/studies, etc.)

---

## 🔟 What's Next?

After testing the MVP, we can add:

- ✨ **P&ID PDF upload and viewing**
- 🤖 **AI suggestions** (Causes, Consequences, Safeguards)
- 📋 **Superior copy/paste** functionality
- ⚡ **Intelligent auto-complete**
- 👥 **Real-time collaboration**
- 📊 **Export to Word/Excel**

See `hazop_claude_prompt.md` for complete feature list and implementation guide.

---

## 📞 Need Help?

- Check [README.md](./README.md) for detailed documentation
- Check [MVP_SUMMARY.md](./MVP_SUMMARY.md) for what's included
- Check `docker-compose logs` for errors
- Open browser DevTools (F12) to see frontend errors

---

**Happy HAZOPing! 🎉**
