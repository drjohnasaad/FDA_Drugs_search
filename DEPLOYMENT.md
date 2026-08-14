# 🚀 Free Deployment Guide

This app is a standard Flask app with minimal dependencies and **no databases or environment secrets required** — which makes it trivial to deploy for free.

## Option 1: Render (Recommended) — 100% Free

[Render](https://render.com) offers a free web service tier with:
- **Free forever** — 512 MB RAM, 0.1 CPU
- Auto-deploy from GitHub
- Free SSL certificate (HTTPS)
- Custom domain support (free on paid, subdomain `.onrender.com` is free)

### Steps

1. **Push this project to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/fda-medication-search.git
   git push -u origin main
   ```

2. **Go to Render dashboard:** https://dashboard.render.com

3. Click **"New +"** → **"Blueprint"** (easiest — uses the included `render.yaml`)

4. Connect your GitHub account and select the repo. Render will automatically detect `render.yaml` and create the service.

5. Click **"Apply"** — Render will build and deploy the app in ~2 minutes.

6. **Done!** Your app will be live at `https://fda-medication-search.onrender.com`

> **Alternative (manual setup):** Click **New +** → **Web Service** → select the repo → name it `fda-medication-search` → **Environment: Python 3** → Build Command: `pip install -r requirements.txt` → Start Command: `gunicorn app:app` → **Free** plan → Deploy.

---

## Option 2: Railway — 100% Free Starter Credits

[Railway](https://railway.app) gives free monthly credits, enough for small apps.

1. Push the project to GitHub (same steps as above).
2. Go to https://railway.app and click **"Start a New Project"**.
3. Choose **"Deploy from GitHub repo"** — select your repo.
4. Railway auto-detects the `Procfile` and `runtime.txt`, installs dependencies, and starts `gunicorn app:app`.
5. Click **"Generate Domain"** and get a free `*.up.railway.app` URL.

> **Tip:** The Procfile tells Railway exactly how to run the app, no extra config needed.

---

## Option 3: PythonAnywhere — Free forever

[PythonAnywhere](https://www.pythonanywhere.com) free tier works but requires a small manual WSGI setup. Note the free tier's outbound HTTP is behind a whitelist proxy, so FDA API calls may be blocked.

---

## Database / Secrets

**None needed.** This app calls public APIs (FDA, RxImage, Google favicons) and does not store data, so no database or environment variables are required.

## Watching Logs / Debugging

- **Render:** Dashboard → your service → **Logs**
- **Railway:** Dashboard → your service → **Deployments** → **Deploy Logs**
- The app prints `DEBUG:` messages for each search — check logs if something breaks.

## Updating

Push to GitHub on any of these platforms and auto-deploy will retrain and reload the app automatically.

## Local Development

```bash
pip install -r requirements.txt
python app.py
# goes to http://localhost:5000 — debug on
```

To run in production mode locally (no debug):
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## Files added for deployment

| File | Purpose |
|------|---------|
| `requirements.txt` | Flask + gunicorn pinned versions |
| `Procfile` | Tells Heroku (Render/Railway) how to run the app |
| `render.yaml` | One-click blueprint for Render auto-deploy |
| `runtime.txt` | Pins Python version (3.12.1) for Heroku/Railway |
| `.gitignore` | Prevents committing Python/IDE junk |
| `app.py` | Now reads `PORT` & `DEBUG` env vars, binds `0.0.0.0` |
</｜DSML｜tool>