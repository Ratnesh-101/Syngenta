# backend/services/auth_service.py
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

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
            managed_rep_ids=[],
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

    # ---------- OTP login ----------

    def login_or_signup_with_phone(self, db: Session, phone: str) -> Rep:
        phone = normalize_phone(phone)
        if not phone:
            raise HTTPException(status_code=400, detail="Invalid phone number")

        ident = self._find_identity(db, "whatsapp_otp", phone)

        if ident:
            rep = db.query(Rep).filter(Rep.id == ident.rep_id).first()
            if not rep or not rep.is_active:
                raise HTTPException(status_code=403, detail="Account disabled")
            if not ident.verified_at:
                ident.verified_at = datetime.utcnow()
                db.commit()
            return rep

        rep = Rep(
            id=str(uuid.uuid4()),
            rep_id=None,
            name=f"User {phone[-4:]}",
            primary_email=None,
            role="rep",
            managed_rep_ids=[],
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

    # ---------- Google login ----------

    def login_or_signup_with_google(self, db: Session, info: Dict[str, Any]) -> Rep:
        google_sub = info["sub"]
        email      = info["email"].lower().strip()
        name       = info.get("name") or email.split("@")[0]

        ident = self._find_identity(db, "google", google_sub)
        if ident:
            rep = db.query(Rep).filter(Rep.id == ident.rep_id).first()
            if not rep or not rep.is_active:
                raise HTTPException(status_code=403, detail="Account disabled")
            return rep

        rep = self._find_rep_by_email(db, email)
        if rep:
            if not rep.is_active:
                raise HTTPException(status_code=403, detail="Account disabled")
            db.add(AuthIdentity(
                id=str(uuid.uuid4()),
                rep_id=rep.id,
                provider="google",
                identifier=google_sub,
                credential=None,
                verified_at=datetime.utcnow(),
            ))
            db.commit()
            db.refresh(rep)
            return rep

        rep = Rep(
            id=str(uuid.uuid4()),
            rep_id=None,
            name=name,
            primary_email=email,
            role="rep",
            managed_rep_ids=[],
            is_active=True,
        )
        db.add(rep)
        db.flush()

        db.add(AuthIdentity(
            id=str(uuid.uuid4()),
            rep_id=rep.id,
            provider="google",
            identifier=google_sub,
            credential=None,
            verified_at=datetime.utcnow(),
        ))
        db.commit()
        db.refresh(rep)
        return rep

    # ---------- linking ----------

    def link_google_to_current(self, db: Session, rep: Rep, info: Dict[str, Any]) -> Rep:
        google_sub = info["sub"]
        existing = self._find_identity(db, "google", google_sub)
        if existing:
            if existing.rep_id == rep.id:
                return rep
            raise HTTPException(
                status_code=409,
                detail="This Google account is already linked to a different user",
            )

        db.add(AuthIdentity(
            id=str(uuid.uuid4()),
            rep_id=rep.id,
            provider="google",
            identifier=google_sub,
            credential=None,
            verified_at=datetime.utcnow(),
        ))
        db.commit()
        db.refresh(rep)
        return rep

    def link_phone_to_current(self, db: Session, rep: Rep, phone: str) -> Rep:
        phone = normalize_phone(phone)
        existing = self._find_identity(db, "whatsapp_otp", phone)
        if existing:
            if existing.rep_id == rep.id:
                if not existing.verified_at:
                    existing.verified_at = datetime.utcnow()
                    db.commit()
                return rep
            raise HTTPException(
                status_code=409,
                detail="This phone number is already linked to a different user",
            )

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
        rep_id: Optional[str],
        name: str,
        email: str,
        phone: Optional[str],
        password: str,
        role: str = "rep",
        managed_rep_ids: Optional[List[str]] = None,
    ) -> Rep:
        email = email.lower()
        phone = normalize_phone(phone) if phone else None

        rep = self._find_rep_by_email(db, email)
        if rep:
            return rep

        rep = Rep(
            id=str(uuid.uuid4()),
            rep_id=rep_id,
            name=name,
            primary_email=email,
            role=role,
            managed_rep_ids=managed_rep_ids or [],
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
        if phone:
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