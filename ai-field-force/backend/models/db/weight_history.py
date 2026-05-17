# backend/models/db/weight_history.py
from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime
from db.session import Base


class WeightHistory(Base):
    """Snapshot of signal weights at a point in time. Created every time the
    Bayesian updater runs (after an outcome) and every time the recalibration
    job runs. Lets us show 'these weights changed because of this outcome.'
    """
    __tablename__ = "weight_history"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    rep_id      = Column(String, nullable=True, index=True)   # which rep's outcomes triggered this (NULL for global recalibration)
    trigger     = Column(String, nullable=False)              # "outcome_logged" | "manual_recalibration"
    outcome_id  = Column(Integer, nullable=True)              # FK-ish to outcomes; nullable for recalibration
    weights     = Column(JSON, nullable=False)                # the SIGNAL_WEIGHTS dict at this point
    delta       = Column(JSON, nullable=True)                 # per-key change from previous snapshot
    created_at  = Column(DateTime, default=datetime.utcnow, index=True)