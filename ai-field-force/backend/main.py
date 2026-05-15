from fastapi import FastAPI
from api.routes import visits, farmers, signals, outcomes

app = FastAPI(title="Field Force Copilot", version="0.1.0")

app.include_router(visits.router,   prefix="/visits",   tags=["Visits"])
app.include_router(farmers.router,  prefix="/farmers",  tags=["Farmers"])
app.include_router(signals.router,  prefix="/signals",  tags=["Signals"])
app.include_router(outcomes.router, prefix="/outcomes", tags=["Outcomes"])