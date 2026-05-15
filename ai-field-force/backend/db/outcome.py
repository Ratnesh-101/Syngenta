# models/db/signal.py

from sqlalchemy import Column, String, Float, DateTime, JSON

class Signal(Base):
    __tablename__ = "signals"

    id          = Column(String, primary_key=True)
    entity_id   = Column(String)
    signal_type = Column(String)
    severity    = Column(String, nullable=True)
    payload     = Column(JSON)
    expires_at  = Column(DateTime, nullable=True)
    created_at  = Column(DateTime)