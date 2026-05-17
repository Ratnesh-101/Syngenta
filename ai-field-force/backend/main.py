# backend/main.py
from fastapi import FastAPI
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
from models.db import weight_history as weight_history_model  # NEW

from models.db.rep import Rep
from models.db.auth_identity import AuthIdentity
from models.db.outcome import Outcome
from models.db.device import Device
from models.db.weight_history import WeightHistory
from services.auth_service import AuthService
from db.seed_demo_outcomes import seed_demo_outcomes

app = FastAPI(title="Field Force Copilot", version="0.7.0")


@app.on_event("startup")
def startup():
    # Migration: wipe tables whose schema we own and re-create. Signals /
    # farmers_retailers / visits are NOT dropped — they're populated from CSVs
    # by the seed_data script and we don't want to lose them.
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

        # Demo outcomes — populates the dashboards so they look like a real product.
        # Auto-runs every startup. Idempotent (uses stable client_outcome_ids).
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