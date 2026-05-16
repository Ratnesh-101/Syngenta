# backend/main.py
from fastapi import FastAPI
from db.session import engine, Base, SessionLocal
from api.routes import visits, farmers, signals, outcomes, weights, auth

# Import all models so SQLAlchemy knows about them before creating tables
from models.db import farmers       as farmers_model
from models.db import signal        as signal_model
from models.db import outcome       as outcome_model
from models.db import visit         as visit_model
from models.db import rep           as rep_model
from models.db import auth_identity as auth_identity_model

from models.db.rep import Rep
from models.db.auth_identity import AuthIdentity
from services.auth_service import AuthService

app = FastAPI(title="Field Force Copilot", version="0.4.0")


@app.on_event("startup")
def startup():
    # Migration: wipe ONLY the auth tables. Signals / outcomes / farmers / visits stay.
    AuthIdentity.__table__.drop(bind=engine, checkfirst=True)
    Rep.__table__.drop(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready (auth tables migrated)")

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
        )
        print("✓ Demo rep ensured (rep@syngenta.com / 9999999999 / syngenta123)")

        # Demo manager (no phone identity — managers login via password or Google)
        svc.ensure_seed_rep(
            db,
            rep_id=None,
            name="Demo Manager",
            email="manager@syngenta.com",
            phone=None,
            password="manager123",
            role="manager",
        )
        print("✓ Demo manager ensured (manager@syngenta.com / manager123)")
    finally:
        db.close()


# Routers
app.include_router(auth.router,     prefix="/auth",     tags=["Auth"])
app.include_router(visits.router,   prefix="/visits",   tags=["Visits"])
app.include_router(farmers.router,  prefix="/farmers",  tags=["Farmers"])
app.include_router(signals.router,  prefix="/signals",  tags=["Signals"])
app.include_router(outcomes.router, prefix="/outcomes", tags=["Outcomes"])
app.include_router(weights.router,  prefix="/weights",  tags=["Weights"])


@app.get("/")
def root():
    return {"status": "ok", "project": "Field Force Copilot", "version": "0.4.0"}