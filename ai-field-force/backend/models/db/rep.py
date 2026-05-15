# backend/models/db/rep.py
from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from db.session import Base


class Rep(Base):
    __tablename__ = "reps"

    id              = Column(String, primary_key=True)        # uuid
    rep_id          = Column(String, unique=True, index=True)  # e.g. REP_0338
    name            = Column(String, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    phone           = Column(String, unique=True, index=True, nullable=False)  # digits-only, normalized
    hashed_password = Column(String, nullable=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)