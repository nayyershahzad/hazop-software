# Manual Backend Deployment Guide

This guide provides detailed instructions for deploying the HAZOP Software backend API to Render.com manually, bypassing the issues encountered with the Blueprint deployment.

## Prerequisites

- A [Render.com](https://render.com) account
- Access to the HAZOP-Software GitHub repository
- PostgreSQL knowledge for database setup
- Python 3.11+ installed locally (for testing before deployment)

## Preparation Steps

1. **Test the optimized backend locally**

   ```bash
   cd /Users/nayyershahzad/HAZOP-Software/backend
   source venv/bin/activate  # or create a new venv if needed
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

   Verify that the API works correctly by accessing http://localhost:8000/docs

2. **Commit and push your changes**

   ```bash
   git add .
   git commit -m "Optimize backend with robust database handling and CORS configuration"
   git push origin main
   ```

## Deployment Steps

### 1. Create a PostgreSQL Database on Render.com

1. Log in to your Render.com dashboard
2. Click "New +" and select "PostgreSQL"
3. Configure the database:
   - **Name**: `hazop-db`
   - **Database**: `hazop_db`
   - **User**: `hazop_user`
   - **Region**: Choose a region close to your users (e.g., `ohio` for North America)
   - **PostgreSQL Version**: `14`
   - **Plan**: Choose according to your needs (e.g., `Free` for testing)
4. Click "Create Database"
5. Once created, note the "Internal Database URL" - you'll need this for the backend service

### 2. Create a Web Service for the Backend API

1. From the Render dashboard, click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `hazop-api`
   - **Environment**: `Python 3`
   - **Region**: Choose the same region as your database
   - **Branch**: `main`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --timeout 60 --keep-alive 120 --access-logfile - --error-logfile - --log-level info --bind 0.0.0.0:$PORT`

### 3. Configure Environment Variables

Add the following environment variables to your backend service:

**Required Variables:**
- **PYTHON_VERSION**: `3.11.9`
- **DATABASE_URL**: Copy the Internal Database URL from your PostgreSQL service
- **JWT_SECRET**: Generate a secure random string (e.g., use `openssl rand -hex 32` in terminal)
- **JWT_ALGORITHM**: `HS256`
- **ACCESS_TOKEN_EXPIRE_MINUTES**: `1440` (24 hours)
- **ENVIRONMENT**: `production`
- **CORS_ORIGINS**: URL of your frontend service (e.g., `https://hazop-web.onrender.com`)

**Optional Variables:**
- **GEMINI_API_KEY**: Your Google Gemini API key for AI features
- **POOL_SIZE**: `10` (Database connection pool size)
- **MAX_OVERFLOW**: `20` (Max overflow connections)
- **POOL_TIMEOUT**: `30` (Pool timeout in seconds)
- **POOL_RECYCLE**: `1800` (Connection recycle time in seconds)

### 4. Configure Disk Storage

For file uploads and persistent storage:

1. In your backend service settings, go to "Disks"
2. Add a new disk:
   - **Name**: `hazop-api-disk`
   - **Mount Path**: `/opt/render/project/src/backend/uploads`
   - **Size**: `1` GB (adjust as needed)

### 5. Set Up Health Checks

1. In your backend service settings, go to "Health"
2. Set the health check path to: `/health`
3. Configure appropriate intervals and timeouts

### 6. Deploy Manually

1. In your backend service dashboard, click "Manual Deploy" > "Deploy latest commit"
2. Watch the logs for any errors during deployment

### 7. Initialize Database (First Deployment Only)

After the first successful deployment, you'll need to run the database migrations:

1. Go to your backend service in the Render dashboard
2. Click "Shell"
3. Run the following commands:

   ```bash
   cd backend
   python -c "from app.database import init_db; init_db()"
   ```

## Troubleshooting Common Issues

### Database Connection Issues

1. **Connection failures:**
   - Verify the DATABASE_URL is correctly set
   - Check the database service is running
   - Try connecting with psql from the shell to debug

2. **Migration errors:**
   - Check the logs for specific error messages
   - Run migrations manually from the shell

### Server Startup Problems

1. **Module import errors:**
   - Check that all dependencies are installed
   - Verify the correct Python version is being used

2. **Port binding issues:**
   - Let Render handle port binding via the $PORT environment variable
   - Don't hardcode port numbers in the start command

### CORS Errors

1. **Frontend cannot connect to API:**
   - Verify CORS_ORIGINS includes your frontend URL
   - Check browser console for specific CORS error messages
   - Ensure protocols match (http vs https)

## Monitoring and Maintenance

### Performance Monitoring

1. Use the "Metrics" tab in your Render dashboard to monitor:
   - CPU and memory usage
   - Request rates and response times
   - Error rates

2. Set up alerts for resource limits or performance degradation

### Log Management

1. Access logs from the "Logs" tab in your service dashboard
2. Filter logs by:
   - Error severity
   - Time period
   - Custom search terms

### Database Management

1. Monitor database metrics from the PostgreSQL service dashboard
2. Set up regular backups (automatically configured by Render)
3. Consider scaling your database as your user base grows

## Scaling Strategy

### Horizontal Scaling

1. Increase worker count in the start command for more concurrent requests
2. Use the "Autoscaling" feature in Render for traffic-based scaling

### Vertical Scaling

1. Upgrade your service plan for more CPU/memory resources
2. Increase database plan for higher connection limits and performance

## Rollback Plan

If deployment introduces critical issues:

1. From the service dashboard, go to "Deploys"
2. Find the last successful deploy
3. Click "..." > "Rollback to this deploy"

---

## Next Steps

After deploying the backend service:

1. Test the connection between frontend and backend
2. Verify all API endpoints work as expected
3. Implement monitoring and alerts for production use

See the [Frontend Deployment Guide](./MANUAL_FRONTEND_DEPLOYMENT.md) for deploying the user interface.