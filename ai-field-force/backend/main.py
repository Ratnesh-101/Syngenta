# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.session import engine, Base, SessionLocal
from api.routes import visits, farmers, signals, outcomes, weights, auth, devices, manager

# Import all models so SQLAlchemy knows about them before creating tables
from models.db import farmers        as farmers_model
from models.db import signal         as signal_model
from models.db import outcome        as outcome_model
from models.db import visit          as visit_model
from models.db import rep            as rep_model
from models.db import auth_identity  as auth_identity_model
from models.db import device         as device_model
from models.db import weight_history as weight_history_model

from models.db.rep import Rep
from models.db.auth_identity import AuthIdentity
from models.db.outcome import Outcome
from models.db.device import Device
from models.db.weight_history import WeightHistory
from services.auth_service import AuthService
from db.seed_demo_outcomes import seed_demo_outcomes

app = FastAPI(title="Field Force Copilot", version="0.7.0")

# ---------- CORS ----------
# Lets browser-based frontends at common local ports talk to this API.
# Production would restrict origins to the actual deployed frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Create React App default
        "http://localhost:5173",   # Vite default
        "http://localhost:5174",   # Vite secondary
        "http://localhost:4173",   # Vite preview
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "null",                    # file:// origin — for the local HTML demo client
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
def startup():
    WeightHistory.__table__.drop(bind=engine, checkfirst=True)
    Outcome.__table__.drop(bind=engine, checkfirst=True)
    Device.__table__.drop(bind=engine, checkfirst=True)
    AuthIdentity.__table__.drop(bind=engine, checkfirst=True)
    Rep.__table__.drop(bind=engine, checkfirst=True)

    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready (auth + outcomes + devices + weight_history migrated)")

    db = SessionLocal()
    try:
        svc = AuthService()

        svc.ensure_seed_rep(
            db,
            rep_id="REP_0338",
            name="Demo Rep",
            email="rep@syngenta.com",
            phone="9999999999",
            password="syngenta123",
            role="rep",
            managed_rep_ids=[],
        )
        print("✓ Demo rep ensured (rep@syngenta.com / 9999999999 / syngenta123)")

        svc.ensure_seed_rep(
            db,
            rep_id=None,
            name="Demo Manager",
            email="manager@syngenta.com",
            phone=None,
            password="manager123",
            role="manager",
            managed_rep_ids=["REP_0338"],
        )
        print("✓ Demo manager ensured (manager@syngenta.com / manager123, manages [REP_0338])")

        seed_result = seed_demo_outcomes(db)
        print(f"✓ Demo outcomes seeded: created={seed_result['created']}, skipped={seed_result['skipped']}")
    finally:
        db.close()


# Routers
app.include_router(auth.router,     prefix="/auth",     tags=["Auth"])
app.include_router(visits.router,   prefix="/visits",   tags=["Visits"])
app.include_router(farmers.router,  prefix="/farmers",  tags=["Farmers"])
app.include_router(signals.router,  prefix="/signals",  tags=["Signals"])
app.include_router(outcomes.router, prefix="/outcomes", tags=["Outcomes"])
app.include_router(weights.router,  prefix="/weights",  tags=["Weights"])
app.include_router(devices.router,  prefix="/devices",  tags=["Devices"])
app.include_router(manager.router,  prefix="/manager",  tags=["Manager"])


@app.get("/")
def root():
    return {"status": "ok", "project": "Field Force Copilot", "version": "0.7.0"}