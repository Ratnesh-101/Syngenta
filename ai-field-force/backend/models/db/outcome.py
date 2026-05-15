from sqlalchemy import Column, String, Float, DateTime, JSON
from db.session import Base
import uuid

class Outcome(Base):
    __tablename__ = "outcomes"

    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id        = Column(String)
    rep_id           = Column(String)
    visited_at       = Column(DateTime)
    outcome_rating   = Column(Float)
    outcome_type     = Column(String)
    actions_taken    = Column(JSON)
    notes            = Column(String, nullable=True)
    signals_at_visit = Column(JSON)
    synced           = Column(String, default="true")