# backend/models/db/rep.py
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base


class Rep(Base):
    """A user of the system. Auth identities (password, phone, google) are
    attached via the AuthIdentity table.

    For managers, `managed_rep_ids` is the list of Syngenta rep IDs (e.g.
    ["REP_0338", "REP_0339"]) whose territory data they can see. Admins see
    everyone regardless.
    """
    __tablename__ = "reps"

    id              = Column(String, primary_key=True)
    rep_id          = Column(String, unique=True, index=True, nullable=True)
    name            = Column(String, nullable=False)
    primary_email   = Column(String, unique=True, index=True, nullable=True)
    role            = Column(String, default="rep")
    managed_rep_ids = Column(JSON, default=list)  # list[str], only meaningful for role=manager
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    identities = relationship(
        "AuthIdentity",
        back_populates="rep",
        cascade="all, delete-orphan",
    )