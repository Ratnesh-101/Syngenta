# DEPLOYMENT.md

How the live deployment of Kheti Compass is configured.

---

## Production URLs

| Service | URL | Provider | Plan |
|---|---|---|---|
| Backend | https://kheti-compass.onrender.com | Render | Free web service |
| Frontend | https://syngenta-nu.vercel.app | Vercel | Free (Hobby) |
| Keep-alive | (background) | UptimeRobot | Free |

**Total monthly infrastructure cost: ₹0.**

---

## Backend — Render

### Service configuration

| Setting | Value |
|---|---|
| Service type | Web Service |
| Region | Oregon (US West) |
| Runtime | Python 3.11.10 (pinned via `runtime.txt`) |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn main:app --host 0.0.0.0 --port $PORT` (via `Procfile`) |
| Root directory | `ai-field-force/backend` |
| Health check path | `/docs` |
| Plan | Free (512 MB RAM, 0.1 CPU) |
| Auto-deploy | On every push to `main` |

### Environment variables (configured in Render UI)

| Variable | Notes |
|---|---|
| `OPENAI_API_KEY` | For gpt-4o-mini briefing endpoints |
| `JWT_SECRET` | 48-char random string |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_EXPIRE_MINUTES` | `10080` (7 days) |
| `DEV_MODE` | `false` |
| `OTP_PROVIDER` | `console` (OTP delivery is stubbed for Stage 1) |
| `GOOGLE_CLIENT_ID` | OAuth 2.0 client ID for Google sign-in |

### Free-tier behavior

- The service sleeps after **15 minutes** of inactivity
- First request after sleep takes **~30 seconds** to wake (Python interpreter restart + module imports + database re-seed)
- UptimeRobot pings `/docs` every 5 minutes during evaluation to keep the service warm
- SQLite database is bundled with the backend. **The seed script runs on startup**, so demo data is rebuilt on every cold start — fine for evaluation, would migrate to managed PostgreSQL for production (see Section 6.3 of the solution document)

### CORS

The backend uses a regex-based CORS rule that allows:

- Any `localhost` or `127.0.0.1` origin (for local dev)
- Any `*.vercel.app` origin (for the live frontend and Vercel preview deployments)

Configured in `backend/main.py`.

---

## Frontend — Vercel

### Project configuration

| Setting | Value |
|---|---|
| Framework Preset | Vite |
| Root Directory | `ai-field-force/frontend` |
| Build Command | `npm run build` (default for Vite preset) |
| Output Directory | `dist` (default for Vite preset) |
| Install Command | `npm install` (default) |
| Node.js Version | **20.x** (Vite 5 has known issues with Node 24 — leave this set to 20) |
| Auto-deploy | On every push to `main` |

### Environment variables (configured in Vercel UI)

| Variable | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://kheti-compass.onrender.com` |
| `VITE_MOCK_MODE` | `false` |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID (same as backend's) |

### Why Vercel and not Render Static

- Vercel's free tier scales to production volumes for static React apps (CDN-edge served)
- Build times are ~60 seconds end-to-end vs Render's ~120 seconds for the same artifact
- Vercel handles preview deployments automatically (every PR gets its own URL) — useful if we re-open development post-hackathon

---

## Keep-alive — UptimeRobot

| Setting | Value |
|---|---|
| Monitor type | HTTP(s) |
| URL | `https://kheti-compass.onrender.com/docs` |
| Interval | 5 minutes |
| Alert contact | `24f2008613@ds.study.iitm.ac.in` |
| Plan | Free (50 monitors max) |

Pings `/docs` instead of `/` because `/docs` always returns 200 OK if FastAPI is up — `/` may return 404 depending on whether a root route is defined.

---

## Local development

For instructions on running Kheti Compass locally (without using the production deployment), see the main `README.md`.

---

## Production migration path

For a real Syngenta pilot deployment (100 reps at one business unit), the path is documented in Section 6.3 of the solution document:

1. Migrate from SQLite to PostgreSQL (Render managed Postgres, $15/month) — the SQLAlchemy ORM is portable, no schema changes needed
2. Upgrade backend to Render's paid Starter tier ($7/month) or Standard ($25/month) to eliminate cold starts and provide always-on availability
3. Frontend stays on Vercel free tier (it scales to production volumes for static React apps)
4. Total Phase 1 monthly cost: **~$43**

The architecture has clean seams for each transition — none require rewriting the scoring engine or data model.

---

## Troubleshooting

### Backend returns 502 Bad Gateway

Render free tier is mid-restart. Wait 30–60 seconds and retry. UptimeRobot keeps this rare during evaluation.

### Frontend deploys but login fails with CORS error

Verify that the frontend's `VITE_API_BASE_URL` env var points to `https://kheti-compass.onrender.com` (no trailing slash). The backend's CORS regex allows `*.vercel.app` — if you deploy to a different domain, update the regex in `backend/main.py`.

### Vercel build fails with "vite: command not found"

Check Node.js Version in Vercel project settings → set to `20.x` (not 24.x). Vite 5 has known issues with Node 24 where `npm install` completes but the `vite` binary doesn't link correctly into `node_modules/.bin/`.

### Render build fails with numpy compilation error

Verify `runtime.txt` contains `python-3.11.10` (not `python-3.13.x`). NumPy 1.x has pre-built wheels for Python 3.11 on Linux; on Python 3.13 it tries to compile from source.

---

## Contact

For deployment questions: Ratnesh Singh — `24f2008613@ds.study.iitm.ac.in`