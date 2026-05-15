# backend/models/db/rep.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base


class Rep(Base):
    """A user of the system. Auth identities (password, phone, google) are
    attached via the AuthIdentity table — a single Rep can have multiple ways
    to log in, all resolving to this same account.
    """
    __tablename__ = "reps"

    id              = Column(String, primary_key=True)             # uuid
    rep_id          = Column(String, unique=True, index=True, nullable=True)  # e.g. REP_0338 (nullable for self-signups not yet linked to a Syngenta territory)
    name            = Column(String, nullable=False)
    primary_email   = Column(String, unique=True, index=True, nullable=True)  # canonical email for the account; nullable for phone-first signups
    role            = Column(String, default="rep")                # rep | manager | admin
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    identities = relationship(
        "AuthIdentity",
        back_populates="rep",
        cascade="all, delete-orphan",
    )