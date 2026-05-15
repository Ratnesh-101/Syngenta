# backend/models/db/auth_identity.py
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base


class AuthIdentity(Base):
    """A single way to log in to a Rep account.

    One Rep can have many AuthIdentity rows:
      - provider="password",     identifier=email (lowercased), credential=bcrypt hash
      - provider="whatsapp_otp", identifier=phone (digits-only),  credential=NULL
      - provider="google",       identifier=google sub (subject ID), credential=NULL

    Uniqueness is per (provider, identifier) so no two reps can claim the same Google account etc.
    """
    __tablename__ = "auth_identities"
    __table_args__ = (
        UniqueConstraint("provider", "identifier", name="uq_provider_identifier"),
    )

    id          = Column(String, primary_key=True)                                       # uuid
    rep_id      = Column(String, ForeignKey("reps.id", ondelete="CASCADE"), index=True)  # FK to Rep.id (the uuid PK, NOT REP_0338)
    provider    = Column(String, nullable=False)                                         # password | whatsapp_otp | google
    identifier  = Column(String, nullable=False, index=True)                             # email / phone / google sub
    credential  = Column(String, nullable=True)                                          # bcrypt hash for password; NULL for others
    verified_at = Column(DateTime, nullable=True)                                        # when this identity was confirmed
    created_at  = Column(DateTime, default=datetime.utcnow)

    rep = relationship("Rep", back_populates="identities")