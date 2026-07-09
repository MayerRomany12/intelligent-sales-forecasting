# Deployment Guide for Vercel

This guide outlines how to build and host the **React Frontend Client** on [Vercel](https://vercel.com).

---

## 🛠️ Configuration Details

We have configured the React build context to run on Vercel using `frontend/vercel.json`. It redirects all request routes to `index.html` to support frontend client-side routing, and specifies the build directories properly.

---

## 🚀 Step-by-Step Deployment

### Method 1: Deploy using Vercel GitHub Integration (Recommended)
1. Sign in to your [Vercel Dashboard](https://vercel.com).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. In the configuration settings, modify the following parameters:
   * **Framework Preset**: `Vite` (or select `Other` if it defaults)
   * **Root Directory**: `frontend`
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
5. Expand the **Environment Variables** section and add:
   * **Key**: `VITE_API_URL`
   * **Value**: `https://olist-sales-api.onrender.com` (Your deployed production FastAPI backend URL)
6. Click **Deploy**.

---

### Method 2: Deploy using Vercel CLI
If you prefer deploying via terminal commands:

1. Install the Vercel CLI globally:
   ```bash
   npm install -g vercel
   ```
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Authenticate and initialize the deployment:
   ```bash
   vercel login
   vercel
   ```
   Follow the interactive prompts to create a new project.
4. Set production environment variable:
   ```bash
   vercel env add VITE_API_URL https://olist-sales-api.onrender.com production
   ```
5. Deploy to production:
   ```bash
   vercel --prod
   ```
