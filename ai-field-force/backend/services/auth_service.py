# backend/services/auth_service.py
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from models.db.rep import Rep
from models.db.auth_identity import AuthIdentity
from models.schemas.auth import PasswordRegisterRequest
from core.auth.security import (
    hash_password,
    verify_password,
    normalize_phone,
    is_email,
)


class AuthService:
    # ---------- helpers ----------

    def _find_identity(self, db: Session, provider: str, identifier: str) -> Optional[AuthIdentity]:
        return (
            db.query(AuthIdentity)
            .filter(AuthIdentity.provider == provider, AuthIdentity.identifier == identifier)
            .first()
        )

    def _find_rep_by_email(self, db: Session, email: str) -> Optional[Rep]:
        return db.query(Rep).filter(Rep.primary_email == email.lower()).first()

    # ---------- password register / login ----------

    def register_with_password(self, db: Session, data: PasswordRegisterRequest) -> Rep:
        email = data.email.lower().strip()
        phone = normalize_phone(data.phone)
        if not phone:
            raise HTTPException(status_code=400, detail="Invalid phone number")

        # Conflict checks across BOTH the rep table and existing identities.
        if self._find_rep_by_email(db, email):
            raise HTTPException(status_code=409, detail="Email already registered")
        if self._find_identity(db, "password", email):
            raise HTTPException(status_code=409, detail="Email already registered")
        if self._find_identity(db, "whatsapp_otp", phone):
            raise HTTPException(status_code=409, detail="Phone already registered")

        rep = Rep(
            id=str(uuid.uuid4()),
            rep_id=data.rep_id,
            name=data.name.strip(),
            primary_email=email,
            role="rep",
            is_active=True,
        )
        db.add(rep)
        db.flush()  # get rep.id without committing

        # Attach a password identity AND an unverified phone identity (so future OTP
        # login to that phone will resolve to this same account).
        db.add(AuthIdentity(
            id=str(uuid.uuid4()),
            rep_id=rep.id,
            provider="password",
            identifier=email,
            credential=hash_password(data.password),
            verified_at=None,
        ))
        db.add(AuthIdentity(
            id=str(uuid.uuid4()),
            rep_id=rep.id,
            provider="whatsapp_otp",
            identifier=phone,
            credential=None,
            verified_at=None,  # phone isn't verified until an OTP succeeds
        ))
        db.commit()
        db.refresh(rep)
        return rep

    def login_with_password(self, db: Session, identifier: str, password: str) -> Rep:
        identifier = (identifier or "").strip()
        if not identifier:
            raise HTTPException(status_code=400, detail="Identifier required")

        # Identifier can be email (→ password identity) or phone (→ phone identity → owning rep's password identity)
        if is_email(identifier):
            ident = self._find_identity(db, "password", identifier.lower())
        else:
            phone = normalize_phone(identifier)
            phone_ident = self._find_identity(db, "whatsapp_otp", phone)
            ident = None
            if phone_ident:
                ident = (
                    db.query(AuthIdentity)
                    .filter(
                        AuthIdentity.rep_id == phone_ident.rep_id,
                        AuthIdentity.provider == "password",
                    )
                    .first()
                )

        if not ident or not ident.credential or not verify_password(password, ident.credential):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        rep = db.query(Rep).filter(Rep.id == ident.rep_id).first()
        if not rep or not rep.is_active:
            raise HTTPException(status_code=403, detail="Account disabled")
        return rep

    # ---------- seeding ----------

    def ensure_seed_rep(
        self,
        db: Session,
        *,
        rep_id: str,
        name: str,
        email: str,
        phone: str,
        password: str,
        role: str = "rep",
    ) -> Rep:
        """Idempotent: create the demo rep + both identities if missing."""
        email = email.lower()
        phone = normalize_phone(phone)

        rep = self._find_rep_by_email(db, email)
        if rep:
            return rep

        rep = Rep(
            id=str(uuid.uuid4()),
            rep_id=rep_id,
            name=name,
            primary_email=email,
            role=role,
            is_active=True,
        )
        db.add(rep)
        db.flush()

        db.add(AuthIdentity(
            id=str(uuid.uuid4()),
            rep_id=rep.id,
            provider="password",
            identifier=email,
            credential=hash_password(password),
            verified_at=datetime.utcnow(),
        ))
        db.add(AuthIdentity(
            id=str(uuid.uuid4()),
            rep_id=rep.id,
            provider="whatsapp_otp",
            identifier=phone,
            credential=None,
            verified_at=datetime.utcnow(),  # pre-verified for the demo rep
        ))
        db.commit()
        db.refresh(rep)
        return rep