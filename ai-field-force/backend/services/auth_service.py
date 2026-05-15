# backend/services/auth_service.py
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
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
        db.flush()

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
            verified_at=None,
        ))
        db.commit()
        db.refresh(rep)
        return rep

    def login_with_password(self, db: Session, identifier: str, password: str) -> Rep:
        identifier = (identifier or "").strip()
        if not identifier:
            raise HTTPException(status_code=400, detail="Identifier required")

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

    # ---------- OTP-based login / auto-signup ----------

    def login_or_signup_with_phone(self, db: Session, phone: str) -> Rep:
        """Called AFTER the OTP code has already been verified. Finds an existing
        Rep linked to this phone, or auto-creates one. Marks the phone identity
        as verified. Returns the Rep ready for token issuance.
        """
        phone = normalize_phone(phone)
        if not phone:
            raise HTTPException(status_code=400, detail="Invalid phone number")

        ident = self._find_identity(db, "whatsapp_otp", phone)

        if ident:
            # Existing phone identity → log into the owning rep
            rep = db.query(Rep).filter(Rep.id == ident.rep_id).first()
            if not rep or not rep.is_active:
                raise HTTPException(status_code=403, detail="Account disabled")
            # Mark verified if it wasn't already
            if not ident.verified_at:
                ident.verified_at = datetime.utcnow()
                db.commit()
            return rep

        # Auto-create a new Rep with this phone as the sole identity
        rep = Rep(
            id=str(uuid.uuid4()),
            rep_id=None,                      # not linked to a Syngenta territory yet
            name=f"User {phone[-4:]}",        # placeholder; user can edit later
            primary_email=None,
            role="rep",
            is_active=True,
        )
        db.add(rep)
        db.flush()

        db.add(AuthIdentity(
            id=str(uuid.uuid4()),
            rep_id=rep.id,
            provider="whatsapp_otp",
            identifier=phone,
            credential=None,
            verified_at=datetime.utcnow(),
        ))
        db.commit()
        db.refresh(rep)
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
            verified_at=datetime.utcnow(),
        ))
        db.commit()
        db.refresh(rep)
        return rep