# Vercel Deployment Guide — LegalMet Verify

This guide walks you through deploying **LegalMet Verify** on [Vercel](https://vercel.com).

---

## 1. Architecture Overview

- **Frontend**: Vite + React + TypeScript + Tailwind CSS (Hosted on Vercel CDN with global edge caching and SPA routing).
- **Backend**: FastAPI + SQLAlchemy + SQLite / PostgreSQL (Hosted on Render, Railway, Fly.io, or VPS).

---

## 2. Deploying the Frontend to Vercel (Quick Setup)

### Method A: Connect via GitHub (Recommended)

1. Push your repository to GitHub.
2. Go to your [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New..."** → **"Project"**.
3. Select your repository (`LegalMet_SIH`).
4. Configure Project Settings:
   - **Framework Preset**: `Vite` (automatically detected)
   - **Root Directory**: Select `frontend` (or leave default `./` — both are configured!)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. In **Environment Variables**, add:
   - `VITE_API_BASE_URL`: URL of your deployed backend (e.g., `https://legalmet-backend.onrender.com/api`)
   *(If not set, it defaults to `/api` for local or proxy use)*
6. Click **Deploy**.

---

## 3. Configuration Files Included

We have pre-configured everything needed for Vercel:

| File | Purpose |
|------|---------|
| [`vercel.json`](./vercel.json) | Root Vercel config with build command and SPA rewrite rules (`/(.*)` → `/index.html`) so refreshing routes like `/admin/dashboard` never 404s. |
| [`frontend/vercel.json`](./frontend/vercel.json) | Vercel SPA rewrite config if you set Root Directory to `frontend` in Vercel settings. |
| [`frontend/.env.example`](./frontend/.env.example) | Example environment file for `VITE_API_BASE_URL`. |
| [`frontend/src/api/client.ts`](./frontend/src/api/client.ts) | Dynamic API client supporting `import.meta.env.VITE_API_BASE_URL` with fallback to `/api`. |

---

## 4. Backend Deployment (Render / Railway / VPS)

Because the backend relies on Python FastAPI, SQLite/PostgreSQL, PDF generation (ReportLab), and OCR tools, deploy the backend to a Python web service such as **Render** (Free tier available):

### Deploying Backend to Render (5 minutes):

1. Go to [Render Dashboard](https://dashboard.render.com/) and click **"New +"** → **"Web Service"**.
2. Connect your GitHub repository.
3. Configure the service:
   - **Name**: `legalmet-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. In **Environment Variables**, add:
   - `SECRET_KEY`: `your-production-secret-key-2026`
   - `FRONTEND_URL`: `https://your-app.vercel.app`
5. Copy your Render service URL (e.g. `https://legalmet-backend.onrender.com`).
6. In your Vercel project, set `VITE_API_BASE_URL` to `https://legalmet-backend.onrender.com/api`.
7. Redeploy Vercel frontend.

---

## 5. Verification Checklist

- [ ] Visit `https://<your-project>.vercel.app/` — homepage loads smoothly.
- [ ] Test public verification at `https://<your-project>.vercel.app/verify/IND-2024-WM-88210`.
- [ ] Direct navigation to `/admin/dashboard` or `/public/verify` loads without 404 (handled by `vercel.json` SPA rewrite).
- [ ] Login with test credentials:
  - Admin: `admin@legalmet.gov.in` / `Admin@123`
  - LMO: `lmo.sharma@legalmet.gov.in` / `Lmo@123`
  - Trader: `trader.patel@agrotraders.in` / `Trader@123`
