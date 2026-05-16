# backend/models/db/device.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base


class Device(Base):
    """A device (phone, tablet) used by a Rep. Tracks sync activity and lets us
    show 'devices linked to your account' / 'revoke this device' in the UI.
    """
    __tablename__ = "devices"

    id            = Column(String, primary_key=True)        # client-supplied device_id (uuid)
    rep_id        = Column(String, ForeignKey("reps.id", ondelete="CASCADE"), index=True, nullable=False)
    name          = Column(String, nullable=True)            # human label, e.g. "Ravi's phone"
    platform      = Column(String, nullable=True)            # "android" | "ios" | "web"
    is_revoked    = Column(Boolean, default=False)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at  = Column(DateTime, default=datetime.utcnow)
    last_sync_at  = Column(DateTime, nullable=True)
    sync_count    = Column(String, default="0")              # cumulative outcomes synced via this device

    rep = relationship("Rep")