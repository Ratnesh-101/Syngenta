# Field Force Copilot

**AI-guided field operations copilot for Syngenta agricultural reps.**

Helps reps decide who to visit, what to discuss, detects anomalies, learns from outcomes — and gives managers a control tower over their territory.

Built for the Syngenta Hackathon. Real dataset, real ML, real offline-resilient design.

---

## What this is

A field rep working in rural Bikaner, Rajasthan has to decide every morning: with 27+ growers in my territory and limited hours, **who do I visit today?**

This project answers that question continuously and explainably.

- **For reps:** a daily priority list ranked by an ML score, with reasons, anomaly alerts, LLM-generated visit briefings, and recommended actions. Outcomes recorded offline, synced when signal returns.
- **For managers:** a territory health dashboard, per-rep performance, cross-rep top priorities, and a visible learning trail.

---

## The interesting parts

### 1. Multi-method auth that doesn't paint you into a corner
- Email + password, WhatsApp OTP, Google sign-in — **one account, multiple identities**. Sign in with phone today, link Google tomorrow, same account either way.
- 7-day JWTs, role-based access (rep / manager / admin), 403 safety net for accounts not yet linked to a Syngenta territory.

### 2. A priority list that explains itself
Every grower in `/visits/today` ships with a `reasons[]` array and an `anomalies[]` array. No black box. If a grower jumps to rank #1, the rep can see why before they get in the car.

### 3. Offline-first outcome sync
Field reps lose signal constantly. Outcomes recorded on-device get a client UUID, queue up locally, and replay to the server when connectivity returns.

- **Idempotent** on `(device_id, client_outcome_id)` — replays don't double-count.
- **Mixed-status response** — some succeed, some fail, the client sees exactly what happened with each item.
- **Device tracking** — each rep can see linked devices and revoke any that's been lost or stolen.

### 4. Visible ML learning
The project literally tagline says "learns from outcomes" — and we can prove it. Every recorded outcome captures the grower's signal state at that moment, runs a Bayesian update against the rating, and persists a snapshot. `GET /weights/history` returns the full trail with per-signal deltas.

### 5. A manager dashboard with a real KPI
`territory_health_score` is computed as `0.4 × coverage + 0.4 × outcome_quality + 0.2 × urgency_resolution`. Each component is exposed in the API response so it's auditable, not magical. Weights are tunable via `.env`.

---

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite + LangChain + OpenAI (gpt-4o-mini) + Pydantic
- **Auth:** PyJWT-via-jose, bcrypt, google-auth
- **Runtime:** Python 3.11+, Windows-friendly (developed on PowerShell)
- **Frontend:** *[to be added by frontend team]*

---

## Running it

```powershell
cd backend

# 1. Install deps (one-time)
pip install fastapi uvicorn sqlalchemy "python-jose[cryptography]" python-multipart `
            python-dotenv email-validator bcrypt google-auth langchain langchain-openai

# 2. Seed the dataset (one-time — populates 27 growers from CSV)
python -m db.seed_data

# 3. Run
uvicorn main:app --reload
```

Server boots at `http://localhost:8000`. Swagger UI at `http://localhost:8000/docs`.

You'll see this on startup:
```
✓ Database tables ready
✓ Demo rep ensured (rep@syngenta.com / 9999999999 / syngenta123)
✓ Demo manager ensured (manager@syngenta.com / manager123, manages [REP_0338])
✓ Demo outcomes seeded: created=8, skipped=0
```

---

## Demo credentials

| Role    | Email                    | Password      | Phone        |
|---------|--------------------------|---------------|--------------|
| Rep     | rep@syngenta.com         | syngenta123   | 9999999999   |
| Manager | manager@syngenta.com     | manager123    | —            |

The rep's `rep_id` is `REP_0338` — Bikaner, Rajasthan territory, 27 growers.

---

## Project structure

```
backend/
├── main.py                   # FastAPI app, startup migration, demo seeding
├── config.py                 # Env-driven settings (JWT, OTP, health-score weights)
├── api/routes/               # HTTP layer — auth, visits, signals, outcomes,
│                             # weights, devices, manager
├── core/
│   ├── auth/                 # JWT, password, OTP, Google verify, roles
│   ├── deterministic/        # Signal normalizer, anomaly detector, NBA engine, explainer
│   ├── ml/                   # Feature builder, priority scorer, weight updater, confidence
│   └── llm/                  # Briefing + explainer chains
├── models/
│   ├── db/                   # SQLAlchemy models
│   └── schemas/              # Pydantic request/response types
├── services/                 # Business logic (routes call services; services call core)
└── db/
    ├── seed_data.py          # Loads 27 real growers from CSVs
    ├── seed_demo_outcomes.py # Pre-populates dashboards on every startup
    └── data/                 # The real Syngenta dataset
```

**Architectural rule:** routes → services → core. Core never imports from services or routes. LLM is only called for briefings/explanations, never the priority list itself.

---

## API surface

Full reference: see `API.md`. Quick sampling:

```
POST  /auth/otp/send                      # WhatsApp OTP (console mode for demo)
POST  /auth/otp/verify                    # Auto-creates account on first verify
POST  /auth/google/verify                 # Frontend-driven Google sign-in
GET   /visits/today                       # Daily ranked priority list (27 growers)
GET   /visits/{id}/brief                  # LLM-generated visit briefing
POST  /outcomes/sync                      # Bulk-sync offline outcomes, idempotent
GET   /weights/history                    # The ML learning trail
GET   /manager/overview                   # Territory health KPI + dashboard
```

---

## What's not in scope (and why)

We made deliberate cuts. Things judges might ask about:

- **Weather is randomized.** No weather CSV in the source dataset. We acknowledge it; in production this plugs into an India Meteorological Department API.
- **OTP delivery is console-mode.** The OTP sender is pluggable (`core/auth/otp/`). A Twilio WhatsApp adapter is a 1-file addition; we left it out so the demo has zero external dependencies.
- **Email verification.** Out of scope. Google accounts arrive verified by Google; passwords trust the user.
- **Refresh tokens.** 7-day JWTs are sufficient for the project window.
- **Manager hierarchies.** A manager has explicit `managed_rep_ids`. We didn't model manager-of-managers.

---

## Roadmap

If we kept building:
- Weather + market price ingestion → richer signals
- Push notifications via FCM for high-urgency anomalies
- Twilio WhatsApp adapter for production OTP
- Real-time outcome stream for managers (websockets)
- A/B testing the priority weights against actual sales conversion