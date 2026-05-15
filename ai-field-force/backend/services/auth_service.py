# backend/services/auth_service.py
import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from models.db.rep import Rep
from models.schemas.auth import RegisterRequest
from core.auth.security import (
    hash_password,
    verify_password,
    normalize_phone,
    is_email,
)


class AuthService:
    def register(self, db: Session, data: RegisterRequest) -> Rep:
        email = data.email.lower().strip()
        phone = normalize_phone(data.phone)

        if not phone:
            raise HTTPException(status_code=400, detail="Invalid phone number")

        # uniqueness checks
        existing = (
            db.query(Rep)
            .filter(or_(Rep.email == email, Rep.phone == phone))
            .first()
        )
        if existing:
            if existing.email == email:
                raise HTTPException(status_code=409, detail="Email already registered")
            raise HTTPException(status_code=409, detail="Phone already registered")

        rep = Rep(
            id=str(uuid.uuid4()),
            rep_id=data.rep_id,
            name=data.name.strip(),
            email=email,
            phone=phone,
            hashed_password=hash_password(data.password),
            is_active=True,
        )
        db.add(rep)
        db.commit()
        db.refresh(rep)
        return rep

    def authenticate(self, db: Session, identifier: str, password: str) -> Rep:
        identifier = (identifier or "").strip()
        if not identifier:
            raise HTTPException(status_code=400, detail="Identifier required")

        if is_email(identifier):
            rep = db.query(Rep).filter(Rep.email == identifier.lower()).first()
        else:
            rep = db.query(Rep).filter(Rep.phone == normalize_phone(identifier)).first()

        if not rep or not verify_password(password, rep.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not rep.is_active:
            raise HTTPException(status_code=403, detail="Account disabled")
        return rep

    def ensure_seed_rep(
        self,
        db: Session,
        *,
        rep_id: str,
        name: str,
        email: str,
        phone: str,
        password: str,
    ) -> Optional[Rep]:
        """Idempotent: create the demo rep if missing. Returns the rep (new or existing)."""
        email = email.lower()
        phone = normalize_phone(phone)
        existing = (
            db.query(Rep)
            .filter(or_(Rep.email == email, Rep.phone == phone, Rep.rep_id == rep_id))
            .first()
        )
        if existing:
            return existing

        rep = Rep(
            id=str(uuid.uuid4()),
            rep_id=rep_id,
            name=name,
            email=email,
            phone=phone,
            hashed_password=hash_password(password),
            is_active=True,
        )
        db.add(rep)
        db.commit()
        db.refresh(rep)
        return rep