# backend/main.py
from fastapi import FastAPI
from db.session import engine, Base, SessionLocal
from api.routes import visits, farmers, signals, outcomes, weights, auth, devices, manager

# Import all models so SQLAlchemy knows about them before creating tables
from models.db import farmers       as farmers_model
from models.db import signal        as signal_model
from models.db import outcome       as outcome_model
from models.db import visit         as visit_model
from models.db import rep           as rep_model
from models.db import auth_identity as auth_identity_model
from models.db import device        as device_model

from models.db.rep import Rep
from models.db.auth_identity import AuthIdentity
from models.db.outcome import Outcome
from models.db.device import Device
from services.auth_service import AuthService

app = FastAPI(title="Field Force Copilot", version="0.6.0")


@app.on_event("startup")
def startup():
    # Migration: wipe auth tables and the recently-changed outcomes/devices/rep tables.
    # Rep table needs to drop to pick up the new `managed_rep_ids` column.
    Outcome.__table__.drop(bind=engine, checkfirst=True)
    Device.__table__.drop(bind=engine, checkfirst=True)
    AuthIdentity.__table__.drop(bind=engine, checkfirst=True)
    Rep.__table__.drop(bind=engine, checkfirst=True)

    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready (auth + outcomes + devices + rep migrated)")

    db = SessionLocal()
    try:
        svc = AuthService()

        # Demo field rep
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

        # Demo manager who manages REP_0338
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
    return {"status": "ok", "project": "Field Force Copilot", "version": "0.6.0"}