from sqlalchemy import Column, String, DateTime, JSON
from db.session import Base
import uuid

class Signal(Base):
    __tablename__ = "signals"

    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id   = Column(String)
    signal_type = Column(String)
    severity    = Column(String, nullable=True)
    payload     = Column(JSON)
    expires_at  = Column(DateTime, nullable=True)
    created_at  = Column(DateTime)