# Manual Frontend Deployment Guide

This guide provides step-by-step instructions for deploying the HAZOP Software frontend to Render.com manually, avoiding the issues encountered with the automatic Blueprint deployment.

## Prerequisites

- A [Render.com](https://render.com) account
- Access to the HAZOP-Software GitHub repository
- Node.js 18+ and npm installed on your local machine (for testing before deployment)

## Preparation Steps

1. **Test the optimized frontend locally**

   ```bash
   cd /Users/nayyershahzad/HAZOP-Software/frontend
   npm install
   npm run build
   npm run preview
   ```

   Verify that the application works correctly, especially the dashboard with the simplified chart components.

2. **Commit and push your changes**

   ```bash
   git add .
   git commit -m "Optimize frontend with simplified charts, remove recharts dependency"
   git push origin main
   ```

## Deployment Steps

### 1. Create a New Static Site on Render.com

1. Log in to your Render.com dashboard
2. Click "New +" and select "Static Site"
3. Connect your GitHub repository
4. Configure the following settings:
   - **Name**: `hazop-web`
   - **Build Command**: `cd frontend && npm install --no-audit --legacy-peer-deps && VITE_SKIP_POSTCSS=true npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Branch**: `main`

### 2. Configure Environment Variables

Add the following environment variables:

- **NODE_VERSION**: `20.19.0` (This is critical for React 19+ compatibility)
- **VITE_API_URL**: The URL of your backend API (e.g., `https://hazop-api.onrender.com`)
- **VITE_SKIP_POSTCSS**: `true` (To avoid PostCSS issues during build)

### 3. Advanced Build Settings (Optional)

For larger projects, you might want to configure:

- **Auto-Deploy**: Set to `No` if you want to manually control deployments
- **Build Filter**: Set to `frontend/**` to only trigger builds when frontend files change

### 4. Deploy Manually

1. In your Render dashboard, go to the `hazop-web` service
2. Click "Manual Deploy" > "Deploy latest commit"
3. Watch the build logs for any errors

## Troubleshooting Common Issues

### Build Failures

1. **"Module not found" errors**:
   - Check that all dependencies are properly listed in package.json
   - Ensure no references to removed packages (like recharts) remain in the code

2. **PostCSS/Tailwind Issues**:
   - We've simplified the PostCSS configuration to avoid build issues
   - If problems persist, try removing tailwindcss from the build process temporarily

3. **React Compatibility Issues**:
   - Ensure Node.js version is set to 20.19.0 or later
   - Check for deprecated React APIs in the codebase

### Runtime Errors

1. **API Connection Issues**:
   - Verify the `VITE_API_URL` environment variable is set correctly
   - Check that CORS is properly configured on the backend

2. **Chart Rendering Issues**:
   - Inspect browser console for errors
   - Verify the chart data format in the API responses

## Post-Deployment Verification

After deploying, perform these checks:

1. Navigate to the dashboard page and verify charts render correctly
2. Test user authentication flow
3. Verify HAZOP study creation and editing
4. Check AI suggestion functionality
5. Verify file uploads and PDF viewing

## Optimizing for Production

To further optimize the frontend:

1. **Enable CDN Caching**:
   - In the Render dashboard, go to `hazop-web` > "Settings" > "Headers"
   - Add Cache-Control headers for static assets

2. **Implement HTTP/2**:
   - Render.com supports HTTP/2 by default for better performance

3. **Monitor Performance**:
   - Use the "Metrics" tab in your Render dashboard
   - Set up alerts for high response times

## Rollback Plan

If deployment fails or introduces critical issues:

1. In the Render dashboard, go to `hazop-web` > "Deploys"
2. Find the last successful deploy
3. Click "..." > "Rollback to this deploy"

---

## Next Steps

After deploying the frontend, follow the [Backend Deployment Guide](./MANUAL_BACKEND_DEPLOYMENT.md) to deploy the API service.