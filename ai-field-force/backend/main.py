from fastapi import FastAPI
from db.session import engine, Base
from api.routes import visits, farmers, signals, outcomes, weights

# Import all models so SQLAlchemy knows about them before creating tables
from models.db import farmers as farmers_model
from models.db import signal as signal_model
from models.db import outcome as outcome_model
from models.db import visit as visit_model

app = FastAPI(title="Field Force Copilot", version="0.1.0")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

# Routers
app.include_router(visits.router,   prefix="/visits",   tags=["Visits"])
app.include_router(farmers.router,  prefix="/farmers",  tags=["Farmers"])
app.include_router(signals.router,  prefix="/signals",  tags=["Signals"])
app.include_router(outcomes.router, prefix="/outcomes", tags=["Outcomes"])
app.include_router(weights.router,  prefix="/weights",  tags=["Weights"])

@app.get("/")
def root():
    return {"status": "ok", "project": "Field Force Copilot"}